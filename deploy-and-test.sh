#!/bin/bash

# BSC测试网自动部署和测试脚本
# 使用方法: ./deploy-and-test.sh

set -e

echo "=================================="
echo "BitUP BSC测试网自动部署和测试"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 错误: Node.js未安装${NC}"
    echo "请先安装Node.js: https://nodejs.org/"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ 错误: npm未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js和npm已安装${NC}"
echo ""

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env文件不存在，从.env.example创建...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  请编辑.env文件，设置你的私钥和钱包地址${NC}"
    exit 1
fi

# 检查私钥是否设置
if grep -q "PRIVATE_KEY=your_private_key_here" .env; then
    echo -e "${RED}❌ 错误: 请在.env文件中设置PRIVATE_KEY${NC}"
    echo "请使用BSC测试网钱包的私钥"
    exit 1
fi

# 检查钱包地址是否设置
if grep -q "WALLET_ADDRESS=your_wallet_address_here" .env; then
    echo -e "${RED}❌ 错误: 请在.env文件中设置WALLET_ADDRESS${NC}"
    echo "请使用BSC测试网钱包地址"
    exit 1
fi

echo -e "${GREEN}✅ 环境变量配置检查通过${NC}"
echo ""

# 安装依赖
echo "📦 安装依赖..."
npm install
echo -e "${GREEN}✅ 依赖安装完成${NC}"
echo ""

# 编译合约
echo "🔨 编译智能合约..."
npx hardhat compile
echo -e "${GREEN}✅ 合约编译完成${NC}"
echo ""

# 部署合约到BSC测试网
echo "🚀 部署合约到BSC测试网..."
npx hardhat run scripts/deploy.js --network bscTestnet
echo -e "${GREEN}✅ 合约部署完成${NC}"
echo ""

# 等待几秒钟让区块确认
echo "⏳ 等待区块确认..."
sleep 10

# 测试合约
echo "🧪 测试合约功能..."
npx hardhat run scripts/test-contract.js --network bscTestnet
echo -e "${GREEN}✅ 合约测试完成${NC}"
echo ""

# 显示部署信息
echo "=================================="
echo "部署和测试完成!"
echo "=================================="
echo ""

if [ -f "deployment-info.json" ]; then
    echo "📄 部署信息:"
    cat deployment-info.json
    echo ""
fi

echo "🔗 区块浏览器链接:"
CONTRACT_ADDRESS=$(grep "BSC_TESTNET_CONTRACT_ADDRESS=" .env | cut -d'=' -f2)
echo "https://testnet.bscscan.com/address/${CONTRACT_ADDRESS}"
echo ""

echo -e "${GREEN}✅ 所有步骤完成!${NC}"
echo ""
echo "下一步:"
echo "1. 重启API服务以使用新的合约地址"
echo "2. 使用API接口进行测试"
echo ""
echo "购买节点示例:"
echo "curl -X POST http://localhost:5001/api/buy-nodes \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"uid\": \"123456\", \"node_count\": 1, \"payment_amount\": 500}'"