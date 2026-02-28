from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from core.blockchain import BlockchainManager


class MiningContract(ABC):
    # 挖矿智能合约抽象基类，定义了所有挖矿合约必须实现的接口
    
    @abstractmethod
    def buy_node(self, node_count: int, payment_amount: float) -> str:
        # 购买节点，返回交易哈希
        pass
    
    @abstractmethod
    def claim_rewards(self) -> str:
        # 领取挖矿奖励，返回交易哈希
        pass
    
    @abstractmethod
    def get_user_nodes(self, user_address: str) -> List[Dict[str, Any]]:
        # 获取用户的节点列表
        pass
    
    @abstractmethod
    def get_user_rewards(self, user_address: str) -> float:
        # 获取用户的待领取奖励
        pass
    
    @abstractmethod
    def get_network_stats(self) -> Dict[str, Any]:
        # 获取网络状态信息
        pass


class EVMMiningContract(MiningContract):
    # EVM兼容链的挖矿智能合约实现类
    
    def __init__(self, blockchain_manager: BlockchainManager, chain_key: str):
        # 初始化EVM挖矿合约
        self.blockchain_manager = blockchain_manager
        self.chain_key = chain_key
        self.connection = blockchain_manager.get_connection(chain_key)
        self.config = blockchain_manager.get_chain_config(chain_key)
        self.contract_address = self.config['CONTRACT_ADDRESS']
        self.contract = None
        # 自动初始化智能合约
        self._initialize_contract()
    
    def _initialize_contract(self):
        # 初始化智能合约实例
        try:
            from web3 import Web3
            if hasattr(self.connection, 'web3') and self.connection.web3:
                # 获取合约ABI（应用二进制接口）
                abi = self._get_contract_abi()
                # 创建合约实例
                self.contract = self.connection.web3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=abi
                )
                print(f"智能合约初始化成功: {self.contract_address}")
        except Exception as e:
            print(f"智能合约初始化失败: {e}")
    
    def _get_contract_abi(self) -> list:
        # 定义智能合约的ABI（应用二进制接口）
        # ABI定义了合约的函数接口，用于与合约交互
        return [
            {
                "inputs": [
                    {"name": "nodeCount", "type": "uint256"},
                    {"name": "paymentAmount", "type": "uint256"}
                ],
                "name": "buyNode",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "claimRewards",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "user", "type": "address"}],
                "name": "getUserNodes",
                "outputs": [
                    {"name": "nodeIds", "type": "uint256[]"},
                    {"name": "hashrates", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "user", "type": "address"}],
                "name": "getUserRewards",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "getNetworkStats",
                "outputs": [
                    {"name": "totalNodes", "type": "uint256"},
                    {"name": "totalHashrate", "type": "uint256"},
                    {"name": "dailyOutput", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def buy_node(self, node_count: int, payment_amount: float) -> str:
        # 购买节点，调用智能合约的buyNode函数
        try:
            from web3 import Web3
            decimals = self.config['NATIVE_DECIMALS']
            # 将支付金额转换为最小单位（Wei）
            amount_wei = int(payment_amount * (10 ** decimals))
            
            if self.contract:
                # 调用合约的buyNode函数，传入节点数量和支付金额
                tx_hash = self.contract.functions.buyNode(
                    node_count,
                    amount_wei
                ).transact({
                    'value': amount_wei,
                    'gas': 300000,
                    'gasPrice': self.connection.web3.eth.gas_price
                })
                return tx_hash.hex()
            return ""
        except Exception as e:
            print(f"购买节点失败: {e}")
            return ""
    
    def claim_rewards(self) -> str:
        # 领取挖矿奖励，调用智能合约的claimRewards函数
        try:
            if self.contract:
                # 调用合约的claimRewards函数
                tx_hash = self.contract.functions.claimRewards().transact({
                    'gas': 200000,
                    'gasPrice': self.connection.web3.eth.gas_price
                })
                return tx_hash.hex()
            return ""
        except Exception as e:
            print(f"领取奖励失败: {e}")
            return ""
    
    def get_user_nodes(self, user_address: str) -> List[Dict[str, Any]]:
        # 获取用户的节点列表，调用智能合约的getUserNodes函数
        try:
            if self.contract:
                from web3 import Web3
                # 调用合约的getUserNodes函数（只读调用）
                result = self.contract.functions.getUserNodes(
                    Web3.to_checksum_address(user_address)
                ).call()
                
                # 解析返回结果
                nodes = []
                node_ids, hashrates = result
                for i, (node_id, hashrate) in enumerate(zip(node_ids, hashrates)):
                    nodes.append({
                        'node_id': node_id,
                        'hashrate': hashrate,
                        'active': True
                    })
                return nodes
            return []
        except Exception as e:
            print(f"获取用户节点失败: {e}")
            return []
    
    def get_user_rewards(self, user_address: str) -> float:
        # 获取用户的待领取奖励，调用智能合约的getUserRewards函数
        try:
            if self.contract:
                from web3 import Web3
                # 调用合约的getUserRewards函数（只读调用）
                rewards_wei = self.contract.functions.getUserRewards(
                    Web3.to_checksum_address(user_address)
                ).call()
                
                # 将奖励从最小单位转换为标准单位
                decimals = self.config['NATIVE_DECIMALS']
                return rewards_wei / (10 ** decimals)
            return 0.0
        except Exception as e:
            print(f"获取用户奖励失败: {e}")
            return 0.0
    
    def get_network_stats(self) -> Dict[str, Any]:
        # 获取网络状态信息，调用智能合约的getNetworkStats函数
        try:
            if self.contract:
                # 调用合约的getNetworkStats函数（只读调用）
                result = self.contract.functions.getNetworkStats().call()
                return {
                    'total_nodes': result[0],
                    'total_hashrate': result[1],
                    'daily_output': result[2]
                }
            return {
                'total_nodes': 0,
                'total_hashrate': 0,
                'daily_output': 0
            }
        except Exception as e:
            print(f"获取网络状态失败: {e}")
            return {
                'total_nodes': 0,
                'total_hashrate': 0,
                'daily_output': 0
            }


class SolanaMiningContract(MiningContract):
    # Solana区块链的挖矿智能合约实现类
    
    def __init__(self, blockchain_manager: BlockchainManager, chain_key: str):
        # 初始化Solana挖矿合约
        self.blockchain_manager = blockchain_manager
        self.chain_key = chain_key
        self.connection = blockchain_manager.get_connection(chain_key)
        self.config = blockchain_manager.get_chain_config(chain_key)
        self.program_id = self.config['CONTRACT_ADDRESS']
    
    def buy_node(self, node_count: int, payment_amount: float) -> str:
        # 购买节点（Solana实现）
        try:
            from solana.transaction import Transaction
            from solana.system_program import Transfer
            
            transaction = Transaction()
            tx_hash = self.connection.client.send_transaction(
                transaction,
                self.connection.signer
            )
            return str(tx_hash.value)
        except Exception as e:
            print(f"购买节点失败: {e}")
            return ""
    
    def claim_rewards(self) -> str:
        # 领取挖矿奖励（Solana实现）
        try:
            from solana.transaction import Transaction
            
            transaction = Transaction()
            tx_hash = self.connection.client.send_transaction(
                transaction,
                self.connection.signer
            )
            return str(tx_hash.value)
        except Exception as e:
            print(f"领取奖励失败: {e}")
            return ""
    
    def get_user_nodes(self, user_address: str) -> List[Dict[str, Any]]:
        # 获取用户的节点列表（Solana实现）
        return []
    
    def get_user_rewards(self, user_address: str) -> float:
        # 获取用户的待领取奖励（Solana实现）
        return 0.0
    
    def get_network_stats(self) -> Dict[str, Any]:
        # 获取网络状态信息（Solana实现）
        return {
            'total_nodes': 0,
            'total_hashrate': 0,
            'daily_output': 0
        }


class ContractManager:
    # 智能合约管理器，用于管理多个区块链网络的智能合约
    
    def __init__(self, blockchain_manager: BlockchainManager):
        # 初始化智能合约管理器
        self.blockchain_manager = blockchain_manager
        self.contracts: Dict[str, MiningContract] = {}
        # 初始化所有配置的智能合约
        self._initialize_contracts()
    
    def _initialize_contracts(self):
        # 只初始化默认链的合约，避免其他链连接失败的问题
        from config.mining_config import DEFAULT_CHAIN
        
        try:
            if DEFAULT_CHAIN == 'SOLANA':
                # Solana使用SolanaMiningContract类
                self.contracts[DEFAULT_CHAIN] = SolanaMiningContract(
                    self.blockchain_manager, DEFAULT_CHAIN
                )
            else:
                # 其他EVM兼容链使用EVMMiningContract类
                self.contracts[DEFAULT_CHAIN] = EVMMiningContract(
                    self.blockchain_manager, DEFAULT_CHAIN
                )
        except Exception as e:
            print(f"警告: 默认链 {DEFAULT_CHAIN} 合约初始化失败: {e}")
    
    def get_contract(self, chain_key: str) -> MiningContract:
        # 获取指定区块链的智能合约实例
        if chain_key not in self.contracts:
            # 动态初始化该链的合约
            try:
                if chain_key == 'SOLANA':
                    # Solana使用SolanaMiningContract类
                    self.contracts[chain_key] = SolanaMiningContract(
                        self.blockchain_manager, chain_key
                    )
                else:
                    # 其他EVM兼容链使用EVMMiningContract类
                    self.contracts[chain_key] = EVMMiningContract(
                        self.blockchain_manager, chain_key
                    )
                print(f"✓ {chain_key} 合约已初始化")
            except Exception as e:
                print(f"✗ {chain_key} 合约初始化失败: {e}")
                raise ValueError(f"不支持的区块链: {chain_key}")
        return self.contracts[chain_key]
