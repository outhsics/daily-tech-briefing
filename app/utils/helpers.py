"""
辅助工具函数
"""
import hashlib
from typing import Optional
from datetime import datetime


def generate_url_hash(url: str) -> str:
    """生成URL哈希"""
    return hashlib.md5(url.encode()).hexdigest()


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M") -> str:
    """格式化日期时间"""
    if not dt:
        return ""
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_list_get(lst: list, index: int, default=None):
    """安全获取列表元素"""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return default
