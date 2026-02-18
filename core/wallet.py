from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from config.mining_config import WALLET_CONFIG


class Wallet(ABC):
    # 钱包抽象基类，定义了所有钱包必须实现的接口
    
    @abstractmethod
    def get_address(self) -> str:
        # 获取钱包地址
        pass
    
    @abstractmethod
    def get_private_key(self) -> str:
        # 获取钱包私钥
        pass
    
    @abstractmethod
    def sign_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        # 签名交易，返回签名后的交易数据
        pass


class EVMWallet(Wallet):
    # EVM兼容链的钱包实现类（支持以太坊、BSC、Polygon等）
    
    def __init__(self, private_key: Optional[str] = None, address: Optional[str] = None):
        # 初始化EVM钱包
        self.private_key = private_key or WALLET_CONFIG['PRIVATE_KEY']
        self.address = address or WALLET_CONFIG['ADDRESS']
        self.account = None
        # 自动初始化账户
        self._initialize_account()
    
    def _initialize_account(self):
        # 初始化EVM账户
        try:
            from eth_account import Account
            if self.private_key and self.private_key != 'YOUR_PRIVATE_KEY_HERE' and self.private_key != 'your_private_key_here':
                # 从私钥创建账户
                self.account = Account.from_key(self.private_key)
                self.address = self.account.address
                print(f"EVM钱包初始化成功: {self.address}")
            else:
                print("警告: 未配置私钥，使用演示模式")
                self.address = '0x0000000000000000000000000000000000000000'
        except ImportError:
            print("警告: eth-account 未安装，使用模拟模式")
            self.address = '0x0000000000000000000000000000000000000000'
        except Exception as e:
            print(f"警告: EVM钱包初始化失败: {e}，使用演示模式")
            self.address = '0x0000000000000000000000000000000000000000'
    
    def get_address(self) -> str:
        # 获取钱包地址
        return self.address
    
    def get_private_key(self) -> str:
        # 获取钱包私钥
        return self.private_key
    
    def sign_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        # 签名交易
        if self.account:
            try:
                # 使用账户签名交易
                signed_tx = self.account.sign_transaction(transaction_data)
                return {
                    'rawTransaction': signed_tx.rawTransaction.hex(),
                    'hash': signed_tx.hash.hex()
                }
            except Exception as e:
                print(f"签名交易失败: {e}")
        return transaction_data


class SolanaWallet(Wallet):
    # Solana区块链的钱包实现类
    
    def __init__(self, private_key: Optional[str] = None, address: Optional[str] = None):
        # 初始化Solana钱包
        self.private_key = private_key or WALLET_CONFIG.get('SOLANA_PRIVATE_KEY', '')
        self.address = address or WALLET_CONFIG.get('SOLANA_ADDRESS', '')
        self.keypair = None
        # 自动初始化密钥对
        self._initialize_keypair()
    
    def _initialize_keypair(self):
        # 初始化Solana密钥对
        try:
            from solders.keypair import Keypair
            from solders.pubkey import Pubkey
            if self.private_key and self.private_key != 'YOUR_PRIVATE_KEY_HERE' and self.private_key != 'your_solana_private_key_here':
                # 尝试从Base58编码的私钥创建密钥对
                try:
                    self.keypair = Keypair.from_base58_secret(self.private_key)
                    self.address = str(self.keypair.pubkey())
                    print(f"Solana钱包初始化成功: {self.address}")
                except Exception as e:
                    print(f"警告: Solana私钥格式错误: {e}，使用演示模式")
                    self.address = '11111111111111111111111111111111'
            else:
                print("警告: 未配置Solana私钥，使用演示模式")
                self.address = '11111111111111111111111111111111'
        except ImportError:
            print("警告: solders 未安装，使用演示模式")
            self.address = '11111111111111111111111111111111'
        except Exception as e:
            print(f"警告: Solana钱包初始化失败: {e}，使用演示模式")
            self.address = '11111111111111111111111111111111'
    
    def get_address(self) -> str:
        # 获取钱包地址
        return self.address
    
    def get_private_key(self) -> str:
        # 获取钱包私钥
        return self.private_key
    
    def sign_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        # 签名交易
        if self.keypair:
            try:
                from solana.transaction import Transaction
                transaction = transaction_data.get('transaction')
                if transaction:
                    # 使用密钥对签名交易
                    transaction.sign(self.keypair)
                    return {
                        'transaction': transaction,
                        'signature': str(transaction.signatures[0])
                    }
            except Exception as e:
                print(f"签名交易失败: {e}")
        return transaction_data


class WalletManager:
    # 钱包管理器，用于管理多个区块链网络的钱包
    
    def __init__(self):
        # 初始化钱包管理器
        self.wallets: Dict[str, Wallet] = {}
        # 初始化所有配置的钱包
        self._initialize_wallets()
    
    def _initialize_wallets(self):
        # 初始化所有配置的钱包
        # ETH、BSC、POLYGON使用EVM钱包
        self.wallets['ETH'] = EVMWallet()
        self.wallets['BSC'] = EVMWallet()
        self.wallets['POLYGON'] = EVMWallet()
        # SOLANA使用Solana钱包
        self.wallets['SOLANA'] = SolanaWallet()
    
    def get_wallet(self, chain_key: str) -> Wallet:
        # 获取指定区块链的钱包实例
        if chain_key not in self.wallets:
            raise ValueError(f"不支持的区块链: {chain_key}")
        return self.wallets[chain_key]
    
    def get_address(self, chain_key: str) -> str:
        # 获取指定区块链的钱包地址
        return self.get_wallet(chain_key).get_address()
    
    def sign_transaction(self, chain_key: str, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        # 使用指定区块链的钱包签名交易
        return self.get_wallet(chain_key).sign_transaction(transaction_data)
    
    def update_wallet(self, chain_key: str, private_key: str, address: Optional[str] = None):
        # 更新指定区块链的钱包信息
        if chain_key in ['ETH', 'BSC', 'POLYGON']:
            # EVM兼容链使用EVM钱包
            self.wallets[chain_key] = EVMWallet(private_key, address)
        elif chain_key == 'SOLANA':
            # Solana使用Solana钱包
            self.wallets[chain_key] = SolanaWallet(private_key, address)
        else:
            raise ValueError(f"不支持的区块链: {chain_key}")
