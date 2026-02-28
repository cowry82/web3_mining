# BitUP 区块链挖矿系统

## 项目简介

这是一个支持多条公链的真实挖矿系统，集成了区块链交互、智能合约调用、钱包管理等功能。

## 支持的区块链

- **Binance Smart Chain (BSC)** - 币安智能链

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
├── buy_nodes_api.py               # 购买节点API
├── requirements.txt               # 依赖包
└── .env                           # 环境变量配置
```

## 配置说明

### 1. 安装依赖

```bash
pip3 install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
pip3 install web3 eth-account python-dotenv
```

### 2. 配置环境变量

编辑 `.env` 文件：

```env
# 钱包配置
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=your_wallet_address_here

# 智能合约地址
BSC_CONTRACT_ADDRESS=0x0000000000000000000000000000000000000000

# 网络配置
DEFAULT_CHAIN=BSC

# 运行模式
DEMO_MODE=false
```

### 3. 区块链配置

编辑 `config/mining_config.py` 文件：

```python
BLOCKCHAIN_CONFIG = {
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
    }
}

DEFAULT_CHAIN = os.getenv('DEFAULT_CHAIN', 'BSC')
```

## API接口

### 1. 购买节点接口

**URL**: `POST /api/buy-nodes`

**请求参数**:
- `uid`: 用户ID
- `node_count`: 节点数量
- `payment_amount`: 支付金额（USDT）

**返回结果**:
- `success`: 是否成功
- `tx_hash`: 交易哈希（如果成功）
- `message`: 提示信息
- `node_info`: 节点信息

**示例请求**:
```bash
curl -X POST http://localhost:5001/api/buy-nodes \
  -H 'Content-Type: application/json' \
  -d '{"uid": "123456", "node_count": 1, "payment_amount": 500}'
```

### 2. 获取节点详情接口

**URL**: `GET /api/node-details/<uid>`

**请求参数**:
- `uid`: 用户ID（路径参数）

**返回结果**:
- `success`: 是否成功
- `node_details`: 节点详情列表

**示例请求**:
```bash
curl http://localhost:5001/api/node-details/123456
```

**节点详情字段**:
- `node_id`: 节点ID
- `hashrate`: 算力
- `xCPT_per_T`: xCPT/T
- `today_output`: 今日产出cpt
- `today_unlock`: 今日解锁代币CPT/T
- `duration`: 时长
- `unlocked_tokens`: 待解锁代币CPT
- `total_output`: 累计产出CPT
- `total_unlocked`: 累计解锁CPT

## 使用方法

### 1. 启动API服务

```bash
python3 buy_nodes_api.py
```

服务运行在: http://localhost:5001

### 2. 购买节点

使用上述API接口购买节点，系统会在BSC链上执行交易。

### 3. 查询节点详情

使用节点详情接口查询用户的节点信息，包括算力、产出等数据。

## 智能合约部署

### BSC智能合约 (Solidity)

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

## 注意事项

1. **安全性**
   - 永远不要泄露私钥
   - 在测试网络中先进行测试
   - 使用硬件钱包存储大额资产

2. **Gas费用**
   - BSC的Gas费用较低
   - 确保钱包有足够的Gas费用

3. **网络延迟**
   - 区块链交易需要确认时间
   - BSC的确认时间约为3-5秒

4. **合约部署**
   - 需要先部署智能合约到BSC
   - 更新配置文件中的合约地址
   - 测试合约功能是否正常

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