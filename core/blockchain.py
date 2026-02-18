from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from config.mining_config import BLOCKCHAIN_CONFIG, DEFAULT_CHAIN, WALLET_CONFIG


class BlockchainConnection(ABC):
    # 区块链连接抽象基类，定义了所有区块链连接必须实现的接口
    
    @abstractmethod
    def connect(self) -> bool:
        # 连接到区块链网络
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> float:
        # 获取指定地址的余额
        pass
    
    @abstractmethod
    def send_transaction(self, transaction_data: Dict[str, Any]) -> str:
        # 发送交易到区块链网络，返回交易哈希
        pass
    
    @abstractmethod
    def get_transaction_status(self, tx_hash: str) -> str:
        # 获取交易状态，返回'confirmed'、'failed'或'pending'
        pass


class EVMBlockchain(BlockchainConnection):
    # EVM兼容区块链连接类（支持以太坊、BSC、Polygon等）
    
    def __init__(self, chain_key: str):
        # 初始化EVM区块链连接
        self.chain_key = chain_key
        self.config = BLOCKCHAIN_CONFIG[chain_key]
        self.web3 = None
        self.demo_mode = not WALLET_CONFIG['PRIVATE_KEY'] or WALLET_CONFIG['PRIVATE_KEY'] == ''
        # 自动连接到区块链网络
        self._connect()
    
    def _connect(self):
        # 内部连接方法，尝试连接到配置的RPC节点
        if self.demo_mode:
            print(f"[演示模式] {self.config['NAME']} 使用模拟连接")
            return False
        
        try:
            from web3 import Web3
            # 遍历所有配置的RPC URL，直到成功连接
            for rpc_url in self.config['RPC_URLS']:
                if not rpc_url or 'YOUR_API_KEY' in rpc_url:
                    continue
                self.web3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.web3.is_connected():
                    print(f"成功连接到 {self.config['NAME']}: {rpc_url}")
                    return True
            raise ConnectionError(f"无法连接到 {self.config['NAME']}")
        except ImportError:
            print("警告: web3.py 未安装，使用模拟模式")
            self.web3 = None
            return False
    
    def connect(self) -> bool:
        # 检查连接状态
        return self.web3 is not None
    
    def get_balance(self, address: str) -> float:
        # 获取指定地址的余额
        if self.demo_mode:
            print(f"[演示模式] 返回 {self.config['NAME']} 的模拟余额")
            mock_balances = {
                'ETH': 14134.9542,
                'BSC': 99232.4853,
                'POLYGON': 91665.9462
            }
            return mock_balances.get(self.chain_key, 0.0)
        
        if self.web3:
            try:
                # 获取余额（单位为Wei）
                balance_wei = self.web3.eth.get_balance(address)
                # 转换为标准单位（考虑小数位数）
                decimals = self.config['NATIVE_DECIMALS']
                return balance_wei / (10 ** decimals)
            except Exception as e:
                print(f"获取余额失败: {e}")
                return 0.0
        return 0.0
    
    def send_transaction(self, transaction_data: Dict[str, Any]) -> str:
        # 发送交易到区块链网络
        if self.demo_mode:
            print(f"[演示模式] 模拟发送交易")
            return "0x" + "0" * 64
        
        if self.web3:
            try:
                # 发送交易并返回交易哈希
                tx_hash = self.web3.eth.send_transaction(transaction_data)
                return tx_hash.hex()
            except Exception as e:
                print(f"发送交易失败: {e}")
                return ""
        return ""
    
    def get_transaction_status(self, tx_hash: str) -> str:
        # 获取交易状态
        if self.demo_mode:
            print(f"[演示模式] 返回模拟交易状态")
            return 'confirmed'
        
        if self.web3:
            try:
                # 获取交易收据
                receipt = self.web3.eth.get_transaction_receipt(tx_hash)
                # 状态为1表示成功，0表示失败
                return 'confirmed' if receipt['status'] == 1 else 'failed'
            except Exception as e:
                print(f"获取交易状态失败: {e}")
                return 'pending'
        return 'unknown'


