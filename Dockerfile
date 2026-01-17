FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p output logs

# 暴露端口（如果需要FastAPI）
EXPOSE 8000

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 默认命令
CMD ["python", "-m", "celery", "-A", "app.tasks.briefing_task", "worker", "--loglevel=info"]
