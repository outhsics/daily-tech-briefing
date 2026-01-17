#!/bin/bash
# 快速启动脚本

echo "🚀 每日科技简报生成系统 - 快速启动"
echo "======================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，从 .env.example 复制..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo "⚠️  请编辑 .env 文件，配置必要的参数（AI API 密钥等）"
    echo ""
    read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
fi

# 创建必要的目录
mkdir -p output logs

echo ""
echo "📦 启动 Docker 服务..."
docker-compose up -d redis postgres

echo ""
echo "⏳ 等待数据库启动..."
sleep 5

echo ""
echo "🚀 启动 Celery Worker 和 Beat..."
docker-compose up -d celery_worker celery_beat

echo ""
echo "✅ 服务启动成功！"
echo ""
echo "📊 查看日志:"
echo "  docker-compose logs -f celery_worker"
echo ""
echo "🎯 手动触发简报生成:"
echo "  python skill.py generate"
echo "  或"
echo "  docker-compose exec celery_worker celery -A app.tasks.briefing_task call manual_trigger_briefing"
echo ""
echo "📈 启动监控面板 (可选):"
echo "  docker-compose --profile monitoring up -d flower"
echo "  访问: http://localhost:5555"
echo ""
echo "🌐 启动 Web API (可选):"
echo "  docker-compose --profile web up -d"
echo "  访问: http://localhost:8000"
echo ""
echo "📖 查看README了解更多信息"
