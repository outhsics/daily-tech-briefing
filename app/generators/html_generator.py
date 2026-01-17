"""
HTML页面生成器
使用Jinja2模板生成静态HTML页面
"""
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.article import Article, BriefingData
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HTMLGenerator:
    """HTML页面生成器"""

    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_briefing(
        self,
        briefing_data: BriefingData,
        filename: str = None
    ) -> str:
        """
        生成简报HTML页面
        :param briefing_data: 简报数据
        :param filename: 输出文件名，默认为日期.html
        :return: 生成的HTML文件路径
        """
        try:
            # 生成文件名
            if not filename:
                filename = f"{briefing_data.date}.html"

            output_path = self.output_dir / filename

            # 按来源分组文章
            articles_by_source = self._group_by_source(briefing_data.articles)

            # 数据源名称映射
            source_names = {
                "v2ex": "V2EX",
                "hackernews": "Hacker News",
                "36kr": "36氪",
                "sspai": "少数派",
                "huxiu": "虎嗅",
                "infoq": "InfoQ",
                "oschina": "开源中国",
                "solidot": "Solidot"
            }

            # 渲染模板
            template = self.env.get_template("briefing.html")
            html_content = template.render(
                title=settings.BRIEFING_TITLE,
                date=briefing_data.date.strftime("%Y年%m月%d日"),
                summary=briefing_data.summary,
                trending_topics=briefing_data.trending_topics,
                articles_by_source=articles_by_source,
                source_names=source_names,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Generated briefing: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            raise

    def _group_by_source(self, articles: List[Article]) -> Dict[str, List[Article]]:
        """按来源分组文章"""
        grouped = {}
        for article in articles:
            source = article.source
            if source not in grouped:
                grouped[source] = []
            grouped[source].append(article)

        # 按分数排序
        for source in grouped:
            grouped[source].sort(key=lambda x: x.score, reverse=True)

        return grouped

    def generate_index(self, briefings: List[str]) -> str:
        """
        生成索引页面
        :param briefings: 简报文件列表
        :return: 索引页面路径
        """
        try:
            output_path = self.output_dir / "index.html"

            template = self.env.get_template("index.html")
            html_content = template.render(
                briefings=sorted(briefings, reverse=True),
                title=settings.BRIEFING_TITLE
            )

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"Generated index: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating index: {e}")
            raise
