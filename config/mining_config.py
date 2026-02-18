# 节点配置
import os
from dotenv import load_dotenv

load_dotenv()

NODE_CONFIG = {
    'BASE_HASHRATE': 500,
    'MAX_NODES_PER_UID': 200,
    'MAX_HASHRATE_PER_UID': 100000
}

# 挖矿配置
MINING_CONFIG = {
    # 早期阶段配置（节点数量较少时）
    'EARLY_PHASE': {
        # 第一阶段：节点数量在0-5000之间
        'PHASE_1': {
            # 第一阶段最大节点数量
            'MAX_NODES': 5000,
            # 第一阶段产出率，每个单位算力每天产出0.03个代币
            'OUTPUT_RATE': 0.03
        },
        # 第二阶段：节点数量在5000-10000之间
        'PHASE_2': {
            # 第二阶段最大节点数量
            'MAX_NODES': 10000,
            # 第二阶段产出率，每个单位算力每天产出0.014个代币（较第一阶段降低）
            'OUTPUT_RATE': 0.014
        }
    },
    # 常规阶段配置（节点数量超过10000后）
    'REGULAR_PHASE': {
        # 全网每日总产出量（单位：代币）
        'TOTAL_DAILY_OUTPUT': 92400,
        # 挖矿分配比例，80%的代币用于挖矿奖励
        'MINING_ALLOCATION': 0.8
    }
}

# 奖励释放配置
REWARD_CONFIG = {
    # 立即释放比例，80%的挖矿奖励立即到账
    'IMMEDIATE_RELEASE_RATIO': 0.8,
    # 线性释放比例，20%的挖矿奖励需要线性释放
    'LINEAR_RELEASE_RATIO': 0.2,
    # 线性释放周期，剩余的20%在10天内每天平均释放
    'LINEAR_RELEASE_DAYS': 10,
    # 奖励分发时间，每天00:00分发奖励
    'DISTRIBUTION_TIME': '00:00',
    # 时区设置，使用UTC+8（北京时间）
    'TIMEZONE': 'UTC+8'
}

# 减产机制配置（类似比特币的减产机制）
HALVING_CONFIG = {
    # 初始每日产出量，系统启动时每天产出92400个代币
    'INITIAL_DAILY_OUTPUT': 92400,
    # 减产周期天数，每1460天（约4年）减产一次
    'HALVING_PERIOD_DAYS': 1460,
    # 减产周期年数，每4年减产一次
    'HALVING_PERIOD_YEARS': 4
}

# 邀请奖励配置
INVITATION_CONFIG = {
    # 直推奖励比例，推荐人获得被推荐人节点算力的10%作为奖励
    'DIRECT_REFERRAL_REWARD_RATIO': 0.1,
    # 直推算力奖励，推荐人额外获得200T的算力奖励
    'DIRECT_REFERRAL_HASHRATE_REWARD': 200,
    # 挖矿时长范围，挖矿可持续10-15年
    'MINING_DURATION_YEARS_MIN': 10,
    'MINING_DURATION_YEARS_MAX': 15,
    # BUB代币每日释放比例，线性释放的代币每天释放1%
    'BUB_DAILY_RELEASE_RATIO': 0.01,
    # 投资1000U每日最低产出，投资1000美元每天至少产出10个代币
    'INVESTMENT_1000U_DAILY_OUTPUT_MIN': 10,
    # 投资1000U每日最高产出，投资1000美元每天最多产出30个代币
    'INVESTMENT_1000U_DAILY_OUTPUT_MAX': 30
}

# 权益配置
BENEFITS_CONFIG = {
    # 永久挖矿，节点购买后永久有效
    'PERMANENT_MINING': True,
    # 手续费返佣最高比例，最高可返佣50%
    'FEE_REBATE_MAX_RATIO': 0.5,
    # 上币奖励最高比例，最高可奖励50%
    'LISTING_REWARD_MAX_RATIO': 0.5,
    # U卡价值，每张U卡价值100美元
    'U_CARD_VALUE': 100
}

