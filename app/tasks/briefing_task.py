"""
Celery定时任务
生成每日科技简报
"""
from datetime import date, datetime
from celery import Celery, shared_task
from celery.schedules import crontab

from app.config import settings
from app.scrapers import fetch_all_sources
from app.ai import get_ai_service
from app.generators.html_generator import HTMLGenerator
from app.notifiers.telegram import TelegramNotifier
from app.notifiers.email import EmailNotifier
from app.database.crud import ArticleCRUD, BriefingCRUD
from app.models.article import BriefingData, ArticleCreate
from app.database import async_session_maker
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建Celery应用
celery_app = Celery(
    "briefing",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    # 定时任务配置
    beat_schedule={
        'daily-briefing': {
            'task': 'app.tasks.briefing_task.generate_daily_briefing',
            'schedule': crontab(hour=settings.BRIEFING_HOUR, minute=settings.BRIEFING_MINUTE),
        },
    }
)


@shared_task(name="generate_daily_briefing")
def generate_daily_briefing():
    """
    生成每日科技简报
    这是主要的定时任务
    """
    import asyncio
    return asyncio.run(_generate_daily_briefing_async())


async def _generate_daily_briefing_async():
    """异步执行简报生成任务"""
    start_time = datetime.now()
    logger.info("Starting daily briefing generation...")

    try:
        # 1. 数据采集
        logger.info("Step 1: Fetching articles from sources...")
        scraped_data = await fetch_all_sources(limit=settings.MAX_ARTICLES_PER_SOURCE)

        all_articles = []
        for source, articles in scraped_data.items():
            logger.info(f"Fetched {len(articles)} articles from {source}")
            all_articles.extend(articles)

        if not all_articles:
            logger.warning("No articles fetched, aborting")
            return {"status": "failed", "reason": "no articles"}

        # 2. 保存到数据库
        logger.info("Step 2: Saving articles to database...")
        async with async_session_maker() as session:
            article_creates = [
                ArticleCreate(
                    title=a.title,
                    url=a.url,
                    source=a.source,
                    content=a.content,
                    published_at=a.published_at
                )
                for a in all_articles
            ]
            result = await ArticleCRUD.batch_create_articles(session, article_creates)
            logger.info(f"Created {result['created']}, skipped {result['skipped']} articles")

            # 3. 获取今日文章
            today_articles = await ArticleCRUD.get_articles_by_date(session, date.today())

        # 4. AI分析
        logger.info("Step 3: Analyzing articles with AI...")
        ai_service = get_ai_service()

        # 为每篇文章生成摘要和关键词
        for article in today_articles:
            if not article.summary:
                try:
                    analysis = await ai_service.analyze_article(article)
                    async with async_session_maker() as session:
                        await ArticleCRUD.update_article_summary(
                            session,
                            article.id,
                            analysis.summary,
                            analysis.keywords,
                            analysis.score
                        )
                except Exception as e:
                    logger.error(f"Error analyzing article {article.id}: {e}")

        # 5. 生成总体摘要
        logger.info("Step 4: Generating overall summary...")
        summary_result = await ai_service.summarize_articles(today_articles)

        # 6. 生成HTML页面
        logger.info("Step 5: Generating HTML page...")
        generator = HTMLGenerator()

        briefing_data = BriefingData(
            date=date.today(),
            articles=today_articles[:50],  # 限制50篇
            trending_topics=summary_result.get("trending_topics", []),
            summary=summary_result.get("summary", "")
        )

        html_path = generator.generate_briefing(briefing_data)

        # 7. 保存简报记录
        logger.info("Step 6: Saving briefing record...")
        async with async_session_maker() as session:
            briefing = await BriefingCRUD.create_briefing(
                session,
                {
                    "date": date.today(),
                    "total_articles": len(today_articles),
                    "html_path": html_path
                }
            )

        # 8. 推送通知
        logger.info("Step 7: Sending notifications...")

        # Telegram
        if settings.TELEGRAM_BOT_TOKEN:
            telegram_notifier = TelegramNotifier()
            await telegram_notifier.send_briefing(
                title=f"{settings.BRIEFING_TITLE} - {date.today()}",
                summary=summary_result.get("summary", "")[:200],
                url=html_path,
                articles_count=len(today_articles)
            )

        # Email
        if settings.SMTP_HOST:
            email_notifier = EmailNotifier()
            await email_notifier.send_briefing(
                title=f"{settings.BRIEFING_TITLE} - {date.today()}",
                summary=summary_result.get("summary", "")[:200],
                url=html_path,
                articles_count=len(today_articles)
            )

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Daily briefing generated successfully in {elapsed:.2f}s")

        return {
            "status": "success",
            "articles_count": len(today_articles),
            "html_path": html_path,
            "elapsed": elapsed
        }

    except Exception as e:
        logger.error(f"❌ Error generating daily briefing: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e)
        }


@shared_task(name="manual_trigger_briefing")
def manual_trigger_briefing():
    """手动触发简报生成"""
    logger.info("Manual briefing generation triggered")
    return generate_daily_briefing()


@shared_task(name="test_notification")
def test_notification():
    """测试通知推送"""
    import asyncio
    return asyncio.run(_test_notification_async())


async def _test_notification_async():
    """异步执行通知测试"""
    logger.info("Testing notifications...")

    # Test Telegram
    if settings.TELEGRAM_BOT_TOKEN:
        telegram_notifier = TelegramNotifier()
        success = await telegram_notifier.test_connection()
        logger.info(f"Telegram test: {'✅ Success' if success else '❌ Failed'}")

    # Test Email
    if settings.SMTP_HOST:
        email_notifier = EmailNotifier()
        success = await email_notifier.send_email(
            subject="测试邮件",
            html_content="<h1>测试成功</h1><p>这是一封测试邮件。</p>"
        )
        logger.info(f"Email test: {'✅ Success' if success else '❌ Failed'}")

    return {"status": "tested"}
