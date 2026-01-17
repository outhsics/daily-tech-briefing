#!/bin/bash
# Docker 快速启动脚本

echo "🐳 使用 Docker 启动项目"
echo "================================"

# 构建轻量级镜像
echo "📦 构建轻量级镜像（不含 Playwright）..."
docker-compose build celery_worker celery_beat

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d celery_worker celery_beat

echo ""
echo "✅ Docker 服务启动成功！"
echo ""
echo "📊 查看日志:"
echo "  docker-compose logs -f celery_worker"
echo ""
echo "🔍 查看状态:"
echo "  docker-compose ps"