# 区块链网络配置
BLOCKCHAIN_CONFIG = {
    'ETH': {
        'CHAIN_ID': 1,
        'NAME': 'Ethereum',
        'SYMBOL': 'ETH',
        'RPC_URLS': [
            'https://eth.llamarpc.com',
            'https://rpc.ankr.com/eth',
            f'https://eth-mainnet.g.alchemy.com/v2/{os.getenv("ALCHEMY_API_KEY", "")}'
        ],
        'EXPLORER_URL': 'https://etherscan.io',
        'GAS_PRICE_GWEI': 20,
        'CONTRACT_ADDRESS': os.getenv('ETH_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000'),
        'NATIVE_DECIMALS': 18
    },
    'BSC': {
        'CHAIN_ID': 56,
        'NAME': 'Binance Smart Chain',
        'SYMBOL': 'BNB',
        'RPC_URLS': [
            'https://bsc-dataseed.binance.org',
            'https://bsc-dataseed1.defibit.io',
            'https://bsc-dataseed1.ninicoin.io'
        ],
        'EXPLORER_URL': 'https://bscscan.com',
        'GAS_PRICE_GWEI': 5,
        'CONTRACT_ADDRESS': os.getenv('BSC_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000'),
        'NATIVE_DECIMALS': 18
    },
    'BSC_TESTNET': {
        'CHAIN_ID': 97,
        'NAME': 'Binance Smart Chain Testnet',
        'SYMBOL': 'tBNB',
        'RPC_URLS': [
            'https://rpc.ankr.com/bsc_testnet_chapel',
            'https://bsc-testnet.blockpi.network/v1/rpc/public',
            'https://endpoints.omniatech.io/v1/bsc/testnet/public',
            'https://data-seed-prebsc-1-s1.binance.org:8545'
        ],
        'EXPLORER_URL': 'https://testnet.bscscan.com',
        'GAS_PRICE_GWEI': 5,
        'CONTRACT_ADDRESS': os.getenv('BSC_TESTNET_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000'),
        'NATIVE_DECIMALS': 18
    },
    'POLYGON': {
        'CHAIN_ID': 137,
        'NAME': 'Polygon',
        'SYMBOL': 'MATIC',
        'RPC_URLS': [
            'https://polygon-rpc.com',
            'https://rpc.ankr.com/polygon',
            f'https://polygon-mainnet.g.alchemy.com/v2/{os.getenv("ALCHEMY_API_KEY", "")}'
        ],
        'EXPLORER_URL': 'https://polygonscan.com',
        'GAS_PRICE_GWEI': 30,
        'CONTRACT_ADDRESS': os.getenv('POLYGON_CONTRACT_ADDRESS', '0x0000000000000000000000000000000000000000'),
        'NATIVE_DECIMALS': 18
    },
    'SOLANA': {
        'CHAIN_ID': 'solana',
        'NAME': 'Solana',
        'SYMBOL': 'SOL',
        'RPC_URLS': [
            'https://api.mainnet-beta.solana.com',
            'https://solana-api.projectserum.com',
            'https://rpc.ankr.com/solana'
        ],
        'EXPLORER_URL': 'https://explorer.solana.com',
        'CONTRACT_ADDRESS': os.getenv('SOLANA_CONTRACT_ADDRESS', '11111111111111111111111111111111'),
        'NATIVE_DECIMALS': 9
    }
}

DEFAULT_CHAIN = os.getenv('DEFAULT_CHAIN', 'BSC_TESTNET')

WALLET_CONFIG = {
    'PRIVATE_KEY': os.getenv('PRIVATE_KEY', ''),
    'ADDRESS': os.getenv('WALLET_ADDRESS', ''),
    'SOLANA_PRIVATE_KEY': os.getenv('SOLANA_PRIVATE_KEY', ''),
    'SOLANA_ADDRESS': os.getenv('SOLANA_ADDRESS', '')
}

DEMO_MODE = os.getenv('DEMO_MODE', 'false').lower() == 'true'
