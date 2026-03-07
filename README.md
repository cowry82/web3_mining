# 挖矿系统 README

## 项目概述

这是一个基于Python和Flask的挖矿系统，支持BSC链集成，实现了节点购买、挖矿奖励分发、邀请奖励等功能。系统使用配置文件管理所有数值参数，支持MySQL和SQLite数据库，并提供了完整的API接口。

## 功能特性

- **节点系统**：支持4种节点类型（basic、intermediate、advanced、genesis），每种节点有不同的价格、购买限制和邀请奖励
- **挖矿机制**：实现了固定产出率、挖矿时长、产量浮动等规则
- **收益分配**：80%用于节点挖矿分配，日释放1%
- **减产机制**：类似于比特币的每4年（1460天）产量减半
- **邀请奖励**：一级邀请和二级邀请都有USDT和算力奖励
- **数据库支持**：同时支持MySQL和SQLite，MySQL连接失败时自动切换到SQLite
- **定时任务**：独立的定时任务系统，可通过API控制启动/停止
- **API接口**：提供了完整的RESTful API接口
- **算力管理**：用户算力存储在fa_app_currency_user表中

## 技术栈

- **后端**：Python 3.8+, Flask 2.0.1
- **数据库**：MySQL / SQLite
- **区块链**：BSC (Binance Smart Chain)
- **部署**：本地开发服务器

## 目录结构

```
mining/
├── app.py              # 主应用文件，实现API接口
├── config.py           # 配置文件，管理所有数值参数
├── database.py         # 数据库连接和初始化
├── mining_service.py   # 挖矿核心逻辑
├── scheduler.py        # 定时任务实现
├── requirements.txt    # 依赖包管理
├── mining.db           # SQLite数据库文件（自动生成）
└── __pycache__/        # Python缓存文件
```

## 配置说明

所有配置参数都在 `config.py` 文件中定义，主要包括：

- **节点配置**：价格、最大购买次数、邀请奖励、总供应量
- **挖矿规则**：固定产出速率、挖矿年限、基础节点日产量范围
- **收益分配**：挖矿分配比例、日释放率
- **减产机制**：初始日产量、减产间隔
- **奖励发放时间**：每日发放奖励的时间
- **区块链配置**：BSC RPC URL
- **数据库配置**：数据库类型、主机、端口、用户名、密码、数据库名
- **服务器配置**：服务端口

## 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 配置数据库

在 `config.py` 中修改数据库配置：

```python
'database': {
    'type': 'mysql',  # 或 'sqlite'
    'host': '192.168.2.202',
    'port': 3306,
    'user': 'jys_php',
    'password': 'XGDHy47fxhThDSkA',
    'db': 'bitup-mining'
}
```

### 3. 启动服务

```bash
python3 app.py
```

服务将在 `http://127.0.0.1:8000` 启动。

### 4. 初始化数据库

服务启动时会自动初始化数据库表结构，包括：
- users：用户表
- node_purchases：节点购买记录表
- unlock_records：解锁记录表
- nodes：节点表
- mining_records：挖矿记录表
- network_power：全网算力表
- fa_app_currency：币种表
- fa_app_currency_user：用户币种表

### 5. 启动定时任务

通过API启动定时任务：

```bash
curl -X POST http://localhost:8000/api/scheduler/start -H "Authorization: token_123"
```

## API接口文档

### 1. 购买节点

**URL**: `/api/purchase-node`
**方法**: POST
**请求体**:
```json
{
  "user_id": "123",
  "node_type": "basic",
  "referrer_code": "REF_456_1234"  // 可选
}
```
**响应**:
```json
{
  "success": true,
  "user_id": "123",
  "node_type": "basic",
  "price": 1000,
  "referrer_id": "456"
}
```

### 2. 获取节点详情

**URL**: `/api/node-details/<node_type>`
**方法**: GET
**响应**:
```json
{
  "success": true,
  "node_type": "basic",
  "price": 1000,
  "max_purchase": 5,
  "total_supply": 5000,
  "remaining": 4999,
  "referral_level1": {
    "power": 50,
    "usdt": 0.05
  },
  "referral_level2": {
    "power": 5,
    "usdt": 0.02
  }
}
```

### 3. 获取购买记录

**URL**: `/api/purchase-records`
**方法**: GET
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "node_type": "basic",
      "price": 1000.0,
      "purchase_time": "2026-03-07 14:44:55",
      "referrer_id": null,
      "status": "active"
    }
  ]
}
```

### 4. 获取节点价格

**URL**: `/api/node-prices`
**方法**: GET
**响应**:
```json
{
  "success": true,
  "prices": {
    "advanced": 10000,
    "basic": 1000,
    "genesis": 50000,
    "intermediate": 3000
  }
}
```

### 5. 获取解锁记录

**URL**: `/api/unlock-records`
**方法**: GET
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "records": []
}
```

### 6. 获取挖矿记录

**URL**: `/api/mining-records`
**方法**: GET
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "records": [
    {
      "id": 1,
      "amount": 756000.0,
      "power": 50.0,
      "total_power": 50.0,
      "daily_output": 945000.0,
      "mining_date": "2026-03-07",
      "created_at": "2026-03-07 14:45:30"
    }
  ]
}
```

### 7. 获取用户算力

**URL**: `/api/user-power`
**方法**: GET
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "user_id": "123",
  "power": 50.0
}
```

### 8. 手动触发挖矿

