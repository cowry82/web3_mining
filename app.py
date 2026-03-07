from flask import Flask, request, jsonify
from config import config
from mining_service import mining_service
from datetime import datetime, timedelta
from functools import wraps
import random
from database import get_db
from scheduler import scheduler

app = Flask(__name__)

# 从配置文件获取数据库配置
db_type = config['database']['type']

# 装饰器：验证token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        # 从token中提取user_id (简单实现，实际应该解析JWT)
        try:
            user_id = token.split('_')[-1]
            request.user_id = user_id
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# 1. 购买节点
@app.route('/api/purchase-node', methods=['POST'])
def purchase_node():
    try:
        data = request.json
        user_id = data.get('user_id')
        node_type = data.get('node_type')
        referrer_code = data.get('referrer_code')
        
        if not user_id or not node_type:
            return jsonify({'error': 'Missing user_id or node_type'}), 400
        
        # 检查节点类型是否有效
        if node_type not in config['nodes']:
            return jsonify({'error': 'Invalid node type'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        # 检查用户是否存在，不存在则创建
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        
        if is_mysql:
            existing_user = cursor.fetchone()
        else:
            existing_user = cursor.fetchone()
        
        if not existing_user:
            # 创建新用户
            referral_code = f'REF_{user_id}_{random.randint(1000, 9999)}'
            cursor.execute(
                'INSERT INTO users (user_id, tokens, power, referral_code) VALUES (?, 0, 0, ?)',
                (user_id, referral_code)
            )
        
        # 检查推荐人
        referrer_id = None
        level2_referrer_id = None
        
        if referrer_code:
            cursor.execute('SELECT user_id, referrer_id FROM users WHERE referral_code = ?', (referrer_code,))
            
            if is_mysql:
                referrer = cursor.fetchone()
            else:
                referrer = cursor.fetchone()
            
            if referrer:
                referrer_id = referrer[0]
                level2_referrer_id = referrer[1]
        
        # 检查用户购买次数是否超过限制
        cursor.execute('SELECT COUNT(*) FROM node_purchases WHERE user_id = ? AND node_type = ?', (user_id, node_type))
        
        if is_mysql:
            purchase_count = cursor.fetchone()[0]
        else:
            purchase_count = cursor.fetchone()[0]
        
        if purchase_count >= config['nodes'][node_type]['max_purchase']:
            conn.close()
            return jsonify({'error': f'Exceeded maximum purchase limit for {node_type} node'}), 400
        
        # 检查节点库存
        cursor.execute('SELECT remaining FROM nodes WHERE type = ?', (node_type,))
        
        if is_mysql:
            stock = cursor.fetchone()
        else:
            stock = cursor.fetchone()
        
        if not stock:
            # 初始化节点库存
            node_config = config['nodes'][node_type]
            cursor.execute(
                'INSERT INTO nodes (type, total_supply, remaining, price) VALUES (?, ?, ?, ?)',
                (node_type, node_config['total_supply'], node_config['total_supply'], node_config['price'])
            )
            remaining = node_config['total_supply'] - 1
        else:
            remaining = stock[0] - 1
            if remaining < 0:
                conn.close()
                return jsonify({'error': f'{node_type} node sold out'}), 400
        
        # 更新节点库存
        cursor.execute('UPDATE nodes SET remaining = ? WHERE type = ?', (remaining, node_type))
        
        # 记录购买
        node_config = config['nodes'][node_type]
        cursor.execute(
            'INSERT INTO node_purchases (user_id, node_type, price, referrer_id) VALUES (?, ?, ?, ?)',
            (user_id, node_type, node_config['price'], referrer_id)
        )
        
        # 处理邀请奖励
        if referrer_id:
            # 一级邀请奖励 - 更新算力到fa_app_currency_user表
            level1_reward = node_config['price'] * node_config['referral_level1']['usdt']
            cursor.execute(
                'UPDATE users SET tokens = tokens + ? WHERE user_id = ?',
                (level1_reward, referrer_id)
            )
            # 更新算力
            # 直接在当前连接中更新算力，避免创建新连接
            now = int(datetime.now().timestamp())
            # 检查是否已有power币种记录
            cursor.execute('''
                SELECT cu.id, cu.num 
                FROM fa_app_currency_user cu
                JOIN fa_app_currency c ON cu.curr_id = c.id
                WHERE cu.user_id = ? AND c.name = 'power'
            ''', (referrer_id,))
            
            if is_mysql:
                result = cursor.fetchone()
            else:
                result = cursor.fetchone()
            
            if result:
                # 更新现有记录
                cursor.execute('''
                    UPDATE fa_app_currency_user 
                    SET num = num + ?, updatetime = ?
                    WHERE id = ?
                ''', (node_config['referral_level1']['power'], now, result[0]))
            else:
                # 获取power币种的id
                cursor.execute('SELECT id FROM fa_app_currency WHERE name = ?', ('power',))
                
                if is_mysql:
                    currency = cursor.fetchone()
                else:
                    currency = cursor.fetchone()
                
                if currency:
                    # 创建新记录
                    cursor.execute('''
                        INSERT INTO fa_app_currency_user 
                        (user_id, curr_id, num, updatetime, regtime)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (referrer_id, currency[0], node_config['referral_level1']['power'], now, now))
            
            # 二级邀请奖励
            if level2_referrer_id:
                level2_reward = node_config['price'] * node_config['referral_level2']['usdt']
                cursor.execute(
                    'UPDATE users SET tokens = tokens + ? WHERE user_id = ?',
                    (level2_reward, level2_referrer_id)
                )
                # 更新算力
                # 直接在当前连接中更新算力，避免创建新连接
                # 检查是否已有power币种记录
                cursor.execute('''
                    SELECT cu.id, cu.num 
                    FROM fa_app_currency_user cu
                    JOIN fa_app_currency c ON cu.curr_id = c.id
                    WHERE cu.user_id = ? AND c.name = 'power'
                ''', (level2_referrer_id,))
                
                if is_mysql:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchone()
                
                if result:
                    # 更新现有记录
                    cursor.execute('''
                        UPDATE fa_app_currency_user 
                        SET num = num + ?, updatetime = ?
                        WHERE id = ?
                    ''', (node_config['referral_level2']['power'], now, result[0]))
                else:
                    # 获取power币种的id
                    cursor.execute('SELECT id FROM fa_app_currency WHERE name = ?', ('power',))
                    
                    if is_mysql:
                        currency = cursor.fetchone()
                    else:
                        currency = cursor.fetchone()
                    
                    if currency:
                        # 创建新记录
                        cursor.execute('''
                            INSERT INTO fa_app_currency_user 
                            (user_id, curr_id, num, updatetime, regtime)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (level2_referrer_id, currency[0], node_config['referral_level2']['power'], now, now))
        
        # 更新用户算力
        # 直接在当前连接中更新算力，避免创建新连接
        now = int(datetime.now().timestamp())
        # 检查是否已有power币种记录
        cursor.execute('''
            SELECT cu.id, cu.num 
            FROM fa_app_currency_user cu
            JOIN fa_app_currency c ON cu.curr_id = c.id
            WHERE cu.user_id = ? AND c.name = 'power'
        ''', (user_id,))
        
        if is_mysql:
            result = cursor.fetchone()
        else:
            result = cursor.fetchone()
        
        if result:
            # 更新现有记录
            cursor.execute('''
                UPDATE fa_app_currency_user 
                SET num = num + ?, updatetime = ?
                WHERE id = ?
            ''', (node_config['referral_level1']['power'], now, result[0]))
        else:
            # 获取power币种的id
            cursor.execute('SELECT id FROM fa_app_currency WHERE name = ?', ('power',))
            
            if is_mysql:
                currency = cursor.fetchone()
            else:
                currency = cursor.fetchone()
            
            if currency:
                # 创建新记录
                cursor.execute('''
                    INSERT INTO fa_app_currency_user 
                    (user_id, curr_id, num, updatetime, regtime)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, currency[0], node_config['referral_level1']['power'], now, now))
        
        # 更新全网算力
        # 直接在当前连接中更新全网算力，避免创建新连接
        cursor.execute('''
            SELECT SUM(cu.num) 
            FROM fa_app_currency_user cu
            JOIN fa_app_currency c ON cu.curr_id = c.id
            WHERE c.name = 'power'
        ''')
        
        if is_mysql:
            total_power = cursor.fetchone()[0] or 0
        else:
            total_power = cursor.fetchone()[0] or 0
        
        # 更新全网算力，根据数据库类型使用不同的语法
        if is_mysql:
            # MySQL使用ON DUPLICATE KEY UPDATE
            cursor.execute('''
                INSERT INTO network_power (total_power, update_time)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE total_power = ?, update_time = ?
            ''', (total_power, datetime.now(), total_power, datetime.now()))
        else:
            # SQLite使用UPSERT语法
            cursor.execute('''
                INSERT OR REPLACE INTO network_power (id, total_power, update_time)
                VALUES (1, ?, ?)
            ''', (total_power, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'node_type': node_type,
            'price': node_config['price'],
            'referrer_id': referrer_id
        })
    except Exception as e:
        print(f'Purchase node error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 2. 获取节点详情
@app.route('/api/node-details/<node_type>', methods=['GET'])
def get_node_details(node_type):
    try:
        if node_type not in config['nodes']:
            return jsonify({'error': 'Invalid node type'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        # 获取节点库存
        cursor.execute('SELECT remaining FROM nodes WHERE type = ?', (node_type,))
        
        if is_mysql:
            stock = cursor.fetchone()
        else:
            stock = cursor.fetchone()
        
        remaining = stock[0] if stock else config['nodes'][node_type]['total_supply']
        
        node_config = config['nodes'][node_type]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'node_type': node_type,
            'price': node_config['price'],
            'max_purchase': node_config['max_purchase'],
            'total_supply': node_config['total_supply'],
            'remaining': remaining,
            'referral_level1': node_config['referral_level1'],
            'referral_level2': node_config['referral_level2']
        })
    except Exception as e:
        print(f'Get node details error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 3. 获取购买记录
@app.route('/api/purchase-records', methods=['GET'])
@token_required
def get_purchase_records():
    try:
        user_id = request.user_id
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        cursor.execute('SELECT * FROM node_purchases WHERE user_id = ? ORDER BY purchase_time DESC', (user_id,))
        
        if is_mysql:
            records = cursor.fetchall()
        else:
            records = cursor.fetchall()
        
        record_list = []
        for record in records:
            record_list.append({
                'id': record[0],
                'node_type': record[2],
                'price': record[3],
                'purchase_time': record[4],
                'referrer_id': record[5],
                'status': record[6]
            })
        
        conn.close()
        return jsonify({'success': True, 'records': record_list})
    except Exception as e:
        print(f'Get purchase records error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 4. 获取节点价格
@app.route('/api/node-prices', methods=['GET'])
def get_node_prices():
    try:
        prices = {}
        for node_type, node_config in config['nodes'].items():
            prices[node_type] = node_config['price']
        return jsonify({'success': True, 'prices': prices})
    except Exception as e:
        print(f'Get node prices error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 5. 获取解锁记录
@app.route('/api/unlock-records', methods=['GET'])
@token_required
def get_unlock_records():
    try:
        user_id = request.user_id
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        cursor.execute('SELECT * FROM unlock_records WHERE user_id = ? ORDER BY unlock_time DESC', (user_id,))
        
        if is_mysql:
            records = cursor.fetchall()
        else:
            records = cursor.fetchall()
        
        record_list = []
        for record in records:
            record_list.append({
                'id': record[0],
                'amount': record[2],
                'unlock_time': record[3],
                'status': record[4]
            })
        
        conn.close()
        return jsonify({'success': True, 'records': record_list})
    except Exception as e:
        print(f'Get unlock records error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 6. 获取挖矿记录
@app.route('/api/mining-records', methods=['GET'])
@token_required
def get_mining_records():
    try:
        user_id = request.user_id
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        cursor.execute('SELECT * FROM mining_records WHERE user_id = ? ORDER BY mining_date DESC', (user_id,))
        
        if is_mysql:
            records = cursor.fetchall()
        else:
            records = cursor.fetchall()
        
        record_list = []
        for record in records:
            record_list.append({
                'id': record[0],
                'amount': record[2],
                'power': record[3],
                'total_power': record[4],
                'daily_output': record[5],
                'mining_date': record[6],
                'created_at': record[7]
            })
        
        conn.close()
        return jsonify({'success': True, 'records': record_list})
    except Exception as e:
        print(f'Get mining records error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 7. 获取用户算力
@app.route('/api/user-power', methods=['GET'])
@token_required
def get_user_power():
    try:
        user_id = request.user_id
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        # 查询power币种的num字段
        cursor.execute('''
            SELECT cu.num 
            FROM fa_app_currency_user cu
            JOIN fa_app_currency c ON cu.curr_id = c.id
            WHERE cu.user_id = ? AND c.name = 'power'
        ''', (user_id,))
        
        if is_mysql:
            result = cursor.fetchone()
        else:
            result = cursor.fetchone()
        
        power = result[0] if result else 0
        conn.close()
        
        return jsonify({'success': True, 'user_id': user_id, 'power': power})
    except Exception as e:
        print(f'Get user power error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 8. 手动触发挖矿（用于测试）
@app.route('/api/trigger-mining', methods=['POST'])
@token_required
def trigger_mining():
    try:
        mining_service.distribute_mining_rewards()
        mining_service.process_daily_unlock()
        return jsonify({'success': True, 'message': 'Mining rewards distributed successfully'})
    except Exception as e:
        print(f'Trigger mining error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 9. 启动定时任务
@app.route('/api/scheduler/start', methods=['POST'])
@token_required
def start_scheduler():
    try:
        scheduler.start()
        return jsonify({'success': True, 'message': 'Scheduler started successfully'})
    except Exception as e:
        print(f'Start scheduler error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

# 10. 停止定时任务
@app.route('/api/scheduler/stop', methods=['POST'])
@token_required
def stop_scheduler():
    try:
        scheduler.stop()
        return jsonify({'success': True, 'message': 'Scheduler stopped successfully'})
    except Exception as e:
        print(f'Stop scheduler error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(port=config['server']['port'], debug=True)