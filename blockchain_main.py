from datetime import datetime
from models.models import User, Node
from services.blockchain_mining_service import BlockchainMiningService
from services.mining_service import RewardService, ReleaseService
from core.calculator import HalvingCalculator
from utils.time_utils import TimeUtils
from config.mining_config import BLOCKCHAIN_CONFIG


def create_sample_nodes(uid: str, count: int) -> list[Node]:
    # 创建示例节点，用于演示
    nodes = []
    for i in range(count):
        node = Node(
            node_id=f"node_{uid}_{i}",
            uid=uid,
            hashrate=500,
            purchase_time=datetime.now()
        )
        nodes.append(node)
    return nodes


def main():
    # 主函数，演示区块链挖矿系统的功能
    # 设置挖矿开始日期
    mining_start_date = datetime(2024, 1, 1)
    current_date = datetime.now()
    
    # 初始化服务
    mining_service = BlockchainMiningService(mining_start_date)
    reward_service = RewardService()
    release_service = ReleaseService()
    
    # 创建示例用户
    user1 = User(
        uid="user_001",
        nodes=create_sample_nodes("user_001", 10)
    )
    
    user2 = User(
        uid="user_002",
        nodes=create_sample_nodes("user_002", 5),
        referrer_uid="user_001"
    )
    
    # 注册用户到挖矿系统
    mining_service.register_user(user1)
    mining_service.register_user(user2)
    
    print("=" * 60)
    print("BitUP 区块链挖矿系统演示")
    print("=" * 60)
    print()
    
    print("-" * 60)
    print("支持的区块链网络")
    print("-" * 60)
    # 显示所有支持的区块链网络
    for chain_key, config in BLOCKCHAIN_CONFIG.items():
        print(f"{chain_key}: {config['NAME']} ({config['SYMBOL']})")
        print(f"  Chain ID: {config['CHAIN_ID']}")
        print(f"  浏览器: {config['EXPLORER_URL']}")
        print()
    
    print("-" * 60)
    print(f"当前区块链: {mining_service.get_current_chain()}")
    print("-" * 60)
    
    # 获取并显示钱包余额
    wallet_balance = mining_service.get_wallet_balance()
    print(f"钱包余额: {wallet_balance:.4f}")
    print()
    
    print("-" * 60)
    print("链上网络状态")
    print("-" * 60)
    # 从链上获取网络状态
    network_stats = mining_service.get_network_stats_from_chain()
    print(f"全网节点数: {network_stats['total_nodes']}")
    print(f"全网总算力: {network_stats['total_hashrate']} T")
    print(f"当前日产量: {network_stats['daily_output']} BUB")
    print()
    
    print("-" * 60)
    print("本地用户信息")
    print("-" * 60)
    # 显示用户1的信息
    print(f"用户1 ({user1.uid}):")
    print(f"  节点数: {user1.active_node_count}")
    print(f"  总算力: {user1.total_hashrate} T")
    print()
    # 显示用户2的信息
    print(f"用户2 ({user2.uid}):")
    print(f"  节点数: {user2.active_node_count}")
    print(f"  总算力: {user2.total_hashrate} T")
    print(f"  推荐人: {user2.referrer_uid}")
    print()
    
    print("-" * 60)
    print("链上购买节点演示")
    print("-" * 60)
    print("尝试为用户1购买 2 个节点...")
    # 在区块链上购买节点
    tx_hash = mining_service.buy_nodes_on_chain(
        uid="user_001",
        node_count=2,
        payment_amount=0.1
    )
    if tx_hash:
        print(f"✓ 购买成功，交易哈希: {tx_hash}")
    else:
        print("✗ 购买失败（演示模式或网络连接问题）")
    print()
    
    print("-" * 60)
    print("从链上获取用户节点")
    print("-" * 60)
    # 从链上获取用户节点信息
    chain_nodes = mining_service.get_user_nodes_from_chain("user_001")
    print(f"链上节点数量: {len(chain_nodes)}")
    if chain_nodes:
        for node in chain_nodes:
            print(f"  节点ID: {node['node_id']}, 算力: {node['hashrate']} T")
    print()
    
    print("-" * 60)
    print("从链上获取用户奖励")
    print("-" * 60)
    # 从链上获取用户待领取奖励
    chain_rewards = mining_service.get_user_rewards_from_chain("user_001")
    print(f"链上待领取奖励: {chain_rewards:.2f} BUB")
    print()
    
    print("-" * 60)
    print("链上领取奖励演示")
    print("-" * 60)
    print("尝试领取用户1的奖励...")
    # 在区块链上领取奖励
    claim_tx_hash = mining_service.claim_rewards_on_chain("user_001")
    if claim_tx_hash:
        print(f"✓ 领取成功，交易哈希: {claim_tx_hash}")
    else:
        print("✗ 领取失败（演示模式或网络连接问题）")
    print()
    
    print("-" * 60)
    print("每日挖矿收益计算（本地）")
    print("-" * 60)
    # 计算并分发每日挖矿奖励
    records = mining_service.distribute_daily_rewards(current_date)
    
    # 显示每个用户的挖矿收益
    for record in records:
        print(f"用户 {record.uid}:")
        print(f"  总产出: {record.total_output:.2f} BUB")
        print(f"  立即释放: {record.immediate_release:.2f} BUB (80%)")
        print(f"  线性释放: {record.linear_release:.2f} BUB (20%)")
        print(f"  算力占比: {record.hashrate / record.network_hashrate * 100:.4f}%")
        print()
    
    print("-" * 60)
    print("邀请奖励计算")
    print("-" * 60)
    # 计算邀请奖励
    referred_node_hashrate = 500
    reward = reward_service.process_referral(
        referrer=user1,
        referred_user=user2,
        referred_node_hashrate=referred_node_hashrate,
        reward_time=current_date
    )
    
    # 显示邀请奖励详情
    print(f"推荐人: {reward.referrer_uid}")
    print(f"被推荐人: {reward.referred_uid}")
    print(f"被推荐节点算力: {reward.referred_node_hashrate} T")
    print(f"奖励比例: {reward.reward_ratio * 100:.1f}%")
    print(f"算力奖励: {reward.hashrate_reward} T")
    print(f"代币奖励: {reward.referred_node_hashrate * reward.reward_ratio:.2f} BUB")
    print()
    
    print("-" * 60)
    print("线性释放演示")
    print("-" * 60)
    # 添加待释放的线性奖励
    for record in records:
        release_service.add_pending_release(record.uid, record.linear_release)
        print(f"用户 {record.uid} 待释放总额: {record.linear_release:.2f} BUB")
    
    print()
    print("每日释放进度 (模拟10天):")
    # 模拟10天的线性释放过程
    for day in range(1, 11):
        print(f"\n第 {day} 天:")
        for record in records:
            # 处理每日释放
            daily_release = release_service.process_daily_release(record.uid)
            print(f"  用户 {record.uid}: 释放 {daily_release:.2f} BUB")
    
    print()
    print("-" * 60)
    print("减产机制演示")
    print("-" * 60)
    print("未来5年日产量预测:")
    # 预测未来5年的日产量（考虑减产）
    for year in range(5):
        future_date = datetime(mining_start_date.year + year, 1, 1)
        daily_output = HalvingCalculator.calculate_current_daily_output(
            mining_start_date, future_date
        )
        print(f"  {future_date.year}年: {daily_output:.2f} BUB/天")
    
    print()
    print("-" * 60)
    print("交易历史")
    print("-" * 60)
    # 获取交易历史记录
    transactions = mining_service.get_transaction_history(limit=10)
    if transactions:
        for tx in transactions:
            print(f"交易哈希: {tx.tx_hash}")
            print(f"  区块链: {tx.chain_key}")
            print(f"  状态: {tx.status.value}")
            print(f"  金额: {tx.amount:.4f}")
            print(f"  时间: {TimeUtils.format_datetime(tx.timestamp)}")
            print()
    else:
        print("暂无交易记录")
    
    print()
    print("-" * 60)
    print("交易统计")
    print("-" * 60)
    # 获取交易统计信息
    stats = mining_service.get_transaction_statistics()
    print(f"总交易数: {stats['total_transactions']}")
    print(f"待确认: {stats['pending_count']}")
    print(f"已确认: {stats['confirmed_count']}")
    print(f"失败: {stats['failed_count']}")
    print(f"成功率: {stats['success_rate']:.2f}%")
    print()
    
    print("-" * 60)
    print("切换区块链演示")
    print("-" * 60)
    # 演示切换到以太坊
    print("尝试切换到 ETH...")
    if mining_service.switch_chain('ETH'):
        print(f"✓ 切换成功，当前区块链: {mining_service.get_current_chain()}")
        eth_balance = mining_service.get_wallet_balance()
        print(f"ETH钱包余额: {eth_balance:.4f}")
    else:
        print("✗ 切换失败")
    
    print()
    # 演示切换到Polygon
    print("尝试切换到 POLYGON...")
    if mining_service.switch_chain('POLYGON'):
        print(f"✓ 切换成功，当前区块链: {mining_service.get_current_chain()}")
        polygon_balance = mining_service.get_wallet_balance()
        print(f"POLYGON钱包余额: {polygon_balance:.4f}")
    else:
        print("✗ 切换失败")
    
    print()
    # 演示切换回BSC
    print("尝试切换回 BSC...")
    if mining_service.switch_chain('BSC'):
        print(f"✓ 切换成功，当前区块链: {mining_service.get_current_chain()}")
        bsc_balance = mining_service.get_wallet_balance()
        print(f"BSC钱包余额: {bsc_balance:.4f}")
    else:
        print("✗ 切换失败")
    
    print()
    print("=" * 60)
    print("演示完成")
    print("=" * 60)
    print()
    print("提示:")
    print("1. 要使用真实的区块链功能，请编辑 .env 文件:")
    print("   - PRIVATE_KEY: 设置您的EVM链私钥（十六进制）")
    print("   - SOLANA_PRIVATE_KEY: 设置您的Solana私钥（Base58编码）")
    print("   - WALLET_ADDRESS: 设置您的EVM钱包地址")
    print("   - SOLANA_ADDRESS: 设置您的Solana钱包地址")
    print("   - DEMO_MODE: 设置为 false 以启用生产模式")
    print()
    print("2. 安装依赖（由于SSL证书问题，需要使用trusted-host参数）:")
    print("   pip3 install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org")
    print("   pip3 install web3 eth-account python-dotenv")
    print("   pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org solders")
    print()
    print("3. 部署智能合约到目标区块链网络")
    print("4. 确保钱包有足够的Gas费用")


if __name__ == "__main__":
    main()
