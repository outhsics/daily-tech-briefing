"""
数据库初始化
"""
from app.models.article import Base
from app.database.crud import engine, async_session_maker
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


__all__ = ["init_db", "async_session_maker", "engine"]
