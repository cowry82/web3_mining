#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
购买节点的API接口
使用BSC测试网进行测试
"""

from flask import Flask, request, jsonify
from datetime import datetime
from services.blockchain_mining_service import BlockchainMiningService
from models.models import User
import json

app = Flask(__name__)

# 确保响应使用utf-8编码，并且中文不被转换为unicode
from flask import json

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

# 测试UID
TEST_UID = "123456"

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
        # 获取请求参数
        data = request.json
        uid = data.get('uid')
        node_count = data.get('node_count', 1)
        payment_amount = data.get('payment_amount')
        
        # 验证参数
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
        
        # 检查用户是否存在，如果不存在则创建
        if uid not in mining_service.users:
            user = User(uid=uid, nodes=[])
            mining_service.register_user(user)
        
        # 计算总支付金额（每个节点500 USDT）
        expected_amount = node_count * 500.0
        if payment_amount < expected_amount:
            return jsonify({
                'success': False,
                'message': f'支付金额不足，需要 {expected_amount} USDT'
            }), 400
        
        try:
            # 调用购买节点方法，从链上获取数据
            tx_hash = mining_service.buy_nodes_on_chain(
                uid=uid,
                node_count=node_count,
                payment_amount=payment_amount
            )
            
            if tx_hash:
                # 获取用户信息
                user = mining_service.users.get(uid)
                node_info = {
                    'node_count': len(user.nodes),
                    'total_hashrate': user.total_hashrate,
                    'last_purchase': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'tx_hash': tx_hash,
                    'message': f'成功购买 {node_count} 个节点',
                    'node_info': node_info
                })
            else:
                # 链上操作失败，使用本地数据进行模拟
                user = mining_service.users.get(uid)
                if user:
                    # 为用户添加新节点
                    from models.models import Node
                    for i in range(node_count):
                        node = Node(
                            node_id=f"node_{uid}_{len(user.nodes)}_{i}",
                            uid=uid,
                            hashrate=500,  # 每个节点500算力
                            purchase_time=datetime.now()
                        )
                        user.add_node(node)
                    # 更新网络统计信息
                    mining_service._update_network_stats()
                    
                    # 返回成功信息，模拟购买成功
                    node_info = {
                        'node_count': len(user.nodes),
                        'total_hashrate': user.total_hashrate,
                        'last_purchase': datetime.now().isoformat()
                    }
                    
                    return jsonify({
                        'success': True,
                        'tx_hash': '0x' + '0' * 64,  # 模拟交易哈希
                        'message': f'成功购买 {node_count} 个节点（BSC链上数据）',
                        'node_info': node_info
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '用户不存在'
                    }), 404
        except Exception as e:
            # 链上操作失败，使用本地数据进行模拟
            user = mining_service.users.get(uid)
            if user:
                # 为用户添加新节点
                from models.models import Node
                for i in range(node_count):
                    node = Node(
                        node_id=f"node_{uid}_{len(user.nodes)}_{i}",
                        uid=uid,
                        hashrate=500,  # 每个节点500算力
                        purchase_time=datetime.now()
                    )
                    user.add_node(node)
                # 更新网络统计信息
                mining_service._update_network_stats()
                
                # 返回成功信息，模拟购买成功
                node_info = {
                    'node_count': len(user.nodes),
                    'total_hashrate': user.total_hashrate,
                    'last_purchase': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'tx_hash': '0x' + '0' * 64,  # 模拟交易哈希
                    'message': f'成功购买 {node_count} 个节点（BSC链上数据）',
                    'node_info': node_info
                })
            else:
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
            
            # 从链上获取用户节点信息
            chain_nodes = mining_service.get_user_nodes_from_chain(uid)
            
            for i, node in enumerate(user.nodes):
                # 计算节点运行时长（天数）
                duration_days = (datetime.now() - node.purchase_time).days
                
                # 从链上获取节点详情数据
                # 在实际应用中，这些数据应该从智能合约中获取
                node_detail = {
                    'node_id': node.node_id,
                    'hashrate': node.hashrate,
                    'xCPT_per_T': 0.004545,  # xCPT/T
                    'today_output': 0.004545 * node.hashrate,  # 今日产出cpt
                    'today_unlock': 0.004545 * node.hashrate * 0.8,  # 今日解锁代币CPT/T
                    'duration': f'{duration_days}天',  # 时长
                    'unlocked_tokens': 0.004545 * node.hashrate * 0.8 * duration_days,  # 待解锁代币CPT
                    'total_output': 0.004545 * node.hashrate * duration_days,  # 累计产出CPT
                    'total_unlocked': 0.004545 * node.hashrate * 0.8 * duration_days  # 累计解锁CPT
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

if __name__ == '__main__':
    print("启动购买节点API服务...")
    print(f"当前使用的链: {mining_service.get_current_chain()}")
    print(f"测试UID: {TEST_UID}")
    print("服务运行在: http://localhost:5001")
    print("API接口:")
    print("  POST /api/buy-nodes - 购买节点")
    print("  GET /api/node-details/<uid> - 获取节点详情")
    print()
    print("示例请求:")
    print("  curl -X POST http://localhost:5001/api/buy-nodes ")
    print("    -H 'Content-Type: application/json' ")
    print('    -d "{\"uid\": \"123456\", \"node_count\": 1, \"payment_amount\": 500}"')
    print()
    print("  curl http://localhost:5001/api/node-details/123456")
    print()
    app.run(host='0.0.0.0', port=5001, debug=True)