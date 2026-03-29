FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 创建目录结构（模拟本地开发环境）
RUN mkdir -p backend frontend

# 复制后端代码到 backend/
COPY backend/ ./backend/

# 复制前端静态文件到 frontend/
COPY frontend/ ./frontend/

# 复制配置文件到根目录
COPY agents-config.json .

# 创建必要的目录
RUN mkdir -p assets assets/bg-history assets/home-favorites

# 暴露端口
EXPOSE 19000

# 启动服务（从 backend/ 目录运行）
WORKDIR /app/backend
CMD ["python3", "app.py"]
