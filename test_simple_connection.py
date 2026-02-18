#!/usr/bin/env python3
# 简化的BSC测试网连接测试

from config.mining_config import BLOCKCHAIN_CONFIG, DEFAULT_CHAIN

def test_simple_connection():
    print("=" * 60)
    print("BSC测试网连接测试（简化版）")
    print("=" * 60)
    print()
    
    config = BLOCKCHAIN_CONFIG[DEFAULT_CHAIN]
    print(f"默认链: {DEFAULT_CHAIN}")
    print(f"链名称: {config['NAME']}")
    print(f"Chain ID: {config['CHAIN_ID']}")
    print(f"代币符号: {config['SYMBOL']}")
    print(f"区块浏览器: {config['EXPLORER_URL']}")
    print()
    
    try:
        from web3 import Web3
        import requests
        
        print("测试RPC节点连接...")
        success = False
        
        for i, rpc_url in enumerate(config['RPC_URLS'], 1):
            print(f"  测试节点 {i}: {rpc_url}")
            
            try:
                # 使用简单的RPC调用测试连接
                response = requests.post(
                    rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "method": "eth_chainId",
                        "params": [],
                        "id": 1
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'result' in result:
                        chain_id = result['result']
                        print(f"  ✓ 连接成功！Chain ID: {chain_id}")
                        success = True
                        break
                else:
                    print(f"  ✗ 响应格式错误")
            except Exception as e:
                print(f"  ✗ 连接失败: {str(e)[:100]}")
        
        print()
        if success:
            print("✓ BSC测试网连接测试通过！")
            print()
            print("配置信息:")
            print(f"  网络: {config['NAME']}")
            print(f"  Chain ID: {config['CHAIN_ID']}")
            print(f"  代币: {config['SYMBOL']}")
            print(f"  浏览器: {config['EXPLORER_URL']}")
            print()
            print("下一步:")
            print("1. 在 .env 文件中配置测试网钱包")
            print("2. 访问水龙头获取测试代币")
            print("3. 运行 python3 blockchain_main.py 进行完整测试")
            return True
        else:
            print("✗ BSC测试网连接测试失败")
            print()
            print("请检查:")
            print("1. 网络连接是否正常")
            print("2. RPC节点是否可访问")
            print("3. 防火墙是否阻止了连接")
            return False
            
    except ImportError:
        print("✗ web3库未安装")
        print("请运行: pip3 install web3")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_simple_connection()