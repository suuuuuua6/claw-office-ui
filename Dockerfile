FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制前端静态文件
COPY frontend/ ./static/

# 复制配置文件
COPY agents-config.json .
COPY agents-state.json .
COPY state.json .
COPY join-keys.json .

# 创建必要的目录
RUN mkdir -p assets assets/bg-history assets/home-favorites

# 暴露端口
EXPOSE 19000

# 启动服务
CMD ["python3", "app.py"]
