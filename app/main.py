"""
FastAPI应用入口
提供RESTful API接口
"""
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from datetime import date
from typing import List

from app.config import settings
from app.database import init_db
from app.database.crud import BriefingCRUD, ArticleCRUD
from app.database import async_session_maker
from app.models.article import Briefing, Article
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="每日科技简报生成系统 API"
)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info(f"Starting {settings.APP_NAME}...")
    await init_db()
    logger.info("Application started successfully")


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/api/briefings/recent", response_model=List[Briefing])
async def get_recent_briefings(limit: int = 7):
    """获取最近的简报"""
    async with async_session_maker() as session:
        briefings = await BriefingCRUD.get_recent_briefings(session, limit)
    return briefings


@app.get("/api/briefings/{date_str}", response_model=Briefing)
async def get_briefing_by_date(date_str: str):
    """获取指定日期的简报"""
    try:
        target_date = date.fromisoformat(date_str)
        async with async_session_maker() as session:
            briefing = await BriefingCRUD.get_briefing_by_date(session, target_date)
        if not briefing:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Briefing not found")
        return briefing
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid date format")


@app.get("/api/articles/today", response_model=List[Article])
async def get_today_articles():
    """获取今日文章"""
    async with async_session_maker() as session:
        articles = await ArticleCRUD.get_articles_by_date(session, date.today())
    return articles


@app.get("/api/articles/source/{source}", response_model=List[Article])
async def get_articles_by_source(source: str, limit: int = 10):
    """获取指定来源的文章"""
    async with async_session_maker() as session:
        articles = await ArticleCRUD.get_articles_by_source(session, source, limit)
    return articles


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
