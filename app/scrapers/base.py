"""
爬虫基类
定义爬虫的通用接口和功能
"""
import asyncio
import random
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup

from app.models.article import ScrapedArticle
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseScraper(ABC):
    """爬虫基类"""

    def __init__(self):
        self.name: str = "base"
        self.base_url: str = ""
        self.timeout: int = settings.SCRAPER_TIMEOUT
        self.max_retries: int = settings.SCRAPER_MAX_RETRIES
        self.delay: float = settings.SCRAPER_DELAY
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """进入上下文管理器"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self._get_headers()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "User-Agent": random.choice(settings.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    async def _fetch(self, url: str) -> Optional[str]:
        """获取页面内容"""
        for attempt in range(self.max_retries):
            try:
                # 添加延迟防止请求过快
                if attempt > 0:
                    await asyncio.sleep(self.delay * (attempt + 1))

                logger.debug(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                async with self.session.get(url) as response:
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"Successfully fetched {url}")
                        return content
                    elif response.status == 429:
                        # 速率限制，增加等待时间
                        wait_time = 5 * (attempt + 1)
                        logger.warning(f"Rate limited, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")

            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {url}")
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching {url}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}")

        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def _parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, "html.parser")

    @abstractmethod
    async def fetch(self, limit: int = 10) -> List[ScrapedArticle]:
        """
        抓取文章列表
        :param limit: 最大文章数
        :return: 文章列表
        """
        pass

    async def close(self):
        """关闭连接"""
        if self.session:
            await self.session.close()
