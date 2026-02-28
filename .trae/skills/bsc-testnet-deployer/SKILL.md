---
name: "bsc-testnet-deployer"
description: "Deploys and tests smart contracts on BSC testnet. Invoke when user wants to deploy contracts to BSC testnet or perform automated testing on testnet."
---

# BSC Testnet Deployer

This skill helps deploy smart contracts to BSC testnet and perform automated testing.

## Capabilities

1. Deploy Solidity smart contracts to BSC testnet
2. Configure Hardhat for BSC testnet deployment
3. Update contract addresses in configuration files
4. Perform automated testing on deployed contracts
5. Verify contracts on BSC testnet explorer

## Prerequisites

- Node.js and npm installed
- BSC testnet wallet with tBNB
- Hardhat configuration

## Usage

### 1. Deploy Contract

```bash
npx hardhat run scripts/deploy.js --network bscTestnet
```

### 2. Update Configuration

After deployment, update:
- `.env` file with new contract address
- `config/mining_config.py` with new contract address

### 3. Test Contract

Run automated tests on the deployed contract.

## Network Details

- **Network**: Binance Smart Chain Testnet
- **Chain ID**: 97
- **RPC URL**: https://data-seed-prebsc-1-s1.binance.org:8545
- **Explorer**: https://testnet.bscscan.com
- **Faucet**: https://testnet.bnbchain.org/faucet-smart