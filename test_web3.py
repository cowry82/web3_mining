#!/usr/bin/env python3
# 测试BSC测试网Web3连接

from config.mining_config import BLOCKCHAIN_CONFIG, DEFAULT_CHAIN

def test_web3_connection():
    print("=" * 60)
    print("测试BSC测试网Web3连接")
    print("=" * 60)
    print()
    
    config = BLOCKCHAIN_CONFIG[DEFAULT_CHAIN]
    print(f"测试链: {config['NAME']}")
    print(f"Chain ID: {config['CHAIN_ID']}")
    print()
    
    try:
        from web3 import Web3
        
        # 测试每个RPC节点
        for i, rpc_url in enumerate(config['RPC_URLS'], 1):
            print(f"测试节点 {i}: {rpc_url}")
            
            try:
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # 检查连接
                if w3.is_connected():
                    print(f"  ✓ 连接成功")
                    
                    # 获取链ID
                    chain_id = w3.eth.chain_id
                    print(f"  ✓ Chain ID: {chain_id}")
                    
                    # 获取最新区块
                    latest_block = w3.eth.get_block('latest')
                    print(f"  ✓ 最新区块: {latest_block['number']}")
                    
                    # 获取Gas价格
                    gas_price = w3.eth.gas_price
                    print(f"  ✓ Gas价格: {gas_price} Gwei")
                    
                    print()
                    print("✓ BSC测试网连接测试通过！")
                    return True
                else:
                    print(f"  ✗ 连接失败")
                    
            except Exception as e:
                print(f"  ✗ 错误: {e}")
                print()
        
        print("✗ 所有RPC节点连接失败")
        return False
        
    except ImportError:
        print("✗ web3库未安装")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_web3_connection()
    print()
    if success:
        print("下一步:")
        print("1. 配置测试网钱包地址和私钥")
        print("2. 部署智能合约到BSC测试网")
        print("3. 运行完整测试: python3 blockchain_main.py")
    else:
        print("请检查:")
        print("1. web3库是否已安装")
        print("2. 网络连接是否正常")
        print("3. RPC节点是否可访问")