"""
Hacker News 爬虫实现
"""
from typing import List, Optional
from datetime import datetime
import asyncio
import json

from app.scrapers.base import BaseScraper
from app.models.article import ScrapedArticle
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HackerNewsScraper(BaseScraper):
    """Hacker News爬虫"""

    def __init__(self):
        super().__init__()
        self.name = "hackernews"
        self.base_url = "https://news.ycombinator.com"
        self.api_url = "https://hacker-news.firebaseio.com/v0"

    async def fetch(self, limit: int = 10) -> List[ScrapedArticle]:
        """抓取Hacker News首页文章"""
        articles = []

        try:
            # 获取Top stories IDs
            top_stories_url = f"{self.api_url}/topstories.json"
            content = await self._fetch(top_stories_url)

            if not content:
                return articles

            story_ids = json.loads(content)[:limit]

            # 并发获取每篇文章详情
            tasks = [self._fetch_story_detail(story_id) for story_id in story_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, ScrapedArticle):
                    articles.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error fetching story: {result}")

            logger.info(f"Fetched {len(articles)} articles from Hacker News")

        except Exception as e:
            logger.error(f"Error fetching Hacker News: {e}")

        return articles

    async def _fetch_story_detail(self, story_id: int) -> Optional[ScrapedArticle]:
        """获取单篇文章详情"""
        try:
            story_url = f"{self.api_url}/item/{story_id}.json"
            content = await self._fetch(story_url)

            if not content:
                return None

            data = json.loads(content)

            article = ScrapedArticle(
                title=data.get("title", ""),
                url=data.get("url", f"{self.base_url}/item?id={story_id}"),
                source=self.name,
                content=None,
                published_at=datetime.fromtimestamp(data.get("time", 0)) if data.get("time") else None,
                author=data.get("by"),
                tags=[data.get("type")] if data.get("type") else []
            )

            return article

        except Exception as e:
            logger.error(f"Error fetching story {story_id}: {e}")
            return None
