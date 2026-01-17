"""
36氪 爬虫实现
"""
from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
import asyncio

from app.scrapers.base import BaseScraper
from app.models.article import ScrapedArticle
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Thirty36Scraper(BaseScraper):
    """36氪爬虫"""

    def __init__(self):
        super().__init__()
        self.name = "36kr"
        self.base_url = "https://36kr.com"
        self.news_url = f"{self.base_url}/news"

    async def fetch(self, limit: int = 10) -> List[ScrapedArticle]:
        """抓取36氪快讯"""
        articles = []

        try:
            content = await self._fetch(self.news_url)
            if not content:
                return articles

            soup = self._parse_html(content)

            # 36氪的文章项选择器
            article_items = soup.select(".news-item")[:limit]

            for item in article_items:
                try:
                    article = self._parse_article(item)
                    if article:
                        articles.append(article)
                        logger.debug(f"Parsed article: {article.title[:50]}")
                except Exception as e:
                    logger.error(f"Error parsing article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from 36氪")

        except Exception as e:
            logger.error(f"Error fetching 36氪: {e}")

        return articles

    def _parse_article(self, item: Tag) -> Optional[ScrapedArticle]:
        """解析文章项"""
        try:
            # 标题和链接
            title_elem = item.select_one(".news-title a")
            if not title_elem:
                return None

            title = title_elem.get_text(strip=True)
            url = title_elem.get("href", "")

            if not url.startswith("http"):
                url = f"{self.base_url}{url}"

            # 摘要
            summary_elem = item.select_one(".news-summary")
            content = summary_elem.get_text(strip=True) if summary_elem else ""

            # 时间
            time_elem = item.select_one(".news-time")
            time_text = time_elem.get_text(strip=True) if time_elem else ""
            published_at = self._parse_time(time_text)

            return ScrapedArticle(
                title=title,
                url=url,
                source=self.name,
                content=content,
                published_at=published_at
            )

        except Exception as e:
            logger.error(f"Error parsing article item: {e}")
            return None

    def _parse_time(self, time_text: str) -> Optional[datetime]:
        """解析时间文本"""
        try:
            # 处理"2小时前"、"30分钟前"等格式
            if "小时前" in time_text:
                hours = int(time_text.replace("小时前", "").strip())
                return datetime.now() - timedelta(hours=hours)
            elif "分钟前" in time_text:
                minutes = int(time_text.replace("分钟前", "").strip())
                return datetime.now() - timedelta(minutes=minutes)
            elif "天前" in time_text:
                days = int(time_text.replace("天前", "").strip())
                return datetime.now() - timedelta(days=days)
        except Exception as e:
            logger.debug(f"Error parsing time '{time_text}': {e}")
        return None
