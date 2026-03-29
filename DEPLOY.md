# 部署指南

## 快速部署

```bash
# 1. 构建并启动
docker-compose up -d --build

# 2. 查看日志
docker-compose logs -f

# 3. 访问
# http://localhost:19000
```

## 配置说明

### agents-config.json

已在项目中配置好 6 个 agent（main, ling, yi, hua, xiaosu, jiuku）：

```json
{
  "defaults": {
    "secretKey": "z5wKfgiOwCfFTtQSR-ThM0nOa-IYCvXoqo4PwsxereU"
  },
  "agents": [...]
}
```

### OpenClaw 那边需要配置

在 `~/.openclaw/openclaw.json` 的 `agents.defaults` 中添加：

```json
{
  "agents": {
    "defaults": {
      "starOffice": {
        "officeUrl": "http://star-office:19000",
        "secretKey": "z5wKfgiOwCfFTtQSR-ThM0nOa-IYCvXoqo4PwsxereU"
      }
    }
  }
}
```

### Docker 网络互通

如果 OpenClaw 和 Star Office 在同一台服务器：

**方案 1：同一 docker-compose**

```yaml
services:
  star-office:
    build: ./Star-Office-UI
    ports:
      - "19000:19000"
    networks:
      - office-net

  openclaw:
    image: openclaw
    networks:
      - office-net

networks:
  office-net:
```

OpenClaw 配置 `officeUrl: http://star-office:19000`

**方案 2：使用宿主机 IP**

OpenClaw 配置 `officeUrl: http://宿主机内网IP:19000`

## 常用命令

```bash
# 重启服务
docker-compose restart

# 重新构建
docker-compose up -d --build

# 查看状态
docker-compose ps

# 停止服务
docker-compose down
```

## 文件挂载

已挂载的文件（可在宿主机直接编辑）：

- `agents-config.json` - Agent 配置
- `agents-state.json` - Agent 状态
- `state.json` - 主状态
- `assets/` - 资产文件
- `frontend/` - 前端文件
