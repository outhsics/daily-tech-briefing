#!/usr/bin/env python3
"""
Claude Agent Skill - 每日科技简报生成系统
通过自然语言控制简报生成和管理
"""
import sys
import asyncio
from datetime import date, datetime
from typing import Optional

# 添加项目路径
sys.path.insert(0, "/app")

from app.tasks.briefing_task import manual_trigger_briefing, test_notification
from app.database.crud import BriefingCRUD, ArticleCRUD
from app.database import async_session_maker
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BriefingSkill:
    """Claude Agent Skill - 科技简报管理"""

    def __init__(self):
        self.name = "每日科技简报生成系统"

    async def generate_briefing(self) -> dict:
        """立即生成今日简报"""
        logger.info("🚀 触发简报生成...")
        result = manual_trigger_briefing()
        return {
            "action": "generate_briefing",
            "result": result,
            "message": f"✅ 简报生成完成！共 {result.get('articles_count', 0)} 篇文章"
        }

    async def get_recent_briefings(self, days: int = 7) -> dict:
        """获取最近的简报"""
        async with async_session_maker() as session:
            briefings = await BriefingCRUD.get_recent_briefings(session, limit=days)

        return {
            "action": "get_recent_briefings",
            "briefings": [
                {
                    "date": str(b.date),
                    "total_articles": b.total_articles,
                    "html_path": b.html_path
                }
                for b in briefings
            ],
            "count": len(briefings)
        }

    async def get_today_articles(self) -> dict:
        """获取今日抓取的文章"""
        async with async_session_maker() as session:
            articles = await ArticleCRUD.get_articles_by_date(session, date.today())

        return {
            "action": "get_today_articles",
            "articles": [
                {
                    "title": a.title,
                    "source": a.source,
                    "url": a.url,
                    "score": a.score
                }
                for a in articles[:20]  # 限制20篇
            ],
            "count": len(articles)
        }

    async def test_notifications(self) -> dict:
        """测试通知推送"""
        logger.info("📧 测试通知推送...")
        result = test_notification()
        return {
            "action": "test_notifications",
            "result": result,
            "message": "✅ 通知测试完成"
        }

    async def get_system_status(self) -> dict:
        """获取系统状态"""
        return {
            "action": "get_system_status",
            "status": "running",
            "config": {
                "ai_provider": settings.AI_PROVIDER,
                "briefing_time": f"{settings.BRIEFING_HOUR:02d}:{settings.BRIEFING_MINUTE:02d}",
                "max_articles": settings.MAX_ARTICLES_PER_SOURCE,
                "telegram_enabled": bool(settings.TELEGRAM_BOT_TOKEN),
                "email_enabled": bool(settings.SMTP_HOST)
            },
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """主函数 - 处理命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description="每日科技简报生成系统 - Claude Agent Skill")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["generate", "recent", "today", "test", "status"],
                       help="命令: generate(生成简报), recent(最近简报), today(今日文章), test(测试通知), status(系统状态)")

    args = parser.parse_args()
    skill = BriefingSkill()

    # 执行对应命令
    if args.command == "generate":
        result = await skill.generate_briefing()
    elif args.command == "recent":
        result = await skill.get_recent_briefings()
    elif args.command == "today":
        result = await skill.get_today_articles()
    elif args.command == "test":
        result = await skill.test_notifications()
    else:  # status
        result = await skill.get_system_status()

    # 输出结果
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
