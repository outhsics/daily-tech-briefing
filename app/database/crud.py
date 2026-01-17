"""
数据库CRUD操作
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.models.article import ArticleORM, BriefingORM, Article, Briefing, ArticleCreate, BriefingCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(lambda: Base.metadata.create_all(engine))
    logger.info("Database initialized successfully")


# 文章CRUD操作
class ArticleCRUD:
    """文章CRUD操作类"""

    @staticmethod
    async def create_article(
        session: AsyncSession,
        article_data: ArticleCreate
    ) -> Optional[Article]:
        """创建文章"""
        try:
            article_orm = ArticleORM(**article_data.model_dump())
            session.add(article_orm)
            await session.commit()
            await session.refresh(article_orm)
            logger.info(f"Created article: {article_data.title[:50]}")
            return Article.from_orm(article_orm)
        except IntegrityError as e:
            await session.rollback()
            logger.warning(f"Article already exists: {article_data.url}")
            return None
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating article: {e}")
            return None

    @staticmethod
    async def get_article_by_url(
        session: AsyncSession,
        url: str
    ) -> Optional[Article]:
        """根据URL获取文章"""
        result = await session.execute(
            select(ArticleORM).where(ArticleORM.url == url)
        )
        article_orm = result.scalar_one_or_none()
        return Article.from_orm(article_orm) if article_orm else None

    @staticmethod
    async def get_articles_by_date(
        session: AsyncSession,
        date: date
    ) -> List[Article]:
        """获取指定日期的文章"""
        result = await session.execute(
            select(ArticleORM).where(
                func.date(ArticleORM.created_at) == date
            ).order_by(ArticleORM.score.desc())
        )
        articles = result.scalars().all()
        return [Article.from_orm(a) for a in articles]

    @staticmethod
    async def get_articles_by_source(
        session: AsyncSession,
        source: str,
        limit: int = 10
    ) -> List[Article]:
        """获取指定数据源的文章"""
        result = await session.execute(
            select(ArticleORM)
            .where(ArticleORM.source == source)
            .order_by(ArticleORM.score.desc())
            .limit(limit)
        )
        articles = result.scalars().all()
        return [Article.from_orm(a) for a in articles]

    @staticmethod
    async def get_recent_articles(
        session: AsyncSession,
        days: int = 1,
        limit: int = 100
    ) -> List[Article]:
        """获取最近几天的文章"""
        since_date = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(ArticleORM)
            .where(ArticleORM.created_at >= since_date)
            .order_by(ArticleORM.score.desc())
            .limit(limit)
        )
        articles = result.scalars().all()
        return [Article.from_orm(a) for a in articles]

    @staticmethod
    async def batch_create_articles(
        session: AsyncSession,
        articles: List[ArticleCreate]
    ) -> Dict[str, Any]:
        """批量创建文章"""
        created_count = 0
        skipped_count = 0
        errors = []

        for article_data in articles:
            try:
                # 检查是否已存在
                existing = await ArticleCRUD.get_article_by_url(session, article_data.url)
                if existing:
                    skipped_count += 1
                    continue

                article_orm = ArticleORM(**article_data.model_dump())
                session.add(article_orm)
                created_count += 1
            except Exception as e:
                errors.append(str(e))
                logger.error(f"Error creating article: {e}")

        try:
            await session.commit()
            logger.info(f"Batch created {created_count} articles, skipped {skipped_count}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error committing batch: {e}")

        return {
            "created": created_count,
            "skipped": skipped_count,
            "errors": errors
        }

    @staticmethod
    async def update_article_summary(
        session: AsyncSession,
        article_id: int,
        summary: str,
        keywords: List[str],
        score: float
    ) -> Optional[Article]:
        """更新文章摘要和分析结果"""
        try:
            result = await session.execute(
                select(ArticleORM).where(ArticleORM.id == article_id)
            )
            article_orm = result.scalar_one_or_none()
            if not article_orm:
                return None

            article_orm.summary = summary
            article_orm.keywords = keywords
            article_orm.score = score
            await session.commit()
            await session.refresh(article_orm)
            return Article.from_orm(article_orm)
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating article: {e}")
            return None


# 简报CRUD操作
class BriefingCRUD:
    """简报CRUD操作类"""

    @staticmethod
    async def create_briefing(
        session: AsyncSession,
        briefing_data: BriefingCreate
    ) -> Optional[Briefing]:
        """创建简报"""
        try:
            briefing_orm = BriefingORM(**briefing_data.model_dump())
            session.add(briefing_orm)
            await session.commit()
            await session.refresh(briefing_orm)
            logger.info(f"Created briefing for date: {briefing_data.date}")
            return Briefing.from_orm(briefing_orm)
        except IntegrityError:
            await session.rollback()
            logger.warning(f"Briefing already exists for date: {briefing_data.date}")
            return await BriefingCRUD.get_briefing_by_date(session, briefing_data.date)
        except Exception as e:
            await session.rollback()
            logger.error(f"Error creating briefing: {e}")
            return None

    @staticmethod
    async def get_briefing_by_date(
        session: AsyncSession,
        date: date
    ) -> Optional[Briefing]:
        """根据日期获取简报"""
        result = await session.execute(
            select(BriefingORM).where(BriefingORM.date == date)
        )
        briefing_orm = result.scalar_one_or_none()
        return Briefing.from_orm(briefing_orm) if briefing_orm else None

    @staticmethod
    async def update_briefing_status(
        session: AsyncSession,
        briefing_id: int,
        html_path: Optional[str] = None,
        sent_telegram: Optional[bool] = None,
        sent_email: Optional[bool] = None
    ) -> Optional[Briefing]:
        """更新简报状态"""
        try:
            result = await session.execute(
                select(BriefingORM).where(BriefingORM.id == briefing_id)
            )
            briefing_orm = result.scalar_one_or_none()
            if not briefing_orm:
                return None

            if html_path is not None:
                briefing_orm.html_path = html_path
            if sent_telegram is not None:
                briefing_orm.sent_telegram = sent_telegram
            if sent_email is not None:
                briefing_orm.sent_email = sent_email

            await session.commit()
            await session.refresh(briefing_orm)
            return Briefing.from_orm(briefing_orm)
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating briefing: {e}")
            return None

    @staticmethod
    async def get_recent_briefings(
        session: AsyncSession,
        limit: int = 30
    ) -> List[Briefing]:
        """获取最近的简报"""
        result = await session.execute(
            select(BriefingORM)
            .order_by(BriefingORM.date.desc())
            .limit(limit)
        )
        briefings = result.scalars().all()
        return [Briefing.from_orm(b) for b in briefings]
