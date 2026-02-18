#!/usr/bin/env python3
# 简单的BSC测试网测试

from config.mining_config import DEFAULT_CHAIN, BLOCKCHAIN_CONFIG

print("当前配置:")
print(f"默认链: {DEFAULT_CHAIN}")
print()

if DEFAULT_CHAIN in BLOCKCHAIN_CONFIG:
    config = BLOCKCHAIN_CONFIG[DEFAULT_CHAIN]
    print(f"链名称: {config['NAME']}")
    print(f"Chain ID: {config['CHAIN_ID']}")
    print(f"代币符号: {config['SYMBOL']}")
    print(f"区块浏览器: {config['EXPLORER_URL']}")
    print()
    print("RPC节点:")
    for i, rpc_url in enumerate(config['RPC_URLS'], 1):
        print(f"  {i}. {rpc_url}")
else:
    print(f"错误: 找不到 {DEFAULT_CHAIN} 配置")