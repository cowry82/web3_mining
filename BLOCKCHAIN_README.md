# BitUP 区块链挖矿系统

## 项目简介

这是一个支持多条公链的真实挖矿系统，集成了区块链交互、智能合约调用、钱包管理等功能。

## 支持的区块链

- **Ethereum (ETH)** - 以太坊主网
- **Binance Smart Chain (BSC)** - 币安智能链
- **Polygon** - Polygon网络
- **Solana** - Solana网络

## 项目结构

```
wakuang/
├── config/                        # 配置层
│   ├── __init__.py
│   └── mining_config.py           # 挖矿参数 + 区块链配置
├── models/                        # 数据模型层
│   ├── __init__.py
│   └── models.py                  # 节点、用户、记录模型
├── core/                          # 核心计算层
│   ├── __init__.py
│   ├── calculator.py              # 挖矿、减产、奖励计算公式
│   ├── blockchain.py              # 区块链连接管理
│   ├── contract.py                # 智能合约接口
│   └── wallet.py                  # 钱包管理
├── services/                      # 业务服务层
│   ├── __init__.py
│   ├── mining_service.py          # 基础挖矿服务
│   ├── blockchain_mining_service.py # 区块链挖矿服务
│   └── transaction_manager.py     # 交易管理
├── utils/                         # 工具层
│   ├── __init__.py
│   └── time_utils.py              # 时间工具
├── main.py                        # 基础挖矿演示
├── blockchain_main.py             # 区块链挖矿演示
├── requirements.txt               # 依赖包
├── requirements.md                # 需求文档
└── README.md                      # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 区块链配置

编辑 `config/mining_config.py` 文件：

```python
BLOCKCHAIN_CONFIG = {
    'ETH': {
        'CHAIN_ID': 1,
        'NAME': 'Ethereum',
        'SYMBOL': 'ETH',
        'RPC_URLS': [
            'https://eth.llamarpc.com',
            'https://rpc.ankr.com/eth'
        ],
        'EXPLORER_URL': 'https://etherscan.io',
        'CONTRACT_ADDRESS': '0x...',  # 您的智能合约地址
        'NATIVE_DECIMALS': 18
    },
    # ... 其他链配置
}

DEFAULT_CHAIN = 'BSC'  # 默认使用的区块链
```

### 2. 钱包配置

```python
WALLET_CONFIG = {
    'PRIVATE_KEY': 'YOUR_PRIVATE_KEY_HERE',  # 您的私钥
    'ADDRESS': 'YOUR_WALLET_ADDRESS_HERE'    # 您的钱包地址
}
```

**安全提示**: 
- 永远不要将私钥提交到代码仓库
- 建议使用环境变量存储私钥
- 仅在测试网络中使用真实私钥

## 运行程序


### 区块链挖矿

```bash
python3 blockchain_main.py
```

## 核心功能

### 1. 多链支持

系统支持在ETH、BSC、Polygon、Solana之间切换：

```python
from services.blockchain_mining_service import BlockchainMiningService

mining_service = BlockchainMiningService(mining_start_date)

# 切换到以太坊
mining_service.switch_chain('ETH')

# 切换到BSC
mining_service.switch_chain('BSC')

# 切换到Polygon
mining_service.switch_chain('POLYGON')
```

### 2. 链上购买节点

```python
# 在链上购买节点
tx_hash = mining_service.buy_nodes_on_chain(
    uid="user_001",
    node_count=2,
    payment_amount=0.1  # 支付金额
)
```

### 3. 链上领取奖励

```python
# 领取挖矿奖励
tx_hash = mining_service.claim_rewards_on_chain("user_001")
```

### 4. 查询链上数据

```python
# 获取用户节点
nodes = mining_service.get_user_nodes_from_chain("user_001")

# 获取用户奖励
rewards = mining_service.get_user_rewards_from_chain("user_001")

# 获取网络状态
stats = mining_service.get_network_stats_from_chain()
```

### 5. 交易管理

```python
# 获取交易历史
transactions = mining_service.get_transaction_history(limit=100)

