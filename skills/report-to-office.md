# 汇报状态到 Claw Office

将当前 agent 的状态汇报到 Claw Office UI，让主人可以在办公室界面看到你的工作情况。

## 使用方式

```
/report-to-claw-office <state> [detail]
```

- `state`: 必填，当前状态
- `detail`: 可选，状态详情描述

## 状态说明

| 状态 | 含义 | 办公室位置 |
|------|------|-----------|
| `idle` | 待命/休息 | 休息区 (沙发) |
| `writing` | 写代码/文档 | 工作区 (办公桌) |
| `researching` | 调研/搜索 | 工作区 (办公桌) |
| `executing` | 执行任务 | 工作区 (办公桌) |
| `syncing` | 同步/等待 | 工作区 (办公桌) |
| `error` | 出错了 | 错误区 (bug区域) |

## 示例

```
/report-to-claw-office writing 正在重构用户模块
/report-to-claw-office researching 搜索最佳实践
/report-to-claw-office executing 运行测试套件
/report-to-claw-office idle 任务完成，待命中
/report-to-claw-office error 数据库连接失败
```

## 技术实现

向 Claw Office 发送带 HMAC 签名的心跳请求：

**端点**: `POST /agent-heartbeat`

**请求头**:
```
Content-Type: application/json
X-Agent-Id: <agentId>
X-Timestamp: 2026-03-29T12:00:00Z
X-Signature: hmac-sha256=<signature>
```

**请求体**:
```json
{
  "state": "writing",
  "detail": "正在编写 API 文档",
  "progress": 50
}
```

**签名算法**: `HMAC-SHA256(timestamp + "\n" + body, secretKey)`

配置从 `openclaw.json` 的 `agents.defaults.clawOffice` 读取。

## 注意事项

- 心跳间隔建议 15-30 秒
- 超过 5 分钟无心跳会被标记为 offline
- 时间戳使用 UTC，允许 ±5 分钟偏差
