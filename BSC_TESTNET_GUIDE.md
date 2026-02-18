# BSC测试网使用指南

## 概述

BSC测试网（Binance Smart Chain Testnet）是币安智能链的测试网络，用于开发和调试。使用测试网可以：

- 免费获取测试代币
- 测试智能合约功能
- 调试交易流程
- 无需真实资金

## 网络信息

- **网络名称**: Binance Smart Chain Testnet
- **Chain ID**: 97
- **代币符号**: tBNB (测试BNB)
- **RPC端点**: 
  - https://data-seed-prebsc-1-s1.binance.org:8545
  - https://data-seed-prebsc-2-s1.binance.org:8545
  - https://data-seed-prebsc-1-s2.binance.org:8545
- **区块浏览器**: https://testnet.bscscan.com

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中设置：

```env
# 使用BSC测试网
DEFAULT_CHAIN=BSC_TESTNET

# BSC测试网合约地址
BSC_TESTNET_CONTRACT_ADDRESS=0x你的测试网合约地址
```

### 2. 代码配置

系统已自动配置BSC测试网支持，包括：
- Chain ID: 97
- RPC节点：测试网专用节点
- 区块浏览器：testnet.bscscan.com

## 获取测试代币

### 方法1: BSC测试网水龙头

访问 BSC测试网水龙头获取测试代币：

- **官方水龙头**: https://testnet.bnbchain.org/faucet-smart
- **备用水龙头**: https://testnet.bnbchain.org/faucet-smart

### 方法2: MetaMask配置

1. 打开MetaMask扩展
2. 点击网络选择器 → 添加网络
3. 填入以下信息：
   - **网络名称**: BSC Testnet
   - **新的RPC URL**: https://data-seed-prebsc-1-s1.binance.org:8545
   - **链ID**: 97
   - **货币符号**: tBNB
   - **区块浏览器URL**: https://testnet.bscscan.com
4. 保存网络

### 方法3: 获取测试私钥

创建测试钱包：

```python
from eth_account import Account

# 创建测试账户
account = Account.create()
print(f"私钥: {account.key.hex()}")
print(f"地址: {account.address}")
```

## 部署测试合约

### 1. 编写智能合约

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MiningContract {
    mapping(address => uint256) public nodeCount;
    mapping(address => uint256) public rewards;
    
    function buyNode(uint256 count) external payable {
        require(msg.value >= count * 0.01 ether, "Insufficient payment");
        nodeCount[msg.sender] += count;
    }
    
    function claimRewards() external {
        uint256 reward = rewards[msg.sender];
        require(reward > 0, "No rewards to claim");
        rewards[msg.sender] = 0;
        payable(msg.sender).transfer(reward);
    }
}
```

### 2. 使用Hardhat部署

```javascript
// hardhat.config.js
module.exports = {
  solidity: "0.8.0",
  networks: {
    bscTestnet: {
      url: "https://data-seed-prebsc-1-s1.binance.org:8545",
      chainId: 97,
      gasPrice: 5000000000,
      accounts: ["你的私钥"]
    }
  }
};
```

```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network bscTestnet
```

### 3. 使用Truffle部署

```javascript
// truffle-config.js
module.exports = {
  networks: {
    bscTestnet: {
      host: "https://data-seed-prebsc-1-s1.binance.org:8545",
      port: 8545,
      network_id: "97",
      gas: 5500000,
      gasPrice: 5000000000,
      from: "你的钱包地址"
    }
  }
};
```

```bash
truffle compile
truffle migrate --network bscTestnet
```

## 测试流程

### 1. 连接测试网

```python
from services.blockchain_mining_service import BlockchainMiningService
from datetime import datetime

# 初始化服务（自动使用BSC测试网）
mining_service = BlockchainMiningService(datetime.now())

# 检查当前网络
print(f"当前网络: {mining_service.get_current_chain()}")
```

### 2. 测试购买节点

```python
# 在测试网上购买节点
tx_hash = mining_service.buy_nodes_on_chain(
    uid="test_user_001",
    node_count=2,
    payment_amount=0.02  # 0.02 tBNB
)

if tx_hash:
    print(f"✓ 购买成功，交易哈希: {tx_hash}")
    print(f"查看交易: https://testnet.bscscan.com/tx/{tx_hash}")
```

### 3. 测试领取奖励

```python
# 在测试网上领取奖励
tx_hash = mining_service.claim_rewards_on_chain("test_user_001")

if tx_hash:
    print(f"✓ 领取成功，交易哈希: {tx_hash}")
    print(f"查看交易: https://testnet.bscscan.com/tx/{tx_hash}")
```

### 4. 查询测试网余额

```python
# 获取测试网钱包余额
balance = mining_service.get_wallet_balance()
print(f"测试网余额: {balance} tBNB")
```

## 调试技巧

### 1. 查看交易详情

在测试网区块浏览器查看交易：
- 访问 https://testnet.bscscan.com
- 输入交易哈希或钱包地址
- 查看交易状态、Gas使用情况等

### 2. 检查合约状态

```python
# 检查合约是否部署成功
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545'))
code = w3.eth.get_code('你的合约地址')

if code != '0x':
    print("✓ 合约已部署")
else:
    print("✗ 合约未部署")
```

### 3. 测试Gas费用

```python
# 估算Gas费用
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://data-seed-prebsc-1-s1.binance.org:8545'))

# 估算交易Gas
gas_estimate = w3.eth.estimate_gas({
    'to': '合约地址',
    'from': '你的地址',
    'data': '交易数据'
})

gas_price = w3.eth.gas_price
total_cost = gas_estimate * gas_price

print(f"预估Gas: {gas_estimate}")
print(f"Gas价格: {gas_price}")
print(f"总费用: {w3.from_wei(total_cost, 'ether')} tBNB")
```

## 常见问题

### Q: 测试网代币用完了怎么办？

A: 重新访问水龙头获取测试代币。测试网代币是免费的，可以多次获取。

### Q: 测试网交易失败怎么办？

A: 检查以下几点：
1. 钱包是否有足够的测试代币
2. 合约地址是否正确
3. Gas费用是否足够
4. 查看testnet.bscscan.com了解错误详情

### Q: 如何从测试网切换到主网？

A: 修改 `.env` 文件：

```env
# 切换到BSC主网
DEFAULT_CHAIN=BSC

# 使用主网合约地址
BSC_CONTRACT_ADDRESS=0x你的主网合约地址
```

### Q: 测试网和主网有什么区别？

A: 主要区别：
- **测试网**: 免费测试，代币无价值，Chain ID 97
- **主网**: 真实资金，代币有真实价值，Chain ID 56

## 最佳实践

1. **开发阶段**: 使用测试网进行开发和测试
2. **测试阶段**: 在测试网充分测试所有功能
3. **部署阶段**: 确认无误后部署到主网
4. **监控阶段**: 主网部署后密切监控交易和合约状态

## 技术支持

如有问题，请访问：
- BSC测试网文档: https://docs.bnbchain.org/docs/testnet
- BSC社区: https://community.bnbchain.org/