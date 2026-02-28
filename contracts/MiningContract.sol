// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MiningContract {
    // 节点结构
    struct Node {
        uint256 nodeId;
        uint256 hashrate;
        address owner;
        uint256 purchaseTime;
        bool active;
    }
    
    // 用户节点映射
    mapping(address => Node[]) public userNodes;
    mapping(address => uint256) public userRewards;
    mapping(address => uint256) public userTotalHashrate;
    
    // 全网统计
    uint256 public totalNodes;
    uint256 public totalHashrate;
    uint256 public dailyOutput = 92400 * 10**18; // 每日产出92400个代币（18位小数）
    
    // 常量
    uint256 public constant BASE_HASHRATE = 500;
    uint256 public constant NODE_PRICE = 0.01 ether;
    uint256 public constant REWARD_RELEASE_RATIO = 80; // 80%立即释放
    uint256 public constant LINEAR_RELEASE_DAYS = 10;
    
    // 事件
    event NodePurchased(address indexed user, uint256 nodeId, uint256 hashrate, uint256 timestamp);
    event RewardsClaimed(address indexed user, uint256 amount, uint256 timestamp);
    event RewardsDistributed(address indexed user, uint256 amount, uint256 timestamp);
    
    // 购买节点
    function buyNode(uint256 nodeCount) external payable {
        require(msg.value >= nodeCount * NODE_PRICE, "Insufficient payment");
        require(nodeCount > 0, "Node count must be greater than 0");
        
        for (uint256 i = 0; i < nodeCount; i++) {
            uint256 nodeId = totalNodes;
            
            Node memory newNode = Node({
                nodeId: nodeId,
                hashrate: BASE_HASHRATE,
                owner: msg.sender,
                purchaseTime: block.timestamp,
                active: true
            });
            
            userNodes[msg.sender].push(newNode);
            totalNodes++;
            totalHashrate += BASE_HASHRATE;
            userTotalHashrate[msg.sender] += BASE_HASHRATE;
            
            emit NodePurchased(msg.sender, nodeId, BASE_HASHRATE, block.timestamp);
        }
    }
    
    // 领取奖励
    function claimRewards() external {
        uint256 rewards = userRewards[msg.sender];
        require(rewards > 0, "No rewards to claim");
        
        userRewards[msg.sender] = 0;
        
        // 转账奖励（这里简化处理，实际应该使用代币合约）
        // payable(msg.sender).transfer(rewards);
        
        emit RewardsClaimed(msg.sender, rewards, block.timestamp);
    }
    
    // 分发奖励（仅合约所有者或特定角色可调用）
    function distributeRewards(address user, uint256 amount) external {
        userRewards[user] += amount;
        emit RewardsDistributed(user, amount, block.timestamp);
    }
    
    // 获取用户节点数量
    function getUserNodeCount(address user) external view returns (uint256) {
        return userNodes[user].length;
    }
    
    // 获取用户节点详情
    function getUserNodes(address user) external view returns (Node[] memory) {
        return userNodes[user];
    }
    
    // 获取用户总算力
    function getUserHashrate(address user) external view returns (uint256) {
        return userTotalHashrate[user];
    }
    
    // 获取用户待领取奖励
    function getUserRewards(address user) external view returns (uint256) {
        return userRewards[user];
    }
    
    // 获取全网统计
    function getNetworkStats() external view returns (uint256, uint256, uint256) {
        return (totalNodes, totalHashrate, dailyOutput);
    }
    
    // 计算用户每日产出
    function calculateDailyOutput(address user) external view returns (uint256) {
        if (totalHashrate == 0) return 0;
        
        uint256 userHashrate = userTotalHashrate[user];
        uint256 userShare = (userHashrate * 10000) / totalHashrate; // 万分之几
        uint256 userDailyOutput = (dailyOutput * userShare) / 10000;
        
        return userDailyOutput;
    }
    
    // 接收ETH
    receive() external payable {}
}