**URL**: `/api/trigger-mining`
**方法**: POST
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "message": "Mining rewards distributed successfully"
}
```

### 9. 启动定时任务

**URL**: `/api/scheduler/start`
**方法**: POST
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "message": "Scheduler started successfully"
}
```

### 10. 停止定时任务

**URL**: `/api/scheduler/stop`
**方法**: POST
**头部**:
- Authorization: token_123
**响应**:
```json
{
  "success": true,
  "message": "Scheduler stopped successfully"
}
```

## 数据库结构

### 核心表结构

1. **users**：用户表
   - id：自增主键
   - user_id：用户ID
   - tokens：用户代币余额
   - power：用户算力
   - referral_code：邀请码
   - referrer_id：推荐人ID
   - created_at：创建时间

2. **node_purchases**：节点购买记录表
   - id：自增主键
   - user_id：用户ID
   - node_type：节点类型
   - price：购买价格
   - purchase_time：购买时间
   - referrer_id：推荐人ID
   - status：状态

3. **mining_records**：挖矿记录表
   - id：自增主键
   - user_id：用户ID
   - amount：挖矿奖励金额
   - power：用户算力
   - total_power：全网算力
   - daily_output：当日总产量
   - mining_date：挖矿日期
   - created_at：创建时间

4. **fa_app_currency**：币种表
   - id：自增主键
   - name：币种名称
   - full_name：币种全称
   - suffix：币种后缀
   - status：状态

5. **fa_app_currency_user**：用户币种表
   - id：自增主键
   - user_id：用户ID
   - curr_id：币种ID
   - num：币种数量（用于存储算力）
   - updatetime：更新时间
   - regtime：注册时间

## 挖矿规则

### 1. 产出计算

- **固定产出速率**：0.03 BUB / T
- **挖矿年限**：10-15年
- **基础节点日产量**：10-30 BUB（1000U投资）

### 2. 收益分配

- **挖矿分配**：80%用于节点挖矿分配
- **日释放率**：1%

### 3. 减产机制

- **初始日产量**：945,000 BUB
- **减产间隔**：每4年（1,460天）
- **减产方式**：日产量减半

### 4. 邀请奖励

| 节点类型 | 一级邀请奖励 | 二级邀请奖励 |
|---------|------------|------------|
| basic   | 5% USDT + 50T 算力 | 2% USDT + 5T 算力 |
| intermediate | 6% USDT + 100T 算力 | 3% USDT + 10T 算力 |
| advanced | 8% USDT + 150T 算力 | 4% USDT + 20T 算力 |
| genesis | 10% USDT + 200T 算力 | 5% USDT + 50T 算力 |

## 部署说明

### 生产环境部署

1. **安装依赖**：
   ```bash
   pip3 install -r requirements.txt
   ```

2. **配置数据库**：
   - 确保MySQL服务运行
   - 创建数据库 `bitup-mining`
   - 配置数据库用户权限

3. **修改配置**：
   - 在 `config.py` 中修改数据库配置
   - 调整服务器端口（默认8000）

4. **启动服务**：
   ```bash
   python3 app.py
   ```

5. **启动定时任务**：
   ```bash
   curl -X POST http://localhost:8000/api/scheduler/start -H "Authorization: token_admin"
   ```

### 开发环境测试

1. **使用SQLite**：
   - 在 `config.py` 中设置 `'type': 'sqlite'`
   - 系统会自动创建 `mining.db` 文件

2. **测试API**：
   - 使用curl或Postman测试API接口
   - 例如：`curl -X POST http://localhost:8000/api/purchase-node -H "Content-Type: application/json" -d '{"user_id": "123", "node_type": "basic"}'`

## 故障排除

### 1. 数据库连接失败

- **症状**：日志中显示 "数据库连接失败: 1044 (42000): Access denied for user 'jys_php'@'%' to database 'bitup-mining'"
- **解决方案**：
  - 检查MySQL用户名和密码是否正确
  - 确保用户有访问数据库的权限
  - 系统会自动切换到SQLite作为后备

### 2. 端口占用

- **症状**：启动时显示 "Address already in use"
- **解决方案**：
  - 在 `config.py` 中修改 `'port'` 配置
  - 例如：`'port': 8001`

### 3. 数据库锁定

- **症状**：日志中显示 "database is locked"
- **解决方案**：
  - 系统已优化数据库连接管理，确保每次操作后关闭连接
  - 避免并发操作同一个数据库文件

### 4. 定时任务不执行

- **症状**：挖矿奖励没有按时发放
- **解决方案**：
  - 检查定时任务是否已启动：`curl -X POST http://localhost:8000/api/scheduler/start -H "Authorization: token_123"`
  - 检查配置文件中的奖励发放时间设置

## 常见问题

### Q: 如何修改节点价格？
A: 在 `config.py` 文件中修改 `'nodes'` 配置中的 `'price'` 参数。

### Q: 如何调整邀请奖励比例？
A: 在 `config.py` 文件中修改 `'nodes'` 配置中的 `'referral_level1'` 和 `'referral_level2'` 参数。

### Q: 如何查看全网算力？
A: 系统会自动更新 `network_power` 表，可通过数据库查询获取。

### Q: 如何手动触发挖矿奖励？
A: 使用 `/api/trigger-mining` 接口：`curl -X POST http://localhost:8000/api/trigger-mining -H "Authorization: token_123"`

## 技术支持

如需技术支持，请联系系统管理员。

---

**版本**：1.0.0
**更新日期**：2026-03-07
**作者**：Mining System Team