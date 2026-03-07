from database import get_db
from config import config
from datetime import datetime, date, timedelta
import random

class MiningService:
    def __init__(self):
        pass
    
    def get_db_connection(self):
        """获取数据库连接"""
        return get_db()
    
    def get_user_power(self, user_id):
        """从fa_app_currency_user表获取用户算力"""
        conn = self.get_db_connection()
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
        
        conn.close()
        return result[0] if result else 0
    
    def update_user_power(self, user_id, power_increment):
        """更新用户算力到fa_app_currency_user表"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        now = int(datetime.now().timestamp())
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
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
            ''', (power_increment, now, result[0]))
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
                ''', (user_id, currency[0], power_increment, now, now))
        
        conn.commit()
        conn.close()
    
    def update_network_power(self):
        """更新全网算力"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # 计算全网算力
        cursor.execute('''
            SELECT SUM(cu.num) 
            FROM fa_app_currency_user cu
            JOIN fa_app_currency c ON cu.curr_id = c.id
            WHERE c.name = 'power'
        ''')
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        if is_mysql:
            total_power = cursor.fetchone()[0] or 0
        else:
            total_power = cursor.fetchone()[0] or 0
        
        # 更新全网算力
        cursor.execute('''
            INSERT INTO network_power (total_power, update_time)
            VALUES (?, ?)
            ON DUPLICATE KEY UPDATE total_power = ?, update_time = ?
        ''', (total_power, datetime.now(), total_power, datetime.now()))
        
        conn.commit()
        conn.close()
        return total_power
    
    def distribute_mining_rewards(self):
        """分发挖矿奖励"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # 检查是否是MySQL连接
        is_mysql = hasattr(conn, 'is_connected')
        
        # 获取全网算力
        cursor.execute('SELECT total_power FROM network_power ORDER BY update_time DESC LIMIT 1')
        
        if is_mysql:
            network_power = cursor.fetchone()
        else:
            network_power = cursor.fetchone()
        
        if not network_power or network_power[0] == 0:
            conn.close()
            return
        
        total_network_power = network_power[0]
        
        # 获取初始日产量
        initial_daily_output = config['halving']['initial_daily_output']
        halving_interval = config['halving']['halving_interval']
        
        # 计算当前减半周期
        start_date = date(2024, 1, 1)  # 假设从2024年1月1日开始
        current_date = date.today()
        days_passed = (current_date - start_date).days
        halving_cycles = days_passed // halving_interval
        
        # 计算当前日产量
        current_daily_output = initial_daily_output / (2 ** halving_cycles)
        
        # 计算每个用户的挖矿奖励
        cursor.execute('''
            SELECT cu.user_id, cu.num 
            FROM fa_app_currency_user cu
            JOIN fa_app_currency c ON cu.curr_id = c.id
            WHERE c.name = 'power' AND cu.num > 0
        ''')
        
        if is_mysql:
            users = cursor.fetchall()
        else:
            users = cursor.fetchall()
        
        mining_date = current_date
        
        for user in users:
            user_id = user[0]
            user_power = user[1]
            
            # 计算用户当日奖励
            reward = (user_power / total_network_power) * current_daily_output * config['reward']['mining_allocation']
            
            # 记录挖矿记录
            cursor.execute('''
                INSERT INTO mining_records 
                (user_id, amount, power, total_power, daily_output, mining_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, reward, user_power, total_network_power, current_daily_output, mining_date))
        
        conn.commit()
        conn.close()
    
    def process_daily_unlock(self):
        """处理每日解锁"""
        # 这里可以实现每日解锁逻辑
        # 例如：解锁用户的冻结资产，日释放1%
        pass

# 实例化服务
mining_service = MiningService()