from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TransactionStatus(Enum):
    # 交易状态枚举
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class Transaction:
    # 交易数据类，用于存储交易信息
    # 交易哈希，唯一标识一笔交易
    tx_hash: str
    # 区块链网络标识
    chain_key: str
    # 发送方地址
    from_address: str
    # 接收方地址
    to_address: str
    # 交易金额
    amount: float
    # 使用的Gas数量
    gas_used: Optional[float] = None
    # Gas价格
    gas_price: Optional[float] = None
    # 交易状态
    status: TransactionStatus = TransactionStatus.PENDING
    # 交易时间戳
    timestamp: datetime = None
    # 区块高度
    block_number: Optional[int] = None
    # 错误信息
    error_message: Optional[str] = None

    def __post_init__(self):
        # 如果未指定时间戳，使用当前时间
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TransactionManager:
    # 交易管理器，用于管理区块链交易
    
    def __init__(self):
        # 初始化交易管理器
        self.transactions: Dict[str, Transaction] = {}
        # 待确认的交易哈希列表
        self.pending_transactions: List[str] = []
    
    def create_transaction(
        self,
        tx_hash: str,
        chain_key: str,
        from_address: str,
        to_address: str,
        amount: float,
        gas_used: Optional[float] = None,
        gas_price: Optional[float] = None
    ) -> Transaction:
        # 创建并记录一笔新交易
        transaction = Transaction(
            tx_hash=tx_hash,
            chain_key=chain_key,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            gas_used=gas_used,
            gas_price=gas_price
        )
        # 保存交易记录
        self.transactions[tx_hash] = transaction
        # 添加到待确认列表
        self.pending_transactions.append(tx_hash)
        return transaction
    
    def update_transaction_status(
        self,
        tx_hash: str,
        status: TransactionStatus,
        block_number: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        # 更新交易状态
        if tx_hash not in self.transactions:
            return False
        
        # 更新交易信息
        transaction = self.transactions[tx_hash]
        transaction.status = status
        transaction.block_number = block_number
        transaction.error_message = error_message
        
        # 如果交易不再是待确认状态，从待确认列表中移除
        if status != TransactionStatus.PENDING and tx_hash in self.pending_transactions:
            self.pending_transactions.remove(tx_hash)
        
        return True
    
    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        # 根据交易哈希获取交易记录
        return self.transactions.get(tx_hash)
    
    def get_transactions_by_chain(self, chain_key: str) -> List[Transaction]:
        # 获取指定区块链网络的所有交易
        return [
            tx for tx in self.transactions.values()
            if tx.chain_key == chain_key
        ]
    
    def get_transactions_by_address(self, address: str) -> List[Transaction]:
        # 获取指定地址相关的所有交易（作为发送方或接收方）
        return [
            tx for tx in self.transactions.values()
            if tx.from_address == address or tx.to_address == address
        ]
    
    def get_pending_transactions(self) -> List[Transaction]:
        # 获取所有待确认的交易
        return [
            self.transactions[tx_hash]
            for tx_hash in self.pending_transactions
        ]
    
    def get_transaction_history(
        self,
        chain_key: Optional[str] = None,
        status: Optional[TransactionStatus] = None,
        limit: int = 100
    ) -> List[Transaction]:
        # 获取交易历史记录，支持按区块链和状态过滤
        transactions = list(self.transactions.values())
        
        # 按区块链过滤
        if chain_key:
            transactions = [tx for tx in transactions if tx.chain_key == chain_key]
        
        # 按状态过滤
        if status:
            transactions = [tx for tx in transactions if tx.status == status]
        
        # 按时间倒序排序
        transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 返回指定数量的交易
        return transactions[:limit]
    
    def calculate_total_gas_spent(self, chain_key: Optional[str] = None) -> float:
        # 计算总Gas消耗量
        transactions = self.transactions.values()
        
        # 按区块链过滤
        if chain_key:
            transactions = [tx for tx in transactions if tx.chain_key == chain_key]
        
        # 计算总Gas费用
        total_gas = 0.0
        for tx in transactions:
            if tx.gas_used and tx.gas_price:
                total_gas += tx.gas_used * tx.gas_price
        
        return total_gas
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        # 获取交易统计信息
        total_transactions = len(self.transactions)
        pending_count = len(self.pending_transactions)
        confirmed_count = len([
            tx for tx in self.transactions.values()
            if tx.status == TransactionStatus.CONFIRMED
        ])
        failed_count = len([
            tx for tx in self.transactions.values()
            if tx.status == TransactionStatus.FAILED
        ])
        
        return {
            'total_transactions': total_transactions,
            'pending_count': pending_count,
            'confirmed_count': confirmed_count,
            'failed_count': failed_count,
            'success_rate': (confirmed_count / total_transactions * 100) if total_transactions > 0 else 0
        }
