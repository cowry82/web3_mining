from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Node:
    # 节点唯一标识符
    node_id: str
    # 用户ID，表示该节点属于哪个用户
    uid: str
    # 节点算力，单位为T（Terahash）
    hashrate: int
    # 节点购买时间
    purchase_time: datetime
    # 节点是否活跃，默认为True
    is_active: bool = True

    @property
    def node_hashrate(self) -> int:
        # 返回节点算力
        return self.hashrate


@dataclass
class User:
    # 用户唯一标识符
    uid: str
    # 用户拥有的节点列表
    nodes: List[Node]
    # 推荐人UID，可选
    referrer_uid: Optional[str] = None
    # 该用户推荐的用户UID列表，默认为空
    referred_users: List[str] = None

    def __post_init__(self):
        # 如果referred_users为None，初始化为空列表
        if self.referred_users is None:
            self.referred_users = []

    @property
    def total_hashrate(self) -> int:
        # 计算用户的总算力，只计算活跃节点的算力总和
        return sum(node.hashrate for node in self.nodes if node.is_active)

    @property
    def active_node_count(self) -> int:
        # 计算用户的活跃节点数量
        return len([node for node in self.nodes if node.is_active])

    def add_node(self, node: Node):
        # 为用户添加一个新节点
        self.nodes.append(node)

    def add_referred_user(self, uid: str):
        # 为用户添加一个被推荐的用户，避免重复添加
        if uid not in self.referred_users:
            self.referred_users.append(uid)


@dataclass
class MiningRecord:
    # 用户ID
    uid: str
    # 挖矿日期
    date: datetime
    # 总产出量
    total_output: float
    # 立即释放的奖励数量
    immediate_release: float
    # 线性释放的奖励数量
    linear_release: float
    # 线性释放的剩余奖励数量
    linear_release_remaining: float
    # 用户总算力
    hashrate: int
    # 全网总算力
    network_hashrate: int


@dataclass
class InvitationReward:
    # 推荐人UID
    referrer_uid: str
    # 被推荐人UID
    referred_uid: str
    # 奖励发放时间
    reward_time: datetime
    # 奖励比例
    reward_ratio: float
    # 算力奖励
    hashrate_reward: int
    # 被推荐节点的算力
    referred_node_hashrate: int
