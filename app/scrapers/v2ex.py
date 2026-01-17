"""
V2EX 爬虫实现
"""
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup, Tag

from app.scrapers.base import BaseScraper
from app.models.article import ScrapedArticle
from app.utils.logger import get_logger

logger = get_logger(__name__)


class V2EXScraper(BaseScraper):
    """V2EX技术社区爬虫"""

    def __init__(self):
        super().__init__()
        self.name = "v2ex"
        self.base_url = "https://www.v2ex.com"
        self.api_url = f"{self.base_url}/api/topics/hot.json"

    async def fetch(self, limit: int = 10) -> List[ScrapedArticle]:
        """抓取V2EX热门话题"""
        articles = []

        try:
            # V2EX提供API接口
            content = await self._fetch(self.api_url)
            if not content:
                return articles

            import json
            data = json.loads(content)

            for item in data[:limit]:
                try:
                    article = ScrapedArticle(
                        title=self._clean_text(item.get("title", "")),
                        url=f"{self.base_url}/t/{item.get('id')}",
                        source=self.name,
                        content=self._clean_text(item.get("content", "")),
                        published_at=datetime.fromtimestamp(item.get("created", 0)),
                        author=item.get("member", {}).get("username"),
                        tags=item.get("node", {}).get("title", "").split(",") if item.get("node") else []
                    )
                    articles.append(article)
                    logger.debug(f"Parsed article: {article.title[:50]}")
                except Exception as e:
                    logger.error(f"Error parsing V2EX article: {e}")
                    continue

            logger.info(f"Fetched {len(articles)} articles from V2EX")

        except Exception as e:
            logger.error(f"Error fetching V2EX: {e}")

        return articles

    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        from bs4 import BeautifulSoup
        return BeautifulSoup(text, "html.parser").get_text(strip=True)
