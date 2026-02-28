const hre = require("hardhat");
const fs = require('fs');
const path = require('path');

async function main() {
  console.log("开始部署挖矿合约到BSC测试网...");
  
  // 获取部署账户
  const [deployer] = await hre.ethers.getSigners();
  console.log("部署账户:", deployer.address);
  
  // 获取账户余额
  const balance = await deployer.getBalance();
  console.log("账户余额:", hre.ethers.utils.formatEther(balance), "tBNB");
  
  // 部署合约
  const MiningContract = await hre.ethers.getContractFactory("MiningContract");
  const miningContract = await MiningContract.deploy();
  
  await miningContract.deployed();
  
  console.log("合约部署成功!");
  console.log("合约地址:", miningContract.address);
  console.log("交易哈希:", miningContract.deployTransaction.hash);
  
  // 保存部署信息
  const deploymentInfo = {
    network: "bscTestnet",
    chainId: 97,
    contractAddress: miningContract.address,
    deployerAddress: deployer.address,
    transactionHash: miningContract.deployTransaction.hash,
    timestamp: new Date().toISOString()
  };
  
  // 保存到文件
  const deploymentPath = path.join(__dirname, '../deployment-info.json');
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("部署信息已保存到:", deploymentPath);
  
  // 更新.env文件
  const envPath = path.join(__dirname, '../.env');
  let envContent = '';
  
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, 'utf8');
    // 更新或添加合约地址
    if (envContent.includes('BSC_TESTNET_CONTRACT_ADDRESS=')) {
      envContent = envContent.replace(
        /BSC_TESTNET_CONTRACT_ADDRESS=.*/,
        `BSC_TESTNET_CONTRACT_ADDRESS=${miningContract.address}`
      );
    } else {
      envContent += `\nBSC_TESTNET_CONTRACT_ADDRESS=${miningContract.address}\n`;
    }
  } else {
    envContent = `# BSC测试网合约地址\nBSC_TESTNET_CONTRACT_ADDRESS=${miningContract.address}\n`;
  }
  
  fs.writeFileSync(envPath, envContent);
  console.log("合约地址已更新到.env文件");
  
  // 验证合约（可选）
  console.log("\n等待区块确认...");
  await miningContract.deployTransaction.wait(5);
  
  console.log("\n部署完成!");
  console.log("合约地址:", miningContract.address);
  console.log("区块浏览器:", `https://testnet.bscscan.com/address/${miningContract.address}`);
  
  return miningContract.address;
}

main()
  .then((address) => {
    console.log("\n✅ 部署成功!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ 部署失败:", error);
    process.exit(1);
  });