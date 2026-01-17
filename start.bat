@echo off
REM Windows 快速启动脚本

echo 🚀 每日科技简报生成系统 - 快速启动
echo ======================================

REM 检查 Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo ⚠️  .env 文件不存在，从 .env.example 复制...
    copy .env.example .env
    echo ✅ 已创建 .env 文件
    echo ⚠️  请编辑 .env 文件，配置必要的参数（AI API 密钥等）
    echo.
    notepad .env
)

REM 创建必要的目录
if not exist output mkdir output
if not exist logs mkdir logs

echo.
echo 📦 启动 Docker 服务...
docker-compose up -d redis postgres

echo.
echo ⏳ 等待数据库启动...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 启动 Celery Worker 和 Beat...
docker-compose up -d celery_worker celery_beat

echo.
echo ✅ 服务启动成功！
echo.
echo 📊 查看日志:
echo   docker-compose logs -f celery_worker
echo.
echo 🎯 手动触发简报生成:
echo   python skill.py generate
echo.
echo 📈 启动监控面板 (可选):
echo   docker-compose --profile monitoring up -d flower
echo   访问: http://localhost:5555
echo.
pause
