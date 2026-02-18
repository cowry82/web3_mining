from typing import List, Dict, Optional
from datetime import datetime
from models.models import User, MiningRecord, InvitationReward
from core.calculator import (
    MiningCalculator,
    HalvingCalculator,
    InvitationRewardCalculator
)
from core.blockchain import BlockchainManager
from core.contract import ContractManager
from core.wallet import WalletManager
from services.transaction_manager import TransactionManager, TransactionStatus
from config.mining_config import NODE_CONFIG, DEFAULT_CHAIN, DEMO_MODE


class BlockchainMiningService:
    # 区块链挖矿服务类，整合区块链交互和挖矿业务逻辑
    
    def __init__(self, mining_start_date: datetime):
        # 初始化区块链挖矿服务
        self.mining_start_date = mining_start_date
        self.demo_mode = DEMO_MODE
        self.blockchain_manager = BlockchainManager()
        self.contract_manager = ContractManager(self.blockchain_manager)
        self.wallet_manager = WalletManager()
        self.transaction_manager = TransactionManager()
        self.current_chain = DEFAULT_CHAIN
        self.network_hashrate = 0
        self.total_nodes = 0
        self.users: Dict[str, User] = {}
        
        if self.demo_mode:
            print("⚠️  演示模式已启用，使用模拟数据")
        else:
            print("✓ 生产模式已启用，使用真实链上数据")
    
    def switch_chain(self, chain_key: str) -> bool:
        # 切换到指定的区块链网络
        if chain_key not in self.blockchain_manager.get_supported_chains():
            return False
        self.current_chain = chain_key
        return self.blockchain_manager.switch_chain(chain_key)
    
    def get_current_chain(self) -> str:
        # 获取当前使用的区块链网络
        return self.current_chain
    
    def register_user(self, user: User):
        # 注册用户到区块链挖矿系统
        self.users[user.uid] = user
        # 更新网络统计信息
        self._update_network_stats()
    
    def _update_network_stats(self):
        # 更新网络统计信息（总节点数和总算力）
        self.total_nodes = sum(
            user.active_node_count for user in self.users.values()
        )
        self.network_hashrate = sum(
            user.total_hashrate for user in self.users.values()
        )
    
    def buy_nodes_on_chain(
        self,
        uid: str,
        node_count: int,
        payment_amount: float
    ) -> Optional[str]:
        # 在区块链上购买节点
        if self.demo_mode:
            print(f"[演示模式] 模拟购买 {node_count} 个节点")
            return "0x" + "0" * 64
        
        try:
            # 获取智能合约和钱包实例
            contract = self.contract_manager.get_contract(self.current_chain)
            wallet = self.wallet_manager.get_wallet(self.current_chain)
            
            # 调用智能合约购买节点
            tx_hash = contract.buy_node(node_count, payment_amount)
            
            if tx_hash:
                # 创建交易记录
                self.transaction_manager.create_transaction(
                    tx_hash=tx_hash,
                    chain_key=self.current_chain,
                    from_address=wallet.get_address(),
                    to_address=contract.contract_address,
                    amount=payment_amount
                )
                
                # 更新本地用户数据
                user = self.users.get(uid)
                if user:
                    # 为用户添加新节点
                    for i in range(node_count):
                        from models.models import Node
                        node = Node(
                            node_id=f"node_{uid}_{len(user.nodes)}_{i}",
                            uid=uid,
                            hashrate=NODE_CONFIG['BASE_HASHRATE'],
                            purchase_time=datetime.now()
                        )
                        user.add_node(node)
                    # 更新网络统计信息
                    self._update_network_stats()
                
                return tx_hash
            return None
        except Exception as e:
            print(f"链上购买节点失败: {e}")
            return None
    
    def claim_rewards_on_chain(self, uid: str) -> Optional[str]:
        # 在区块链上领取挖矿奖励
        if self.demo_mode:
            print(f"[演示模式] 模拟领取用户 {uid} 的奖励")
            return "0x" + "1" * 64
        
        try:
            # 获取智能合约和钱包实例
            contract = self.contract_manager.get_contract(self.current_chain)
            wallet = self.wallet_manager.get_wallet(self.current_chain)
            
            # 调用智能合约领取奖励
            tx_hash = contract.claim_rewards()
            
            if tx_hash:
                # 创建交易记录
                self.transaction_manager.create_transaction(
                    tx_hash=tx_hash,
                    chain_key=self.current_chain,
                    from_address=wallet.get_address(),
                    to_address=wallet.get_address(),
                    amount=0
                )
                return tx_hash
            return None
        except Exception as e:
            print(f"链上领取奖励失败: {e}")
            return None
    
    def get_user_nodes_from_chain(self, uid: str) -> List[Dict]:
        # 从区块链上获取用户的节点信息
        if self.demo_mode:
            print(f"[演示模式] 返回用户 {uid} 的模拟节点数据")
            user = self.users.get(uid)
            if user:
                return [
                    {
                        'node_id': node.node_id,
                        'hashrate': node.hashrate,
                        'purchase_time': node.purchase_time.isoformat()
                    }
                    for node in user.nodes
                ]
            return []
        
        try:
            # 获取智能合约和钱包实例
            contract = self.contract_manager.get_contract(self.current_chain)
            wallet = self.wallet_manager.get_wallet(self.current_chain)
            # 调用智能合约获取用户节点
            return contract.get_user_nodes(wallet.get_address())
        except Exception as e:
            print(f"从链上获取用户节点失败: {e}")
            return []
    
    def get_user_rewards_from_chain(self, uid: str) -> float:
        # 从区块链上获取用户的待领取奖励
        if self.demo_mode:
            print(f"[演示模式] 返回用户 {uid} 的模拟奖励数据")
            return 100.0
        
        try:
            # 获取智能合约和钱包实例
            contract = self.contract_manager.get_contract(self.current_chain)
            wallet = self.wallet_manager.get_wallet(self.current_chain)
            # 调用智能合约获取用户奖励
            return contract.get_user_rewards(wallet.get_address())
        except Exception as e:
            print(f"从链上获取用户奖励失败: {e}")
            return 0.0
    
    def get_network_stats_from_chain(self) -> Dict[str, int]:
        # 从区块链上获取网络状态信息
        if self.demo_mode:
            print("[演示模式] 返回模拟网络状态数据")
            return {
                'total_nodes': self.total_nodes,
                'total_hashrate': self.network_hashrate,
                'daily_output': 92400
            }
        
        try:
            # 获取智能合约实例
            contract = self.contract_manager.get_contract(self.current_chain)
            # 调用智能合约获取网络状态
            return contract.get_network_stats()
        except Exception as e:
            print(f"从链上获取网络状态失败: {e}")
            return {
                'total_nodes': 0,
                'total_hashrate': 0,
                'daily_output': 0
            }
    
    def calculate_user_daily_output(
        self,
        user: User,
        current_date: datetime
    ) -> MiningRecord:
        # 计算用户的每日挖矿产出
        node_hashrate = NODE_CONFIG['BASE_HASHRATE']
        
        # 计算总产出量
        total_output = MiningCalculator.calculate_daily_output(
            total_nodes=self.total_nodes,
            personal_hashrate=user.total_hashrate,
            network_hashrate=self.network_hashrate,
            node_hashrate=node_hashrate
        )
        
        # 计算奖励分配（立即释放和线性释放）
        immediate_release, linear_release = MiningCalculator.calculate_release_split(
            total_output
        )
        
        # 创建挖矿记录
        record = MiningRecord(
            uid=user.uid,
            date=current_date,
            total_output=total_output,
            immediate_release=immediate_release,
            linear_release=linear_release,
            linear_release_remaining=linear_release,
            hashrate=user.total_hashrate,
            network_hashrate=self.network_hashrate
        )
        
        return record

    def distribute_daily_rewards(self, current_date: datetime) -> List[MiningRecord]:
        # 分发每日挖矿奖励给所有用户
        records = []
        
        for user in self.users.values():
            # 计算每个用户的每日产出
            record = self.calculate_user_daily_output(user, current_date)
            records.append(record)
        
        return records

    def get_network_daily_output(self, current_date: datetime) -> float:
        # 获取网络每日总产出量（考虑减产）
        return HalvingCalculator.calculate_network_daily_output(
            self.mining_start_date,
            current_date
        )
    
    def get_wallet_balance(self) -> float:
        # 获取钱包余额
        if self.demo_mode:
            print(f"[演示模式] 返回 {self.current_chain} 的模拟钱包余额")
            # 为不同链返回不同的模拟余额
            mock_balances = {
                'ETH': 14134.9542,
                'BSC': 99232.4853,
                'POLYGON': 91665.9462,
                'SOLANA': 50000.0
            }
            return mock_balances.get(self.current_chain, 0.0)
        
        try:
            # 获取区块链连接和钱包实例
            connection = self.blockchain_manager.get_connection(self.current_chain)
            wallet = self.wallet_manager.get_wallet(self.current_chain)
            # 获取余额
            return connection.get_balance(wallet.get_address())
        except Exception as e:
            print(f"获取钱包余额失败: {e}")
            return 0.0
    
    def get_transaction_history(self, limit: int = 100) -> List:
        # 获取交易历史记录
        return self.transaction_manager.get_transaction_history(
            chain_key=self.current_chain,
            limit=limit
        )
    
    def get_transaction_statistics(self) -> Dict:
        # 获取交易统计信息
        return self.transaction_manager.get_transaction_statistics()
