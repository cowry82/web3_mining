from typing import List, Dict
from datetime import datetime
from models.models import User, MiningRecord, InvitationReward
from core.calculator import (
    MiningCalculator,
    HalvingCalculator,
    InvitationRewardCalculator
)
from config.mining_config import NODE_CONFIG


class MiningService:
    # 挖矿服务类，负责处理挖矿相关的业务逻辑
    
    def __init__(self, mining_start_date: datetime):
        # 初始化挖矿服务
        self.mining_start_date = mining_start_date
        self.network_hashrate = 0
        self.total_nodes = 0
        self.users: Dict[str, User] = {}

    def register_user(self, user: User):
        # 注册用户到挖矿系统
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


class RewardService:
    # 奖励服务类，负责处理邀请奖励相关的业务逻辑
    
    def __init__(self):
        # 初始化奖励服务
        self.invitation_rewards: List[InvitationReward] = []

    def process_referral(
        self,
        referrer: User,
        referred_user: User,
        referred_node_hashrate: int,
        reward_time: datetime
    ) -> InvitationReward:
        # 处理推荐奖励
        # 计算推荐奖励（代币奖励和算力奖励）
        reward_amount, hashrate_reward = InvitationRewardCalculator.calculate_referral_reward(
            referred_node_hashrate
        )
        
        # 创建邀请奖励记录
        reward = InvitationReward(
            referrer_uid=referrer.uid,
            referred_uid=referred_user.uid,
            reward_time=reward_time,
            reward_ratio=reward_amount / referred_node_hashrate,
            hashrate_reward=hashrate_reward,
            referred_node_hashrate=referred_node_hashrate
        )
        
        # 保存奖励记录并更新推荐人的推荐列表
        self.invitation_rewards.append(reward)
        referrer.add_referred_user(referred_user.uid)
        
        return reward

    def calculate_investment_return(self, investment_usd: float) -> Dict[str, float]:
        # 计算投资的回报范围
        daily_min, daily_max = InvitationRewardCalculator.calculate_investment_daily_output(
            investment_usd
        )
        
        return {
            'daily_output_min': daily_min,
            'daily_output_max': daily_max,
            'investment_usd': investment_usd
        }


class ReleaseService:
    # 释放服务类，负责处理线性释放相关的业务逻辑
    
    def __init__(self):
        # 初始化释放服务
        self.pending_releases: Dict[str, List[float]] = {}

    def add_pending_release(self, uid: str, linear_release: float):
        # 添加待释放的线性奖励到用户的待释放列表
        if uid not in self.pending_releases:
            self.pending_releases[uid] = []
        self.pending_releases[uid].append(linear_release)

    def process_daily_release(self, uid: str) -> float:
        # 处理用户的每日线性释放
        if uid not in self.pending_releases:
            return 0.0
        
        total_daily_release = 0.0
        remaining_releases = []
        
        # 遍历所有待释放的奖励，计算每日释放量
        for pending in self.pending_releases[uid]:
            # 计算每日释放量
            daily_release = InvitationRewardCalculator.calculate_bub_daily_release(pending)
            total_daily_release += daily_release
            # 计算剩余待释放量
            remaining = pending - daily_release
            
            # 如果还有剩余，保留到下次释放
            if remaining > 0.001:
                remaining_releases.append(remaining)
        
        # 更新待释放列表
        self.pending_releases[uid] = remaining_releases
        
        return total_daily_release

    def get_pending_release_amount(self, uid: str) -> float:
        # 获取用户的待释放总额
        if uid not in self.pending_releases:
            return 0.0
        return sum(self.pending_releases[uid])
