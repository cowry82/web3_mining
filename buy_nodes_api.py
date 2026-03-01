#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购买节点的API接口
使用BSC测试网进行测试
"""

from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from services.blockchain_mining_service import BlockchainMiningService
from models.models import User
import json

app = Flask(__name__)

# 覆盖Flask的jsonify函数，确保中文不被转换为unicode
def jsonify(*args, **kwargs):
    response = app.response_class(
        response=json.dumps(dict(*args, **kwargs), ensure_ascii=False, indent=2),
        mimetype='application/json; charset=utf-8'
    )
    return response

# 确保响应使用utf-8编码
@app.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# 初始化区块链挖矿服务
mining_service = BlockchainMiningService(datetime(2024, 1, 1))

# 存储购买记录
purchase_records = {}
unlock_records = {}

# 存储用户倒计时信息 {uid: {'start_time': datetime, 'last_claim_time': datetime}}
countdown_records = {}

@app.route('/api/buy-nodes', methods=['POST'])
def buy_nodes():
    """
    购买节点接口
    
    请求参数：
    - uid: 用户ID
    - node_count: 节点数量
    - payment_amount: 支付金额（USDT）
    
    返回结果：
    - success: 是否成功
    - tx_hash: 交易哈希（如果成功）
    - message: 提示信息
    - node_info: 节点信息
    """
    try:
        data = request.json
        uid = data.get('uid')
        node_count = data.get('node_count', 1)
        payment_amount = data.get('payment_amount')
        
        if not uid:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400
        
        if not payment_amount:
            return jsonify({
                'success': False,
                'message': '支付金额不能为空'
            }), 400
        
        if node_count <= 0:
            return jsonify({
                'success': False,
                'message': '节点数量必须大于0'
            }), 400
        
        if uid not in mining_service.users:
            user = User(uid=uid, nodes=[])
            mining_service.register_user(user)
        
        expected_amount = node_count * 500.0
        if payment_amount < expected_amount:
            return jsonify({
                'success': False,
                'message': f'支付金额不足，需要 {expected_amount} USDT'
            }), 400
        
        try:
            tx_hash = mining_service.buy_nodes_on_chain(
                uid=uid,
                node_count=node_count,
                payment_amount=payment_amount
            )
            
            if tx_hash:
                user = mining_service.users.get(uid)
                node_info = {
                    'node_count': len(user.nodes),
                    'total_hashrate': user.total_hashrate,
                    'last_purchase': datetime.now().isoformat()
                }
                
                purchase_record = {
                    'record_id': f"purchase_{uid}_{int(datetime.now().timestamp())}",
                    'uid': uid,
                    'node_count': node_count,
                    'payment_amount': payment_amount,
                    'price_per_node': 500.0,
                    'total_price': node_count * 500.0,
                    'tx_hash': tx_hash,
                    'purchase_time': datetime.now().isoformat(),
                    'status': 'completed'
                }
                
                if uid not in purchase_records:
                    purchase_records[uid] = []
                purchase_records[uid].append(purchase_record)
                
                # 初始化用户倒计时（如果是首次购买）
                if uid not in countdown_records:
                    countdown_records[uid] = {
                        'start_time': datetime.now(),
                        'last_claim_time': None,
                        'next_claim_time': datetime.now() + timedelta(hours=24)
                    }
                
                return jsonify({
                    'success': True,
                    'tx_hash': tx_hash,
                    'message': f'成功购买 {node_count} 个节点',
                    'node_info': node_info,
                    'purchase_record': purchase_record
                })
            else:
                # 链上购买失败，创建本地节点用于测试
                user = mining_service.users.get(uid)
                if user:
                    from models.models import Node
                    for i in range(node_count):
                        node = Node(
                            node_id=f"node_{uid}_{len(user.nodes)}_{i}",
                            uid=uid,
                            hashrate=500,
                            purchase_time=datetime.now()
                        )
                        user.add_node(node)
                    mining_service._update_network_stats()
                    
                    node_info = {
                        'node_count': len(user.nodes),
                        'total_hashrate': user.total_hashrate,
                        'last_purchase': datetime.now().isoformat()
                    }
                    
                    purchase_record = {
                        'record_id': f"purchase_{uid}_{int(datetime.now().timestamp())}",
                        'uid': uid,
                        'node_count': node_count,
                        'payment_amount': payment_amount,
                        'price_per_node': 500.0,
                        'total_price': node_count * 500.0,
                        'tx_hash': '0x' + '0' * 64,
                        'purchase_time': datetime.now().isoformat(),
                        'status': 'completed'
                    }
                    
                    if uid not in purchase_records:
                        purchase_records[uid] = []
                    purchase_records[uid].append(purchase_record)
                    
                    # 初始化用户倒计时
                    if uid not in countdown_records:
                        countdown_records[uid] = {
                            'start_time': datetime.now(),
                            'last_claim_time': None,
                            'next_claim_time': datetime.now() + timedelta(hours=24)
                        }
                    
                    return jsonify({
                        'success': True,
                        'tx_hash': '0x' + '0' * 64,
                        'message': f'成功购买 {node_count} 个节点（本地模式）',
                        'node_info': node_info,
                        'purchase_record': purchase_record
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '购买节点失败'
                    }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'购买节点失败: {str(e)}'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@app.route('/api/node-details/<uid>', methods=['GET'])
def get_node_details(uid):
    """
    获取节点详情接口
    
    请求参数：
    - uid: 用户ID
    
    返回结果：
    - success: 是否成功
    - node_details: 节点详情列表
    """
    try:
        user = mining_service.users.get(uid)
        if user:
            node_details = []
            
            for node in user.nodes:
                duration_days = (datetime.now() - node.purchase_time).days
                
                node_detail = {
                    'node_id': node.node_id,
                    'hashrate': node.hashrate,
                    'xCPT_per_T': 0.004545,
                    'today_output': 0.004545 * node.hashrate,
                    'today_unlock': 0.004545 * node.hashrate * 0.8,
                    'duration': f'{duration_days}天',
                    'unlocked_tokens': 0.004545 * node.hashrate * 0.8 * duration_days,
                    'total_output': 0.004545 * node.hashrate * duration_days,
                    'total_unlocked': 0.004545 * node.hashrate * 0.8 * duration_days
                }
                node_details.append(node_detail)
            
            return jsonify({
                'success': True,
                'node_details': node_details
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@app.route('/api/purchase-records/<uid>', methods=['GET'])
def get_purchase_records(uid):
    """
    获取节点购买记录接口
    
    请求参数：
    - uid: 用户ID
    
    返回结果：
    - success: 是否成功
    - purchase_records: 购买记录列表
    - total_count: 总记录数
    - total_amount: 总支付金额
    """
    try:
        user = mining_service.users.get(uid)
        if user:
            records = purchase_records.get(uid, [])
            
            total_count = len(records)
            total_amount = sum(record['payment_amount'] for record in records)
            total_nodes = sum(record['node_count'] for record in records)
            
            return jsonify({
                'success': True,
                'uid': uid,
                'purchase_records': records,
                'total_count': total_count,
                'total_amount': total_amount,
                'total_nodes': total_nodes
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@app.route('/api/node-price', methods=['GET'])
def get_node_price():
    """
    获取节点价格接口
    
    返回结果：
    - success: 是否成功
    - price_per_node: 单个节点价格
    - currency: 货币单位
    - discount_info: 折扣信息（如果有）
    """
    try:
        price_config = {
            'price_per_node': 500.0,
            'currency': 'USDT',
            'min_purchase': 1,
            'max_purchase': 200,
            'discount_info': {
                'bulk_discount': {
                    'min_nodes': 10,
                    'discount_rate': 0.05
                }
            }
        }
        
        return jsonify({
            'success': True,
            'price_config': price_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@app.route('/api/unlock-records/<uid>', methods=['GET'])
def get_unlock_records(uid):
    """
    获取解锁记录接口
    
    请求参数：
    - uid: 用户ID
    
    返回结果：
    - success: 是否成功
    - unlock_records: 解锁记录列表
    - total_unlocked: 总解锁金额
    - pending_unlock: 待解锁金额
    """
    try:
        user = mining_service.users.get(uid)
        if user:
            records = unlock_records.get(uid, [])
            
            if not records:
                for node in user.nodes:
                    duration_days = (datetime.now() - node.purchase_time).days
                    
                    for day in range(min(duration_days + 1, 10)):
                        unlock_record = {
                            'record_id': f"unlock_{uid}_{node.node_id}_{day}",
                            'uid': uid,
                            'node_id': node.node_id,
                            'unlock_date': (datetime.now() - timedelta(days=duration_days - day)).isoformat(),
                            'unlock_amount': 0.004545 * node.hashrate * 0.8,
                            'unlock_type': 'daily_linear',
                            'status': 'completed' if day < duration_days else 'pending'
                        }
                        records.append(unlock_record)
                
                unlock_records[uid] = records
            
            total_unlocked = sum(record['unlock_amount'] for record in records if record['status'] == 'completed')
            pending_unlock = sum(record['unlock_amount'] for record in records if record['status'] == 'pending')
            
            return jsonify({
                'success': True,
                'uid': uid,
                'unlock_records': records,
                'total_unlocked': total_unlocked,
                'pending_unlock': pending_unlock,
                'total_records': len(records)
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@app.route('/api/countdown/<uid>', methods=['GET'])
def get_countdown(uid):
    """
    获取24小时倒计时接口
    
    请求参数：
    - uid: 用户ID（URL路径参数）
    
    返回结果：
    - success: 是否成功
    - countdown: 倒计时信息
        - total_seconds: 剩余总秒数
        - hours: 剩余小时数
        - minutes: 剩余分钟数
        - seconds: 剩余秒数
        - formatted: 格式化的时间字符串 (HH:MM:SS)
    - next_claim_time: 下次可领取时间
    - last_claim_time: 上次领取时间
    - can_claim: 是否可以领取
    - daily_reward: 今日可领取奖励
    """
    try:
        user = mining_service.users.get(uid)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        # 如果用户没有倒计时记录，初始化一个
        if uid not in countdown_records:
            countdown_records[uid] = {
                'start_time': datetime.now(),
                'last_claim_time': None,
                'next_claim_time': datetime.now() + timedelta(hours=24)
            }
        
        record = countdown_records[uid]
        now = datetime.now()
        next_claim_time = record['next_claim_time']
        
        # 计算剩余时间
        if now >= next_claim_time:
            # 倒计时已结束，可以领取
            remaining_seconds = 0
            can_claim = True
            # 更新下次领取时间（24小时后）
            countdown_records[uid]['next_claim_time'] = now + timedelta(hours=24)
        else:
            remaining_seconds = int((next_claim_time - now).total_seconds())
            can_claim = False
        
        # 格式化倒计时
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60
        
        # 计算今日奖励（所有节点的今日产出总和）
        daily_reward = sum(0.004545 * node.hashrate for node in user.nodes)
        
        return jsonify({
            'success': True,
            'uid': uid,
            'countdown': {
                'total_seconds': remaining_seconds,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
                'formatted': f'{hours:02d}:{minutes:02d}:{seconds:02d}'
            },
            'next_claim_time': next_claim_time.isoformat(),
            'last_claim_time': record['last_claim_time'].isoformat() if record['last_claim_time'] else None,
            'can_claim': can_claim,
            'daily_reward': daily_reward,
            'node_count': len(user.nodes)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500


@app.route('/api/claim-reward', methods=['POST'])
def claim_reward():
    """
    领取每日奖励接口
    
    请求参数：
    - uid: 用户ID
    
    返回结果：
    - success: 是否成功
    - claimed_amount: 领取金额
    - tx_hash: 交易哈希
    """
    try:
        data = request.json
        uid = data.get('uid')
        
        if not uid:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400
        
        user = mining_service.users.get(uid)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        if uid not in countdown_records:
            return jsonify({
                'success': False,
                'message': '没有可领取的奖励'
            }), 400
        
        record = countdown_records[uid]
        now = datetime.now()
        
        # 检查是否可以领取
        if now < record['next_claim_time']:
            remaining_seconds = int((record['next_claim_time'] - now).total_seconds())
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60
            return jsonify({
                'success': False,
                'message': f'还需等待 {hours:02d}:{minutes:02d}:{seconds:02d} 才能领取',
                'next_claim_time': record['next_claim_time'].isoformat()
            }), 400
        
        # 计算奖励金额
        claimed_amount = sum(0.004545 * node.hashrate for node in user.nodes)
        
        # 更新领取记录
        countdown_records[uid]['last_claim_time'] = now
        countdown_records[uid]['next_claim_time'] = now + timedelta(hours=24)
        
        # 生成交易哈希（实际应用中应该从链上获取）
        import hashlib
        tx_data = f"{uid}_{now.timestamp()}_{claimed_amount}"
        tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:64]
        
        return jsonify({
            'success': True,
            'message': f'成功领取 {claimed_amount:.4f} CPT',
            'claimed_amount': claimed_amount,
            'tx_hash': tx_hash,
            'claim_time': now.isoformat(),
            'next_claim_time': countdown_records[uid]['next_claim_time'].isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)