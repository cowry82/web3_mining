# 配置文件
config = {
    # 节点配置
    'nodes': {
        'basic': {
            'price': 1000,  # 售价 1000 U
            'max_purchase': 5,  # 每个用户最多购买5次
            'referral_level1': {
                'usdt': 0.05,  # 5% U
                'power': 50  # 50 T 算力
            },
            'referral_level2': {
                'usdt': 0.02,  # 2% U
                'power': 5  # 5T 算力
            },
            'total_supply': 5000  # 5000个
        },
        'intermediate': {
            'price': 3000,  # 售价 3000 U
            'max_purchase': 5,  # 每个用户最多购买5次
            'referral_level1': {
                'usdt': 0.06,  # 6% U
                'power': 100  # 100 T 算力
            },
            'referral_level2': {
                'usdt': 0.03,  # 3% U
                'power': 10  # 10T 算力
            },
            'total_supply': 3000  # 3000个
        },
        'advanced': {
            'price': 10000,  # 售价 1万 U
            'max_purchase': 5,  # 每个用户最多购买5次
            'referral_level1': {
                'usdt': 0.08,  # 8% U
                'power': 150  # 150T 算力
            },
            'referral_level2': {
                'usdt': 0.04,  # 4% U
                'power': 20  # 20T 算力
            },
            'total_supply': 2000  # 2000个
        },
        'genesis': {
            'price': 50000,  # 售价 5万 U
            'max_purchase': 5,  # 每个用户最多购买5次
            'referral_level1': {
                'usdt': 0.1,  # 10% U
                'power': 200  # 200T 算力
            },
            'referral_level2': {
                'usdt': 0.05,  # 5% U
                'power': 50  # 50T 算力
            },
            'total_supply': 300  # 300个
        }
    },
    # 挖矿规则
    'mining': {
        'fixed_rate': 0.03,  # 固定产出速率：0.03 BUB / T
        'min_years': 10,  # 挖矿设定 10年
        'max_years': 15,  # 挖矿设定 15年
        'basic_node_daily_output': {
            'min': 10,  # 1000U 日产 10个BuB
            'max': 30  # 1000U 日产 30个BuB
        }
    },
    # 收益分配
    'reward': {
        'mining_allocation': 0.8,  # 80%用于节点挖矿分配
        'daily_release_rate': 0.01  # 日释放 1%
    },
    # 减产机制
    'halving': {
        'initial_daily_output': 945000,  # 初始日产量：945,000 BUB
        'halving_interval': 1460  # 每 4 年（1,460 天）日产量减半
    },
    # 奖励发放时间
    'reward_time': {
        'hour': 0,  # 每日 00:00
        'minute': 0,
        'second': 0,
        'timezone': 'UTC+8'  # UTC+8
    },
    # 区块链配置
    'blockchain': {
        'bsc': {
            'rpc_url': 'https://bsc-dataseed.binance.org/'
        }
    },
    # 数据库配置
    'database': {
        'type': 'mysql',
        'host': '192.168.2.202',
        'port': 3306,
        'user': 'jys_php',
        'password': 'XGDHy47fxhThDSkA',
        'db': 'bitup-mining'
    },
    # 服务器配置
    'server': {
        'port': 5000
    }
}