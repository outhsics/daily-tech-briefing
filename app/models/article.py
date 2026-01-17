"""
数据模型定义
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Date, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

Base = declarative_base()


# SQLAlchemy ORM模型
class ArticleORM(Base):
    """文章表ORM模型"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    keywords = Column(PG_ARRAY(String), nullable=True)
    published_at = Column(DateTime, nullable=True)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class BriefingORM(Base):
    """简报表ORM模型"""
    __tablename__ = "briefings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    total_articles = Column(Integer, default=0)
    html_path = Column(String(500), nullable=True)
    sent_telegram = Column(Boolean, default=False)
    sent_email = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic模型用于API
class ArticleBase(BaseModel):
    """文章基础模型"""
    title: str = Field(..., max_length=500, description="文章标题")
    url: str = Field(..., max_length=1000, description="文章URL")
    source: str = Field(..., max_length=50, description="数据源")
    content: Optional[str] = Field(None, description="文章内容")
    published_at: Optional[datetime] = Field(None, description="发布时间")


class ArticleCreate(ArticleBase):
    """创建文章模型"""
    pass


class ArticleUpdate(BaseModel):
    """更新文章模型"""
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    score: Optional[float] = None


class Article(ArticleBase):
    """文章响应模型"""
    id: int
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    score: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class BriefingBase(BaseModel):
    """简报基础模型"""
    briefing_date: date = Field(..., description="简报日期", alias="date")
    total_articles: int = Field(default=0, description="文章总数")

    class Config:
        populate_by_name = True


class BriefingCreate(BriefingBase):
    """创建简报模型"""
    html_path: Optional[str] = None


class Briefing(BriefingBase):
    """简报响应模型"""
    id: int
    html_path: Optional[str] = None
    sent_telegram: bool
    sent_email: bool
    created_at: datetime

    class Config:
        from_attributes = True


# 用于爬虫返回的数据模型
class ScrapedArticle(BaseModel):
    """爬取的文章数据"""
    title: str
    url: str
    source: str
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None


# AI分析结果模型
class AIAnalysisResult(BaseModel):
    """AI分析结果"""
    summary: str
    keywords: List[str]
    category: Optional[str] = None
    sentiment: Optional[str] = None
    score: float = 0.0


# 简报数据模型
class BriefingData(BaseModel):
    """简报生成数据"""
    date: date
    articles: List[Article]
    trending_topics: List[str]
    summary: str