# 获取交易统计
stats = mining_service.get_transaction_statistics()
```

## 智能合约部署

### EVM链智能合约 (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract BitUPMining {
    uint256 public constant BASE_HASHRATE = 500;
    uint256 public constant NODE_PRICE = 0.1 ether;
    
    struct Node {
        uint256 nodeId;
        uint256 hashrate;
        address owner;
        bool active;
    }
    
    mapping(address => Node[]) public userNodes;
    mapping(address => uint256) public userRewards;
    
    uint256 public totalNodes;
    uint256 public totalHashrate;
    
    function buyNode(uint256 nodeCount) public payable {
        require(msg.value >= nodeCount * NODE_PRICE, "Insufficient payment");
        
        for (uint256 i = 0; i < nodeCount; i++) {
            userNodes[msg.sender].push(Node({
                nodeId: totalNodes,
                hashrate: BASE_HASHRATE,
                owner: msg.sender,
                active: true
            }));
            totalNodes++;
            totalHashrate += BASE_HASHRATE;
        }
    }
    
    function claimRewards() public {
        uint256 rewards = userRewards[msg.sender];
        require(rewards > 0, "No rewards to claim");
        
        userRewards[msg.sender] = 0;
        payable(msg.sender).transfer(rewards);
    }
    
    function getUserNodes(address user) public view returns (uint256[] memory, uint256[] memory) {
        Node[] memory nodes = userNodes[user];
        uint256[] memory nodeIds = new uint256[](nodes.length);
        uint256[] memory hashrates = new uint256[](nodes.length);
        
        for (uint256 i = 0; i < nodes.length; i++) {
            nodeIds[i] = nodes[i].nodeId;
            hashrates[i] = nodes[i].hashrate;
        }
        
        return (nodeIds, hashrates);
    }
    
    function getUserRewards(address user) public view returns (uint256) {
        return userRewards[user];
    }
    
    function getNetworkStats() public view returns (uint256, uint256, uint256) {
        return (totalNodes, totalHashrate, 0);
    }
}
```

### Solana智能合约 (Rust)

需要使用Solana Program Library (SPL) 开发。

## 核心计算公式

### 1. 头矿期产出
```
单节点日产出 = 节点算力 × 产出速率
```

### 2. 常规期产出
```
个人日产出 = (个人算力 / 全网算力) × (全网日产量 × 80%)
```

### 3. 代币释放
```
立即释放 = 总产出 × 80%
线性释放 = 总产出 × 20%
每日线性释放 = 线性释放总额 / 10天
```

### 4. 减产机制
```
当前日产量 = 初始日产量 / (2 ^ 减产次数)
减产次数 = 经过的天数 / 1460天
```

## 使用示例

### 完整挖矿流程

```python
from datetime import datetime
from services.blockchain_mining_service import BlockchainMiningService
from models.models import User, Node

# 初始化服务
mining_service = BlockchainMiningService(datetime(2024, 1, 1))

# 创建用户
user = User(uid="user_001", nodes=[])

# 注册用户
mining_service.register_user(user)

# 购买节点（链上）
tx_hash = mining_service.buy_nodes_on_chain(
    uid="user_001",
    node_count=5,
    payment_amount=0.5
)

# 计算每日收益
records = mining_service.distribute_daily_rewards(datetime.now())

# 领取奖励（链上）
claim_tx = mining_service.claim_rewards_on_chain("user_001")

# 查看交易历史
transactions = mining_service.get_transaction_history()
```

## 注意事项

1. **安全性**
   - 永远不要泄露私钥
   - 在测试网络中先进行测试
   - 使用硬件钱包存储大额资产

2. **Gas费用**
   - 不同链的Gas费用不同
   - BSC和Polygon的Gas费用较低
   - 确保钱包有足够的Gas费用

3. **网络延迟**
   - 区块链交易需要确认时间
   - 不同链的确认时间不同
   - Solana的确认速度最快

4. **合约部署**
   - 需要先部署智能合约到目标链
   - 更新配置文件中的合约地址
   - 测试合约功能是否正常

## 扩展开发

### 添加新的区块链

1. 在 `config/mining_config.py` 中添加新链配置
2. 在 `core/blockchain.py` 中实现连接类
3. 在 `core/contract.py` 中实现合约接口
4. 在 `core/wallet.py` 中实现钱包类

### 添加新的计算公式

在 `core/calculator.py` 中添加新的计算方法。

### 添加新的业务逻辑

在 `services/` 目录下创建新的服务类。

## 故障排除

### 连接失败

- 检查RPC URL是否正确
- 检查网络连接
- 尝试使用备用RPC节点

### 交易失败

- 检查Gas费用是否足够
- 检查合约地址是否正确
- 检查钱包余额是否充足

### 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 技术支持

如有问题，请检查：
1. 配置文件是否正确
2. 依赖包是否完整安装
3. 网络连接是否正常
4. 钱包余额是否充足

## 许可证

本项目仅供学习和研究使用。
