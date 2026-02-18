from typing import Tuple
from datetime import datetime, timedelta
from config.mining_config import (
    MINING_CONFIG,
    HALVING_CONFIG,
    REWARD_CONFIG,
    INVITATION_CONFIG
)


class MiningCalculator:
    # 挖矿计算器，用于计算用户的挖矿收益
    
    @staticmethod
    def calculate_daily_output_early_phase(total_nodes: int, node_hashrate: int) -> float:
        # 计算早期阶段的每日产出量
        # 早期阶段分为两个阶段，根据全网节点数量决定产出率
        phase1_max = MINING_CONFIG['EARLY_PHASE']['PHASE_1']['MAX_NODES']
        phase2_max = MINING_CONFIG['EARLY_PHASE']['PHASE_2']['MAX_NODES']
        
        if total_nodes <= phase1_max:
            # 第一阶段：节点数量 <= 5000
            output_rate = MINING_CONFIG['EARLY_PHASE']['PHASE_1']['OUTPUT_RATE']
        elif total_nodes <= phase2_max:
            # 第二阶段：节点数量在5000-10000之间
            output_rate = MINING_CONFIG['EARLY_PHASE']['PHASE_2']['OUTPUT_RATE']
        else:
            # 超过早期阶段，返回0
            return 0.0
        
        # 计算产出量 = 节点算力 * 产出率
        return node_hashrate * output_rate

    @staticmethod
    def calculate_daily_output_regular_phase(
        personal_hashrate: int,
        network_hashrate: int
    ) -> float:
        # 计算常规阶段的每日产出量
        # 常规阶段根据用户算力占全网算力的比例分配奖励
        total_daily_output = MINING_CONFIG['REGULAR_PHASE']['TOTAL_DAILY_OUTPUT']
        mining_allocation = MINING_CONFIG['REGULAR_PHASE']['MINING_ALLOCATION']
        
        # 挖矿池 = 全网每日总产出 * 挖矿分配比例
        mining_pool = total_daily_output * mining_allocation
        
        # 用户产出 = (用户算力 / 全网算力) * 挖矿池
        return (personal_hashrate / network_hashrate) * mining_pool

    @staticmethod
    def calculate_daily_output(
        total_nodes: int,
        personal_hashrate: int,
        network_hashrate: int,
        node_hashrate: int
    ) -> float:
        # 计算每日产出量，根据当前阶段自动选择计算方式
        phase2_max = MINING_CONFIG['EARLY_PHASE']['PHASE_2']['MAX_NODES']
        
        if total_nodes <= phase2_max:
            # 早期阶段：使用早期阶段计算方式
            return MiningCalculator.calculate_daily_output_early_phase(
                total_nodes, node_hashrate
            )
        else:
            # 常规阶段：使用常规阶段计算方式
            return MiningCalculator.calculate_daily_output_regular_phase(
                personal_hashrate, network_hashrate
            )

    @staticmethod
    def calculate_release_split(total_output: float) -> Tuple[float, float]:
        # 计算奖励释放分配，分为立即释放和线性释放两部分
        immediate_ratio = REWARD_CONFIG['IMMEDIATE_RELEASE_RATIO']
        linear_ratio = REWARD_CONFIG['LINEAR_RELEASE_RATIO']
        
        # 立即释放 = 总产出 * 立即释放比例
        immediate_release = total_output * immediate_ratio
        # 线性释放 = 总产出 * 线性释放比例
        linear_release = total_output * linear_ratio
        
        return immediate_release, linear_release

    @staticmethod
    def calculate_linear_release_daily(linear_release_total: float) -> float:
        # 计算线性释放的每日释放量
        release_days = REWARD_CONFIG['LINEAR_RELEASE_DAYS']
        # 每日释放 = 线性释放总额 / 释放天数
        return linear_release_total / release_days


class HalvingCalculator:
    # 减产计算器，用于计算减产机制下的每日产出量
    
    @staticmethod
    def calculate_halving_count(start_date: datetime, current_date: datetime) -> int:
        # 计算已经发生的减产次数
        halving_period_days = HALVING_CONFIG['HALVING_PERIOD_DAYS']
        # 计算经过的天数
        days_passed = (current_date - start_date).days
        # 减产次数 = 经过的天数 / 减产周期天数
        return days_passed // halving_period_days

    @staticmethod
    def calculate_current_daily_output(
        start_date: datetime,
        current_date: datetime
    ) -> float:
        # 计算当前日期的每日产出量（考虑减产）
        initial_output = HALVING_CONFIG['INITIAL_DAILY_OUTPUT']
        # 计算减产次数
        halving_count = HalvingCalculator.calculate_halving_count(
            start_date, current_date
        )
        
        # 当前每日产出 = 初始产出 / (2的减产次数次方)
        return initial_output / (2 ** halving_count)

    @staticmethod
    def calculate_network_daily_output(
        start_date: datetime,
        current_date: datetime
    ) -> float:
        # 计算网络每日总产出量
        return HalvingCalculator.calculate_current_daily_output(
            start_date, current_date
        )


class InvitationRewardCalculator:
    # 邀请奖励计算器，用于计算推荐奖励
    
    @staticmethod
    def calculate_referral_reward(referred_node_hashrate: int) -> Tuple[float, int]:
        # 计算直推奖励
        reward_ratio = INVITATION_CONFIG['DIRECT_REFERRAL_REWARD_RATIO']
        hashrate_reward = INVITATION_CONFIG['DIRECT_REFERRAL_HASHRATE_REWARD']
        
        # 代币奖励 = 被推荐节点算力 * 奖励比例
        reward_amount = referred_node_hashrate * reward_ratio
        
        return reward_amount, hashrate_reward

    @staticmethod
    def calculate_bub_daily_release(total_bub: float) -> float:
        # 计算BUB代币的每日释放量
        daily_release_ratio = INVITATION_CONFIG['BUB_DAILY_RELEASE_RATIO']
        # 每日释放 = 总BUB代币 * 每日释放比例
        return total_bub * daily_release_ratio

    @staticmethod
    def calculate_investment_daily_output(investment_usd: float) -> Tuple[float, float]:
        # 计算投资的每日产出范围
        min_output = INVITATION_CONFIG['INVESTMENT_1000U_DAILY_OUTPUT_MIN']
        max_output = INVITATION_CONFIG['INVESTMENT_1000U_DAILY_OUTPUT_MAX']
        
        # 每日最低产出 = (投资金额 / 1000) * 最低产出率
        daily_output_min = (investment_usd / 1000) * min_output
        # 每日最高产出 = (投资金额 / 1000) * 最高产出率
        daily_output_max = (investment_usd / 1000) * max_output
        
        return daily_output_min, daily_output_max
