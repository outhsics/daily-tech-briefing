"""
爬虫模块初始化
导出所有爬虫类
"""
from app.scrapers.v2ex import V2EXScraper
from app.scrapers.hackernews import HackerNewsScraper
from app.scrapers.thirty36 import Thirty36Scraper

# 所有可用的爬虫
SCRAPERS = {
    "v2ex": V2EXScraper,
    "hackernews": HackerNewsScraper,
    "36kr": Thirty36Scraper,
}


async def fetch_all_sources(limit: int = 10) -> dict:
    """
    并发抓取所有数据源
    :param limit: 每个数据源的最大文章数
    :return: dict, key为数据源名称，value为文章列表
    """
    results = {}
    from app.utils.logger import get_logger
    logger = get_logger(__name__)

    async def fetch_source(name: str, scraper_class, limit: int):
        """抓取单个数据源"""
        try:
            scraper = scraper_class()
            await scraper.__aenter__()
            articles = await scraper.fetch(limit)
            await scraper.__aexit__(None, None, None)
            return articles
        except Exception as e:
            logger.error(f"Error fetching {name}: {e}")
            return []

    # 并发抓取所有数据源
    import asyncio
    tasks = []
    scraper_names = []

    for name, scraper_class in SCRAPERS.items():
        scraper_names.append(name)
        task = fetch_source(name, scraper_class, limit)
        tasks.append(task)

    articles_lists = await asyncio.gather(*tasks)

    for name, articles in zip(scraper_names, articles_lists):
        results[name] = articles if articles else []

    return results
