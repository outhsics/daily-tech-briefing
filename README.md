# 每日科技简报生成系统 🤖📰

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-5.3+-red.svg)](https://docs.celeryq.dev)

> 一个基于 AI 的自动化科技简报生成系统，定时抓取多个科技媒体内容，使用大模型智能分析并生成结构化简报页面。

## ⭐ 如果这个项目对你有帮助，请给个 Star 支持！

## ✨ 特性

- 🔄 **自动化采集** - 定时抓取 V2EX、Hacker News、36氪等主流科技媒体
- 🤖 **AI 智能分析** - 使用智谱 GLM-4 或通义千问进行内容摘要和趋势分析
- 📊 **结构化展示** - 生成美观的 HTML 简报页面，支持响应式设计
- 📢 **多渠道推送** - 支持 Telegram 和邮件自动推送
- ⏰ **定时任务** - 基于 Celery Beat 的可靠定时调度
- 🎯 **Claude Agent Skills** - 可通过自然语言控制和管理

## 🏗️ 技术架构

```
Claude Agent Skills (Skill 入口)
    │
    ▼
Celery (定时调度 + 任务队列)
    ├── Celery Beat: 定时触发（每天 9:00）
    ├── Celery Worker: 异步处理
    └── Flower: 监控面板
    │
    ▼
业务逻辑模块
    ├── Scrapers: 数据采集（V2EX、HN、36氪等）
    ├── Processors: 数据清洗和去重
    ├── AI Service: 智谱/通义千问分析
    ├── Generator: HTML 页面生成
    └── Notifiers: TG/邮件推送
    │
    ▼
存储层
    ├── PostgreSQL: 文章和简报数据
    └── Redis: Celery 消息队列
```

## 📦 项目结构

```
daily-tech-briefing/
├── app/
│   ├── scrapers/          # 爬虫模块
│   ├── processors/        # 数据处理
│   ├── ai/                # AI 服务（智谱/通义千问）
│   ├── generators/        # 页面生成
│   ├── notifiers/         # 推送通知
│   ├── tasks/             # Celery 任务
│   ├── models/            # 数据模型
│   ├── database/          # 数据库操作
│   └── config.py          # 配置管理
├── output/                # 生成的简报页面
├── logs/                  # 日志文件
├── docker-compose.yml     # Docker 编排
├── Dockerfile             # Docker 镜像
├── skill.py               # Claude Agent Skill 入口
└── requirements.txt       # Python 依赖
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd daily-tech-briefing
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# AI 服务（二选一）
ZHIPUAI_API_KEY=your_key_here  # 智谱 AI
# 或
DASHSCOPE_API_KEY=your_key_here  # 通义千问
AI_PROVIDER=zhipu  # 选择 AI 提供商

# Telegram 推送（可选）
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# 邮件推送（可选）
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email
SMTP_PASSWORD=your_password
```

### 3. Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f celery_worker

# 查看监控面板（可选）
docker-compose --profile monitoring up -d flower
# 访问 http://localhost:5555
```

### 4. 手动触发简报生成

```bash
# 使用 Claude Agent Skill
python skill.py generate

# 或直接使用 Celery
docker-compose exec celery_worker celery -A app.tasks.briefing_task call manual_trigger_briefing
```

### 5. 查看生成的简报

```bash
# 查看输出目录
ls output/

# 或访问 Web 界面（如果启用）
docker-compose --profile web up -d
# 访问 http://localhost:8000
```

## 🎯 Claude Agent Skills 使用

### 通过 Skill 脚本控制

```bash
# 生成今日简报
python skill.py generate

# 查看最近简报
python skill.py recent

# 查看今日文章
python skill.py today

# 测试通知推送
python skill.py test

# 查看系统状态
python skill.py status
```

### 返回格式

```json
{
  "action": "generate_briefing",
  "result": {
    "status": "success",
    "articles_count": 42,
    "html_path": "output/2024-01-15.html",
    "elapsed": 125.3
  },
  "message": "✅ 简报生成完成！共 42 篇文章"
}
```

## 📊 监控和管理

### Flower 监控面板

```bash
# 启用监控
docker-compose --profile monitoring up -d flower

# 访问
http://localhost:5555
```

可以查看：
- 任务执行状态
- Worker 负载情况
- 任务执行历史
- 任务耗时统计

### 日志查看

```bash
# 实时日志
docker-compose logs -f celery_worker

# 查看特定时间范围
docker-compose logs --since 2024-01-15 celery_worker
```

## ⚙️ 配置说明

### 定时任务配置

在 `.env` 中修改：

```env
# 每天执行时间（24小时制）
BRIEFING_HOUR=9
BRIEFING_MINUTE=0
```

### AI 服务配置

```env
# 使用智谱 AI
AI_PROVIDER=zhipu
ZHIPUAI_MODEL=glm-4  # 或 glm-3-turbo

# 使用通义千问
AI_PROVIDER=qwen
DASHSCOPE_MODEL=qwen-turbo  # 或 qwen-plus
```

### 数据源配置

在 `app/scrapers/__init__.py` 中添加或移除数据源。

## 📈 成本估算

基于每月运行：

| 项目 | 成本 |
|------|------|
| AI 调用（智谱 GLM-4） | ~¥15-30/月 |
| 服务器（轻量应用） | ¥30-50/月 |
| **总计** | **¥45-80/月** |

## 🔧 高级配置

### 添加新数据源

1. 在 `app/scrapers/` 创建新爬虫类
2. 继承 `BaseScraper`
3. 实现 `fetch()` 方法
4. 在 `app/scrapers/__init__.py` 中注册

### 自定义 HTML 模板

编辑 `app/generators/templates/briefing.html`

### 添加新推送渠道

在 `app/notifiers/` 创建新的推送类

## 🛠️ 开发指南

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 启动 Redis 和 PostgreSQL（本地或 Docker）
docker-compose up -d redis postgres

# 启动 Celery Worker
celery -A app.tasks.briefing_task worker --loglevel=info

# 启动 Celery Beat（另一个终端）
celery -A app.tasks.briefing_task beat --loglevel=info

# 手动触发任务
python skill.py generate
```

### 运行测试

```bash
pytest tests/ -v
```

## 📝 API 接口

如果启用 Web 服务：

```bash
# 启动 Web 服务
docker-compose --profile web up -d
```

可用接口：
- `GET /` - 服务状态
- `GET /api/briefings/recent` - 最近简报
- `GET /api/briefings/{date}` - 指定日期简报
- `GET /api/articles/today` - 今日文章
- `GET /api/articles/source/{source}` - 按来源查询

## 🐛 故障排查

### Celery Worker 不执行任务

```bash
# 检查 Worker 状态
docker-compose logs celery_worker

# 检查 Celery 配置
docker-compose exec celery_worker celery -A app.tasks.briefing_task inspect active
```

### AI API 调用失败

```bash
# 检查 API 密钥
docker-compose exec celery_worker env | grep API

# 查看详细错误日志
docker-compose logs celery_worker | grep -i error
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 测试连接
docker-compose exec postgres psql -U user -d briefing_db -c "SELECT 1;"
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 数据源：V2EX、Hacker News、36氪等
- AI 服务：智谱 AI、阿里云通义千问
- 技术栈：FastAPI、Celery、Playwright

## 📮 联系方式

- Issues: <repository-issues>
- Email: your-email@example.com

---

**Generated with ❤️ by AI**
