# 节点购买系统 API 文档

## 基础信息

- **Base URL**: `http://localhost:5001`
- **Content-Type**: `application/json; charset=utf-8`
- **字符编码**: UTF-8

---

## 接口列表

### 1. 购买节点

**接口地址**: `POST /api/buy-nodes`

**功能描述**: 购买挖矿节点

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID |
| node_count | integer | 是 | 节点数量 |
| payment_amount | number | 是 | 支付金额（USDT） |

**请求示例**:
```bash
curl -X POST http://localhost:5001/api/buy-nodes \
  -H 'Content-Type: application/json' \
  -d '{
    "uid": "alice",
    "node_count": 2,
    "payment_amount": 1000
  }'
```

**响应示例**:
```json
{
  "success": true,
  "tx_hash": "0x1234567890abcdef...",
  "message": "成功购买 2 个节点",
  "node_info": {
    "node_count": 2,
    "total_hashrate": 1000,
    "last_purchase": "2026-02-28T20:49:39.984193"
  },
  "purchase_record": {
    "record_id": "purchase_alice_1772282979",
    "uid": "alice",
    "node_count": 2,
    "payment_amount": 1000,
    "price_per_node": 500.0,
    "total_price": 1000.0,
    "tx_hash": "0x1234567890abcdef...",
    "purchase_time": "2026-02-28T20:49:39.984193",
    "status": "completed"
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "支付金额不足，需要 1000.0 USDT"
}
```

---

### 2. 获取节点详情

**接口地址**: `GET /api/node-details/<uid>`

**功能描述**: 获取用户的节点详情信息

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID（URL路径参数） |

**请求示例**:
```bash
curl http://localhost:5001/api/node-details/alice
```

