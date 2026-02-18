# BitUP 区块链挖矿系统配置指南

## 概述

本系统支持两种运行模式：
- **演示模式**：使用模拟数据，无需真实钱包和合约
- **生产模式**：使用真实的区块链钱包和智能合约

## 快速开始

### 1. 安装依赖

```bash
pip3 install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
pip3 install web3 eth-account python-dotenv
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org solders
```

注意：
1. 由于SSL证书问题，所有pip命令都需要添加 `--trusted-host` 参数
2. Solana Python SDK已更新为`solders`，这是官方推荐的新一代SDK
3. 建议先升级pip到最新版本以获得更好的兼容性

### 2. 配置环境变量

复制环境变量模板文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入真实的配置信息。

### 3. 运行系统

```bash
python3 blockchain_main.py
```

## 详细配置说明

### 钱包配置

#### 获取钱包私钥和地址

**EVM兼容链（ETH、BSC、Polygon）：**

1. 使用 MetaMask 或其他钱包创建账户
2. 导出私钥（注意：私钥非常重要，请妥善保管）
3. 复制钱包地址

**Solana：**

1. 使用 Phantom 或 Solflare 钱包创建账户
2. 导出私钥（注意：Solana使用的是Base58编码的私钥）
3. 复制钱包地址

**配置示例：**

```env
# EVM链（ETH、BSC、POLYGON）使用十六进制私钥
PRIVATE_KEY=0x1234567890abcdef...

# Solana使用Base58编码的私钥（如果需要单独配置）
SOLANA_PRIVATE_KEY=你的Solana私钥

# 钱包地址
WALLET_ADDRESS=0x1234567890abcdef...（EVM链）
SOLANA_ADDRESS=你的Solana地址（Solana链）
```

### 智能合约地址配置

#### 部署智能合约

在配置真实合约地址之前，你需要先部署智能合约到目标区块链网络。

**EVM智能合约部署步骤：**

1. 编写智能合约（Solidity）
2. 使用 Hardhat 或 Truffle 编译合约
3. 部署到目标网络（需要支付Gas费用）
4. 获取部署后的合约地址

**Solana程序部署步骤：**

1. 编写智能合约（Rust）
2. 使用 Solana CLI 编译程序
3. 部署到 Solana 主网
4. 获取程序ID

**配置示例：**

```env
# 以太坊挖矿合约地址
ETH_CONTRACT_ADDRESS=0x1234567890abcdef...

# BSC挖矿合约地址
BSC_CONTRACT_ADDRESS=0x1234567890abcdef...

# Polygon挖矿合约地址
POLYGON_CONTRACT_ADDRESS=0x1234567890abcdef...

# Solana挖矿程序ID
SOLANA_CONTRACT_ADDRESS=11111111111111111111111111111111
```

### API密钥配置（可选）

为了获得更好的RPC服务，可以配置API密钥：

#### Alchemy API密钥

1. 访问 https://www.alchemy.com/
2. 注册账户
3. 创建应用，获取API密钥

#### Infura API密钥

1. 访问 https://infura.io/
2. 注册账户
3. 创建项目，获取API密钥

**配置示例：**

```env
ALCHEMY_API_KEY=your_alchemy_api_key_here
INFURA_API_KEY=your_infura_api_key_here
```

### 网络配置

选择默认使用的区块链网络：

```env
DEFAULT_CHAIN=BSC
```

可选值：`ETH`、`BSC`、`POLYGON`、`SOLANA`

### 模式配置

设置运行模式：

```env
# 生产模式 - 使用真实链上数据
DEMO_MODE=false

# 演示模式 - 使用模拟数据
DEMO_MODE=true
```

## 模式切换

### 从演示模式切换到生产模式

1. 确保 `.env` 文件中配置了真实的私钥和钱包地址
2. 确保配置了真实的智能合约地址
3. 设置 `DEMO_MODE=false`
4. 重启系统

### 从生产模式切换到演示模式

1. 设置 `DEMO_MODE=true`
2. 重启系统

## 安全注意事项

1. **私钥安全**：
   - 永远不要将私钥提交到代码仓库
   - `.env` 文件已添加到 `.gitignore`
   - 定期备份私钥到安全的地方

2. **合约安全**：
   - 在部署前充分测试智能合约
   - 进行代码审计
   - 使用经过验证的合约代码

3. **API密钥安全**：
   - 不要公开分享API密钥
   - 定期轮换API密钥
   - 设置API密钥的使用限制

## 测试连接

配置完成后，运行系统测试连接：

```bash
python3 blockchain_main.py
```

系统会显示：
- 当前运行模式（演示模式或生产模式）
- 各区块链网络的连接状态
- 钱包余额
- 网络状态信息

## 常见问题

### Q: 如何获取测试网络代币？

A: 可以从以下水龙头获取测试代币：
- ETH: https://faucet.quicknode.com/ethereum
- BSC: https://testnet.bnbchain.org/faucet-smart
- Polygon: https://faucet.polygon.technology/
- Solana: https://faucet.solana.com/

### Q: Gas费用不足怎么办？

A: 确保钱包中有足够的原生代币来支付交易费用：
- ETH: 需要ETH
- BSC: 需要BNB
- Polygon: 需要MATIC
- Solana: 需要SOL

### Q: 如何查看交易记录？

A: 使用对应的区块链浏览器：
- ETH: https://etherscan.io
- BSC: https://bscscan.com
- Polygon: https://polygonscan.com
- Solana: https://explorer.solana.com

### Q: Solana SDK无法安装怎么办？

A: 由于网络问题，solana-py可能无法安装。系统已更新为使用solders（新一代Solana SDK），安装命令：

```bash
pip3 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org solders
```

如果仍有问题，可以暂时跳过Solana功能，系统会自动使用演示模式。

### Q: pip升级时出现SSL证书验证错误怎么办？

A: 这是常见的网络连接问题。解决方法：

```bash
pip3 install --upgrade pip --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
```

建议在安装所有Python包时都添加 `--trusted-host` 参数以避免SSL证书问题。

## 技术支持

如有问题，请联系技术支持团队。