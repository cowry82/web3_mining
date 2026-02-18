#!/usr/bin/env python3
# BSC测试网连接测试脚本

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.mining_config import BLOCKCHAIN_CONFIG, DEFAULT_CHAIN

def test_bsc_testnet_connection():
    print("=" * 60)
    print("BSC测试网连接测试")
    print("=" * 60)
    print()
    
    # 检查默认链
    print(f"默认链配置: {DEFAULT_CHAIN}")
    print()
    
    # 检查BSC测试网配置
    if 'BSC_TESTNET' in BLOCKCHAIN_CONFIG:
        config = BLOCKCHAIN_CONFIG['BSC_TESTNET']
        print("BSC测试网配置:")
        print(f"  名称: {config['NAME']}")
        print(f"  Chain ID: {config['CHAIN_ID']}")
        print(f"  代币符号: {config['SYMBOL']}")
        print(f"  区块浏览器: {config['EXPLORER_URL']}")
        print()
        print("RPC节点:")
        for i, rpc_url in enumerate(config['RPC_URLS'], 1):
            print(f"  {i}. {rpc_url}")
        print()
        
        # 测试RPC连接
        print("测试RPC连接...")
        import requests
        for i, rpc_url in enumerate(config['RPC_URLS'], 1):
            try:
                print(f"  测试节点 {i}: {rpc_url}...")
                response = requests.post(
                    rpc_url,
                    json={"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1},
                    timeout=10
                )
                if response.status_code == 200:
                    result = response.json()
                    if 'result' in result:
                        block_number = int(result['result'], 16)
                        print(f"  ✓ 连接成功！当前区块高度: {block_number}")
                        return True
            except Exception as e:
                print(f"  ✗ 连接失败: {e}")
        
        print()
        print("✗ 所有RPC节点连接失败")
        return False
    else:
        print("✗ BSC_TESTNET配置未找到")
        return False

if __name__ == "__main__":
    success = test_bsc_testnet_connection()
    print()
    if success:
        print("✓ BSC测试网连接测试通过")
        print()
        print("下一步:")
        print("1. 在 .env 文件中配置测试网钱包地址和私钥")
        print("2. 部署智能合约到BSC测试网")
        print("3. 运行 python3 blockchain_main.py 进行完整测试")
    else:
        print("✗ BSC测试网连接测试失败")
        print()
        print("请检查:")
        print("1. 网络连接是否正常")
        print("2. RPC节点是否可访问")
        print("3. 防火墙是否阻止了连接")