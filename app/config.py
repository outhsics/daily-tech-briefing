"""
配置管理模块
使用 Pydantic Settings 进行配置验证
"""
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # 应用基础配置
    APP_NAME: str = "Daily Tech Briefing"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # 数据库配置
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/briefing_db",
        description="数据库连接URL"
    )

    # Redis配置
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis连接URL"
    )

    # Celery配置
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery结果存储URL"
    )

    # 定时任务配置
    BRIEFING_HOUR: int = Field(
        default=9,
        ge=0,
        le=23,
        description="每日简报生成时间（小时）"
    )
    BRIEFING_MINUTE: int = Field(
        default=0,
        ge=0,
        le=59,
        description="每日简报生成时间（分钟）"
    )

    # AI服务配置 - 智谱AI
    ZHIPUAI_API_KEY: Optional[str] = Field(
        default=None,
        description="智谱AI API密钥"
    )
    ZHIPUAI_MODEL: str = Field(
        default="glm-4",
        description="智谱AI模型名称"
    )

    # AI服务配置 - 通义千问
    DASHSCOPE_API_KEY: Optional[str] = Field(
        default=None,
        description="阿里云DashScope API密钥"
    )
    DASHSCOPE_MODEL: str = Field(
        default="qwen-turbo",
        description="通义千问模型名称"
    )

    # AI服务配置 - OpenRouter
    OPENROUTER_API_KEY: Optional[str] = Field(
        default=None,
        description="OpenRouter API密钥"
    )
    OPENROUTER_MODEL: str = Field(
        default="anthropic/claude-3-haiku:beta",
        description="OpenRouter模型名称"
    )

    # AI服务选择
    AI_PROVIDER: str = Field(
        default="zhipu",
        description="AI服务提供商: zhipu, qwen 或 openrouter"
    )

    @field_validator("AI_PROVIDER")
    @classmethod
    def validate_ai_provider(cls, v: str) -> str:
        if v not in ["zhipu", "qwen", "openrouter"]:
            raise ValueError("AI_PROVIDER must be 'zhipu', 'qwen' or 'openrouter'")
        return v

    # Telegram配置
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(
        default=None,
        description="Telegram Bot Token"
    )
    TELEGRAM_CHAT_ID: Optional[str] = Field(
        default=None,
        description="Telegram Chat ID"
    )

    # 邮件配置
    SMTP_HOST: Optional[str] = Field(
        default=None,
        description="SMTP服务器地址"
    )
    SMTP_PORT: int = Field(
        default=587,
        description="SMTP服务器端口"
    )
    SMTP_USER: Optional[str] = Field(
        default=None,
        description="SMTP用户名"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        default=None,
        description="SMTP密码"
    )
    EMAIL_FROM: Optional[str] = Field(
        default=None,
        description="发件人邮箱"
    )
    EMAIL_TO: List[str] = Field(
        default_factory=list,
        description="收件人邮箱列表"
    )

    # 爬虫配置
    SCRAPER_TIMEOUT: int = Field(
        default=30,
        ge=1,
        le=120,
        description="爬虫请求超时时间（秒）"
    )
    SCRAPER_MAX_RETRIES: int = Field(
        default=3,
        ge=1,
        le=10,
        description="爬虫最大重试次数"
    )
    SCRAPER_DELAY: float = Field(
        default=1.0,
        ge=0.1,
        description="爬虫请求间隔（秒）"
    )
    USER_AGENTS: List[str] = Field(
        default_factory=lambda: [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        ],
        description="User-Agent列表"
    )

    # 输出配置
    OUTPUT_DIR: str = Field(
        default="./output",
        description="简报输出目录"
    )
    LOG_DIR: str = Field(
        default="./logs",
        description="日志目录"
    )

    # 简报配置
    MAX_ARTICLES_PER_SOURCE: int = Field(
        default=10,
        ge=1,
        le=50,
        description="每个数据源最大文章数"
    )
    BRIEFING_TITLE: str = Field(
        default="每日科技简报",
        description="简报标题"
    )


# 全局配置实例
settings = Settings()
