"""
AI服务模块
提供统一的AI服务接口
"""
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_ai_service():
    """获取配置的AI服务实例"""
    provider = settings.AI_PROVIDER.lower()

    if provider == "zhipu":
        from app.ai.zhipu import ZhipuAIService
        return ZhipuAIService()
    elif provider == "qwen":
        from app.ai.qwen import QwenAIService
        return QwenAIService()
    elif provider == "openrouter":
        from app.ai.openrouter import OpenRouterAIService
        return OpenRouterAIService()
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")


__all__ = ["get_ai_service"]
