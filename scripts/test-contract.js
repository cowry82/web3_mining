const hre = require("hardhat");
require('dotenv').config();

async function main() {
  console.log("开始测试BSC测试网合约...\n");
  
  // 获取合约地址
  const contractAddress = process.env.BSC_TESTNET_CONTRACT_ADDRESS;
  
  if (!contractAddress || contractAddress === '0x0000000000000000000000000000000000000000') {
    console.error("❌ 错误: 请先在.env文件中设置BSC_TESTNET_CONTRACT_ADDRESS");
    console.log("请先运行部署脚本: npx hardhat run scripts/deploy.js --network bscTestnet");
    process.exit(1);
  }
  
  console.log("合约地址:", contractAddress);
  
  // 获取测试账户
  const [tester] = await hre.ethers.getSigners();
  console.log("测试账户:", tester.address);
  
  // 获取合约实例
  const MiningContract = await hre.ethers.getContractFactory("MiningContract");
  const miningContract = MiningContract.attach(contractAddress);
  
  console.log("\n" + "=".repeat(60));
  console.log("开始测试合约功能");
  console.log("=".repeat(60) + "\n");
  
  // 测试1: 获取全网统计
  console.log("📊 测试1: 获取全网统计");
  try {
    const stats = await miningContract.getNetworkStats();
    console.log("  全网节点数:", stats[0].toString());
    console.log("  全网总算力:", stats[1].toString(), "T");
    console.log("  每日产出:", hre.ethers.utils.formatEther(stats[2]), "代币");
    console.log("  ✅ 测试通过\n");
  } catch (error) {
    console.log("  ❌ 测试失败:", error.message, "\n");
  }
  
  // 测试2: 购买节点
  console.log("🛒 测试2: 购买节点");
  try {
    const nodeCount = 2;
    const price = await miningContract.NODE_PRICE();
    const totalPrice = price.mul(nodeCount);
    
    console.log("  购买数量:", nodeCount, "个节点");
    console.log("  节点单价:", hre.ethers.utils.formatEther(price), "tBNB");
    console.log("  总价格:", hre.ethers.utils.formatEther(totalPrice), "tBNB");
    
    const tx = await miningContract.buyNode(nodeCount, {
      value: totalPrice,
      gasLimit: 300000
    });
    
    console.log("  交易已发送，等待确认...");
    const receipt = await tx.wait();
    console.log("  交易哈希:", receipt.transactionHash);
    console.log("  Gas使用:", receipt.gasUsed.toString());
    console.log("  ✅ 购买成功\n");
  } catch (error) {
    console.log("  ❌ 购买失败:", error.message, "\n");
  }
  
  // 测试3: 获取用户节点
  console.log("📋 测试3: 获取用户节点");
  try {
    const nodeCount = await miningContract.getUserNodeCount(tester.address);
    console.log("  用户节点数:", nodeCount.toString());
    
    if (nodeCount > 0) {
      const nodes = await miningContract.getUserNodes(tester.address);
      console.log("  节点详情:");
      nodes.forEach((node, index) => {
        console.log(`    节点${index + 1}:`);
        console.log(`      ID: ${node.nodeId.toString()}`);
        console.log(`      算力: ${node.hashrate.toString()} T`);
        console.log(`      购买时间: ${new Date(node.purchaseTime * 1000).toLocaleString()}`);
        console.log(`      状态: ${node.active ? '激活' : '未激活'}`);
      });
    }
    console.log("  ✅ 测试通过\n");
  } catch (error) {
    console.log("  ❌ 测试失败:", error.message, "\n");
  }
  
  // 测试4: 获取用户总算力
  console.log("⚡ 测试4: 获取用户总算力");
  try {
    const hashrate = await miningContract.getUserHashrate(tester.address);
    console.log("  用户总算力:", hashrate.toString(), "T");
    console.log("  ✅ 测试通过\n");
  } catch (error) {
    console.log("  ❌ 测试失败:", error.message, "\n");
  }
  
  // 测试5: 计算每日产出
  console.log("💰 测试5: 计算每日产出");
  try {
    const dailyOutput = await miningContract.calculateDailyOutput(tester.address);
    console.log("  用户每日产出:", hre.ethers.utils.formatEther(dailyOutput), "代币");
    console.log("  ✅ 测试通过\n");
  } catch (error) {
    console.log("  ❌ 测试失败:", error.message, "\n");
  }
  
  // 测试6: 再次获取全网统计（查看变化）
  console.log("📊 测试6: 再次获取全网统计");
  try {
    const stats = await miningContract.getNetworkStats();
    console.log("  全网节点数:", stats[0].toString());
    console.log("  全网总算力:", stats[1].toString(), "T");
    console.log("  每日产出:", hre.ethers.utils.formatEther(stats[2]), "代币");
    console.log("  ✅ 测试通过\n");
  } catch (error) {
    console.log("  ❌ 测试失败:", error.message, "\n");
  }
  
  console.log("=".repeat(60));
  console.log("测试完成!");
  console.log("=".repeat(60));
  console.log("\n区块浏览器链接:");
  console.log(`https://testnet.bscscan.com/address/${contractAddress}`);
}

main()
  .then(() => {
    console.log("\n✅ 所有测试完成!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ 测试失败:", error);
    process.exit(1);
  });