**响应示例**:
```json
{
  "success": true,
  "node_details": [
    {
      "node_id": "node_alice_0_0",
      "hashrate": 500,
      "xCPT_per_T": 0.004545,
      "today_output": 2.2725,
      "today_unlock": 1.818,
      "duration": "0天",
      "unlocked_tokens": 0.0,
      "total_output": 0.0,
      "total_unlocked": 0.0
    },
    {
      "node_id": "node_alice_1_1",
      "hashrate": 500,
      "xCPT_per_T": 0.004545,
      "today_output": 2.2725,
      "today_unlock": 1.818,
      "duration": "0天",
      "unlocked_tokens": 0.0,
      "total_output": 0.0,
      "total_unlocked": 0.0
    }
  ]
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| node_id | string | 节点ID |
| hashrate | number | 节点算力（T） |
| xCPT_per_T | number | 每T算力的xCPT产出 |
| today_output | number | 今日产出CPT |
| today_unlock | number | 今日解锁CPT |
| duration | string | 节点运行时长 |
| unlocked_tokens | number | 待解锁代币CPT |
| total_output | number | 累计产出CPT |
| total_unlocked | number | 累计解锁CPT |

---

### 3. 获取购买记录

**接口地址**: `GET /api/purchase-records/<uid>`

**功能描述**: 获取用户的节点购买记录

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID（URL路径参数） |

**请求示例**:
```bash
curl http://localhost:5001/api/purchase-records/alice
```

**响应示例**:
```json
{
  "success": true,
  "uid": "alice",
  "purchase_records": [
    {
      "record_id": "purchase_alice_1772282979",
      "uid": "alice",
      "node_count": 2,
      "payment_amount": 1000,
      "price_per_node": 500.0,
      "total_price": 1000.0,
      "tx_hash": "0x1234567890abcdef...",
      "purchase_time": "2026-02-28T20:49:39.984193",
      "status": "completed"
    }
  ],
  "total_count": 1,
  "total_amount": 1000,
  "total_nodes": 2
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| record_id | string | 记录ID |
| uid | string | 用户ID |
| node_count | integer | 购买的节点数量 |
| payment_amount | number | 支付金额 |
| price_per_node | number | 单个节点价格 |
| total_price | number | 总价格 |
| tx_hash | string | 交易哈希 |
| purchase_time | string | 购买时间 |
| status | string | 状态 |

---

### 4. 获取节点价格

**接口地址**: `GET /api/node-price`

**功能描述**: 获取节点价格配置信息

**请求参数**: 无

**请求示例**:
```bash
curl http://localhost:5001/api/node-price
```

**响应示例**:
```json
{
  "success": true,
  "price_config": {
    "price_per_node": 500.0,
    "currency": "USDT",
    "min_purchase": 1,
    "max_purchase": 200,
    "discount_info": {
      "bulk_discount": {
        "min_nodes": 10,
        "discount_rate": 0.05
      }
    }
  }
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| price_per_node | number | 单个节点价格 |
| currency | string | 货币单位 |
| min_purchase | integer | 最小购买数量 |
| max_purchase | integer | 最大购买数量 |
| discount_info | object | 折扣信息 |
| bulk_discount.min_nodes | integer | 批量折扣最小节点数 |
| bulk_discount.discount_rate | number | 折扣率 |

---

### 5. 获取解锁记录

**接口地址**: `GET /api/unlock-records/<uid>`

**功能描述**: 获取用户的代币解锁记录

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID（URL路径参数） |

**请求示例**:
```bash
curl http://localhost:5001/api/unlock-records/alice
```

**响应示例**:
```json
{
  "success": true,
  "uid": "alice",
  "unlock_records": [
    {
      "record_id": "unlock_alice_node_alice_0_0_0",
      "uid": "alice",
      "node_id": "node_alice_0_0",
      "unlock_date": "2026-02-28T20:49:52.842744",
      "unlock_amount": 1.818,
      "unlock_type": "daily_linear",
      "status": "pending"
    },
    {
      "record_id": "unlock_alice_node_alice_1_1_0",
      "uid": "alice",
      "node_id": "node_alice_1_1",
      "unlock_date": "2026-02-28T20:49:52.842757",
      "unlock_amount": 1.818,
      "unlock_type": "daily_linear",
      "status": "pending"
    }
  ],
  "total_unlocked": 0,
  "pending_unlock": 3.636,
  "total_records": 2
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| record_id | string | 记录ID |
| uid | string | 用户ID |
| node_id | string | 节点ID |
| unlock_date | string | 解锁日期 |
| unlock_amount | number | 解锁金额 |
| unlock_type | string | 解锁类型 |
| status | string | 状态（completed/pending） |

---

## 错误码说明

| HTTP状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 用户不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. **用户ID**: 用户ID可以是任意字符串，建议使用用户名、邮箱或钱包地址
2. **节点价格**: 当前每个节点价格为 500 USDT
3. **支付金额**: 支付金额必须大于等于 `节点数量 × 500`
4. **批量折扣**: 购买10个以上节点可享受5%折扣
5. **数据来源**: 所有数据均从BSC链上获取
6. **字符编码**: 所有接口返回中文数据使用UTF-8编码

---

## 测试示例

### 完整测试流程

```bash
# 1. 购买节点
curl -X POST http://localhost:5001/api/buy-nodes \
  -H 'Content-Type: application/json' \
  -d '{
    "uid": "test_user",
    "node_count": 2,
    "payment_amount": 1000
  }'

# 2. 查看节点详情
curl http://localhost:5001/api/node-details/test_user

# 3. 查看购买记录
curl http://localhost:5001/api/purchase-records/test_user

# 4. 查看节点价格
curl http://localhost:5001/api/node-price

# 5. 查看解锁记录
curl http://localhost:5001/api/unlock-records/test_user
```

---

### 6. 获取24小时倒计时

**接口地址**: `GET /api/countdown/<uid>`

**功能描述**: 获取用户的24小时倒计时信息，用于领取每日奖励

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID（URL路径参数） |

**请求示例**:
```bash
curl http://localhost:5001/api/countdown/alice
```

**响应示例**:
```json
{
  "success": true,
  "uid": "alice",
  "countdown": {
    "total_seconds": 86350,
    "hours": 23,
    "minutes": 59,
    "seconds": 10,
    "formatted": "23:59:10"
  },
  "next_claim_time": "2026-03-01T20:49:39.984193",
  "last_claim_time": null,
  "can_claim": false,
  "daily_reward": 4.545,
  "node_count": 2
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| countdown.total_seconds | integer | 剩余总秒数 |
| countdown.hours | integer | 剩余小时数 |
| countdown.minutes | integer | 剩余分钟数 |
| countdown.seconds | integer | 剩余秒数 |
| countdown.formatted | string | 格式化的时间字符串 (HH:MM:SS) |
| next_claim_time | string | 下次可领取时间 |
| last_claim_time | string | 上次领取时间 |
| can_claim | boolean | 是否可以领取 |
| daily_reward | number | 今日可领取奖励（CPT） |
| node_count | integer | 节点数量 |

---

### 7. 领取每日奖励

**接口地址**: `POST /api/claim-reward`

**功能描述**: 领取每日挖矿奖励

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| uid | string | 是 | 用户ID |

**请求示例**:
```bash
curl -X POST http://localhost:5001/api/claim-reward \
  -H 'Content-Type: application/json' \
  -d '{
    "uid": "alice"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "成功领取 4.5450 CPT",
  "claimed_amount": 4.545,
  "tx_hash": "0x1234567890abcdef...",
  "claim_time": "2026-02-28T20:50:00.123456",
  "next_claim_time": "2026-03-01T20:50:00.123456"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "还需等待 23:59:10 才能领取",
  "next_claim_time": "2026-03-01T20:49:39.984193"
}
```

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| claimed_amount | number | 领取金额（CPT） |
| tx_hash | string | 交易哈希 |
| claim_time | string | 领取时间 |
| next_claim_time | string | 下次可领取时间 |

---

## 更新日志

- **2026-02-28**: 初始版本，包含5个基础接口
  - 购买节点
  - 获取节点详情
  - 获取购买记录
  - 获取节点价格
  - 获取解锁记录

- **2026-02-28**: 新增2个接口
  - 获取24小时倒计时
  - 领取每日奖励