class SolanaBlockchain(BlockchainConnection):
    # Solana区块链连接类
    
    def __init__(self, chain_key: str):
        # 初始化Solana区块链连接
        self.chain_key = chain_key
        self.config = BLOCKCHAIN_CONFIG[chain_key]
        self.client = None
        self.demo_mode = not WALLET_CONFIG['PRIVATE_KEY'] or WALLET_CONFIG['PRIVATE_KEY'] == ''
        # 自动连接到Solana网络
        self._connect()
    
    def _connect(self):
        # 内部连接方法，尝试连接到配置的RPC节点
        if self.demo_mode:
            print(f"[演示模式] {self.config['NAME']} 使用模拟连接")
            return False
        
        try:
            from solders.rpc.requests import GetBalanceRequest
            from solders.rpc.config import RpcRequestConfig
            # 遍历所有配置的RPC URL，直到成功连接
            for rpc_url in self.config['RPC_URLS']:
                try:
                    # 创建简单的连接测试
                    import requests
                    response = requests.get(rpc_url, timeout=5)
                    if response.status_code == 200:
                        print(f"成功连接到 {self.config['NAME']}: {rpc_url}")
                        self.rpc_url = rpc_url
                        return True
                except Exception as e:
                    continue
            raise ConnectionError(f"无法连接到 {self.config['NAME']}")
        except ImportError:
            print("警告: solders 未安装，使用模拟模式")
            self.client = None
            return False
        except Exception as e:
            print(f"警告: Solana连接失败: {e}，使用模拟模式")
            self.client = None
            return False
    
    def connect(self) -> bool:
        # 检查连接状态
        return self.client is not None
    
    def get_balance(self, address: str) -> float:
        # 获取指定地址的余额
        if self.demo_mode:
            print(f"[演示模式] 返回 {self.config['NAME']} 的模拟余额")
            return 50000.0
        
        if self.client:
            try:
                from solana.publickey import PublicKey
                # 获取余额（单位为lamports）
                balance = self.client.get_balance(PublicKey(address))
                # 转换为标准单位（考虑小数位数）
                decimals = self.config['NATIVE_DECIMALS']
                return balance['result']['value'] / (10 ** decimals)
            except Exception as e:
                print(f"获取余额失败: {e}")
                return 0.0
        return 0.0
    
    def send_transaction(self, transaction_data: Dict[str, Any]) -> str:
        # 发送交易到Solana网络
        if self.demo_mode:
            print(f"[演示模式] 模拟发送交易")
            return "0x" + "0" * 64
        
        if self.client:
            try:
                from solana.transaction import Transaction
                # 发送交易并返回交易签名
                result = self.client.send_transaction(Transaction(), transaction_data['signer'])
                return str(result.value)
            except Exception as e:
                print(f"发送交易失败: {e}")
                return ""
        return ""
    
    def get_transaction_status(self, tx_hash: str) -> str:
        # 获取交易状态
        if self.demo_mode:
            print(f"[演示模式] 返回模拟交易状态")
            return 'confirmed'
        
        if self.client:
            try:
                from solana.publickey import PublicKey
                # 查询交易信息
                result = self.client.get_transaction(PublicKey(tx_hash))
                if result['result']:
                    return 'confirmed'
                return 'pending'
            except Exception as e:
                print(f"获取交易状态失败: {e}")
                return 'pending'
        return 'unknown'


class BlockchainManager:
    # 区块链管理器，用于管理多个区块链网络的连接
    
    def __init__(self):
        # 初始化区块链管理器
        self.connections: Dict[str, BlockchainConnection] = {}
        # 初始化所有配置的区块链连接
        self._initialize_connections()
    
    def _initialize_connections(self):
        # 初始化所有配置的区块链连接
        # 只初始化默认链的连接，避免不必要的网络请求
        try:
            if DEFAULT_CHAIN == 'SOLANA':
                # Solana使用SolanaBlockchain类
                self.connections[DEFAULT_CHAIN] = SolanaBlockchain(DEFAULT_CHAIN)
            else:
                # 其他EVM兼容链使用EVMBlockchain类
                self.connections[DEFAULT_CHAIN] = EVMBlockchain(DEFAULT_CHAIN)
        except Exception as e:
            # 如果默认链连接失败，记录错误
            print(f"警告: 默认链 {DEFAULT_CHAIN} 连接初始化失败: {e}")
            self.connections[DEFAULT_CHAIN] = None
    
    def get_connection(self, chain_key: Optional[str] = None) -> BlockchainConnection:
        # 获取指定区块链的连接，如果未指定则使用默认链
        if chain_key is None:
            chain_key = DEFAULT_CHAIN
        
        if chain_key not in self.connections:
            raise ValueError(f"不支持的区块链: {chain_key}")
        
        connection = self.connections[chain_key]
        if connection is None:
            raise ValueError(f"区块链 {chain_key} 连接未初始化")
        
        return connection
    
    def get_supported_chains(self) -> list[str]:
        # 获取所有支持的区块链列表
        return list(BLOCKCHAIN_CONFIG.keys())
    
    def get_chain_config(self, chain_key: str) -> Dict[str, Any]:
        # 获取指定区块链的配置信息
        if chain_key not in BLOCKCHAIN_CONFIG:
            raise ValueError(f"不支持的区块链: {chain_key}")
        return BLOCKCHAIN_CONFIG[chain_key]
    
    def switch_chain(self, chain_key: str) -> bool:
        # 切换到指定的区块链网络
        if chain_key not in BLOCKCHAIN_CONFIG:
            return False
        
        # 如果该链尚未初始化，则初始化它
        if chain_key not in self.connections or self.connections[chain_key] is None:
            try:
                if chain_key == 'SOLANA':
                    self.connections[chain_key] = SolanaBlockchain(chain_key)
                else:
                    self.connections[chain_key] = EVMBlockchain(chain_key)
                print(f"✓ {chain_key} 链已初始化")
            except Exception as e:
                print(f"✗ {chain_key} 链初始化失败: {e}")
                return False
        
        # 检查连接状态
        return self.connections[chain_key].connect()
