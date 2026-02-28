# BSC测试网智能合约部署指南

## 快速开始

### 1. 准备工作

确保你已经安装了：
- Node.js (v16或更高版本)
- npm
- Python 3 (用于运行API服务)

### 2. 配置钱包

编辑 `.env` 文件，设置你的BSC测试网钱包：

```bash
# 钱包配置（BSC测试网）
PRIVATE_KEY=0x你的测试网私钥
WALLET_ADDRESS=0x你的测试网钱包地址

# 网络配置
DEFAULT_CHAIN=BSC_TESTNET
DEMO_MODE=false
```

**获取测试网钱包：**
1. 使用MetaMask创建一个新的钱包
2. 切换到BSC测试网
3. 导出私钥（以0x开头）

**获取测试代币：**
1. 访问 https://testnet.bnbchain.org/faucet-smart
2. 输入你的测试网钱包地址
3. 获取测试BNB（tBNB）

### 3. 自动部署和测试

运行一键部署脚本：

```bash
chmod +x deploy-and-test.sh
./deploy-and-test.sh
```

这个脚本会自动：
1. 检查环境配置
2. 安装依赖
3. 编译智能合约
4. 部署到BSC测试网
5. 自动测试合约功能
6. 更新配置文件

### 4. 手动部署（可选）

如果你不想使用自动脚本，可以手动执行：

```bash
# 安装依赖
npm install

# 编译合约
npx hardhat compile

# 部署到BSC测试网
npx hardhat run scripts/deploy.js --network bscTestnet

# 测试合约
npx hardhat run scripts/test-contract.js --network bscTestnet
```

### 5. 验证部署

部署成功后，你会看到：
- 合约地址
- 交易哈希
- 区块浏览器链接

访问 https://testnet.bscscan.com 查看合约详情。

### 6. 重启API服务

部署完成后，重启API服务以使用新的合约地址：

```bash
# 停止现有服务
Ctrl+C

# 重新启动
python3 buy_nodes_api.py
```

### 7. 测试API接口

使用curl测试购买节点接口：

```bash
# 购买节点
curl -X POST http://localhost:5001/api/buy-nodes \
  -H 'Content-Type: application/json' \
  -d '{"uid": "123456", "node_count": 1, "payment_amount": 500}'

# 获取节点详情
curl http://localhost:5001/api/node-details/123456
```

## 项目结构

```
wakuang/
├── contracts/
│   └── MiningContract.sol      # 智能合约源码
├── scripts/
│   ├── deploy.js               # 部署脚本
│   └── test-contract.js        # 测试脚本
├── hardhat.config.js           # Hardhat配置
├── package.json                # Node.js依赖
├── deploy-and-test.sh          # 一键部署脚本
├── .env                        # 环境变量配置
└── DEPLOY_GUIDE.md             # 本指南
```

## 合约功能

### 核心功能

1. **购买节点**
   - 每个节点价格：0.01 tBNB
   - 每个节点算力：500 T
   - 支持批量购买

2. **查询功能**
   - 获取用户节点数量
   - 获取用户节点详情
   - 获取用户总算力
   - 获取全网统计
   - 计算每日产出

3. **奖励系统**
   - 分发奖励
   - 领取奖励
   - 查询待领取奖励

### 事件

- `NodePurchased`: 节点购买事件
- `RewardsClaimed`: 奖励领取事件
- `RewardsDistributed`: 奖励分发事件

## 常用命令

```bash
# 编译合约
npm run compile

# 部署到测试网
npm run deploy:testnet

# 测试合约
npm run test:contract

# 验证合约（需要BSCScan API密钥）
npm run verify:testnet -- 合约地址
```

## 故障排除

### 1. 部署失败

**问题**: "insufficient funds for gas"

**解决**: 你的测试网钱包没有足够的tBNB。访问水龙头获取测试代币。

### 2. 合约验证失败

**问题**: "Contract verification failed"

**解决**: 
- 确保合约代码与部署时完全一致
- 等待几个区块后再尝试验证
- 检查BSCScan API密钥是否正确

### 3. API连接失败

**问题**: "Failed to connect to BSC testnet"

**解决**:
- 检查网络连接
- 尝试使用其他RPC节点
- 检查防火墙设置

### 4. 交易失败

**问题**: 购买节点交易失败

**解决**:
- 确保钱包有足够的tBNB
- 检查Gas费用设置
- 查看交易详情了解失败原因

## 安全注意事项

1. **私钥安全**
   - 永远不要泄露私钥
   - 使用测试网钱包，不要与主网钱包混用
   - 定期更换测试网钱包

2. **合约安全**
   - 部署前充分测试合约
   - 使用经过审计的合约代码
   - 在生产环境使用前先在小金额测试

3. **资金安全**
   - 测试网代币没有价值，但不要滥用
   - 主网操作前务必仔细检查

## 技术支持

如有问题，请检查：
1. 环境配置是否正确
2. 依赖包是否完整安装
3. 网络连接是否正常
4. 钱包余额是否充足

## 下一步

部署成功后，你可以：
1. 使用API接口进行挖矿操作
2. 集成到前端应用
3. 添加更多功能到智能合约
4. 部署到BSC主网（需要真实资金）