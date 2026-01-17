"""
AI服务基类
定义AI服务的通用接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from app.models.article import Article, AIAnalysisResult


class AIServiceBase(ABC):
    """AI服务基类"""

    def __init__(self):
        self.name = "base"

    @abstractmethod
    async def analyze_article(self, article: Article) -> AIAnalysisResult:
        """
        分析单篇文章
        :param article: 文章对象
        :return: AI分析结果
        """
        pass

    @abstractmethod
    async def summarize_articles(
        self,
        articles: List[Article],
        max_summary_length: int = 500
    ) -> Dict[str, Any]:
        """
        批量总结文章并生成趋势分析
        :param articles: 文章列表
        :param max_summary_length: 最大摘要长度
        :return: 包含summary, trending_topics, category等的字典
        """
        pass

    @abstractmethod
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        提取关键词
        :param text: 文本内容
        :param max_keywords: 最大关键词数
        :return: 关键词列表
        """
        pass

    @abstractmethod
    async def categorize_article(self, article: Article) -> str:
        """
        对文章进行分类
        :param article: 文章对象
        :return: 分类标签
        """
        pass

    def _build_article_context(self, article: Article) -> str:
        """构建文章上下文"""
        return f"""
标题: {article.title}
来源: {article.source}
内容: {article.content or article.url}
"""
