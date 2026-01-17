"""
通义千问AI服务实现
"""
import json
from typing import List, Dict, Any
import dashscope
from dashscope import Generation

from app.ai.base import AIServiceBase
from app.ai.prompts import QWEN_PROMPTS
from app.models.article import Article, AIAnalysisResult
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QwenAIService(AIServiceBase):
    """通义千问AI服务实现"""

    def __init__(self):
        super().__init__()
        self.name = "qwen"
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.DASHSCOPE_MODEL

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用通义千问API"""
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                result_format='message'
            )
            return response.output.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Qwen API: {e}")
            raise

    async def analyze_article(self, article: Article) -> AIAnalysisResult:
        """分析单篇文章"""
        try:
            prompt = QWEN_PROMPTS["analyze_article"].format(
                article=self._build_article_context(article)
            )

            messages = [
                {"role": "system", "content": "你是一个专业的科技资讯分析师。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages)

            # 尝试解析JSON
            try:
                result = json.loads(response)
                return AIAnalysisResult(
                    summary=result.get("summary", response[:200]),
                    keywords=result.get("keywords", []),
                    category=result.get("category"),
                    sentiment=result.get("sentiment"),
                    score=result.get("score", 0.5)
                )
            except json.JSONDecodeError:
                return AIAnalysisResult(
                    summary=response[:200],
                    keywords=[],
                    score=0.5
                )

        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return AIAnalysisResult(summary="", keywords=[], score=0.0)

    async def summarize_articles(
        self,
        articles: List[Article],
        max_summary_length: int = 500
    ) -> Dict[str, Any]:
        """批量总结文章"""
        try:
            articles_context = "\n\n".join([
                f"{i+1}. {article.title}\n   {article.content or article.url}"
                for i, article in enumerate(articles[:20])
            ])

            prompt = QWEN_PROMPTS["summarize_articles"].format(
                articles=articles_context
            )

            messages = [
                {"role": "system", "content": "你是一个专业的科技资讯分析师。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages, temperature=0.5)

            try:
                result = json.loads(response)
                return {
                    "summary": result.get("summary", response),
                    "trending_topics": result.get("trending_topics", []),
                    "category": result.get("category", "科技"),
                }
            except json.JSONDecodeError:
                return {
                    "summary": response,
                    "trending_topics": [],
                    "category": "科技"
                }

        except Exception as e:
            logger.error(f"Error summarizing articles: {e}")
            return {
                "summary": "无法生成摘要",
                "trending_topics": [],
                "category": "科技"
            }

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        try:
            prompt = f"请从以下文本中提取{max_keywords}个最重要的技术关键词，用逗号分隔：\n\n{text[:500]}"

            messages = [
                {"role": "system", "content": "你是专业的关键词提取助手。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages, temperature=0.3, max_tokens=200)
            keywords = [kw.strip() for kw in response.split(",")]
            return keywords[:max_keywords]

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

    async def categorize_article(self, article: Article) -> str:
        """对文章进行分类"""
        try:
            prompt = f"""请将以下文章分类到一个最合适的技术类别：

标题：{article.title}

可选类别：人工智能、移动开发、前端技术、后端开发、云计算、大数据、区块链、物联网、安全、产品设计、创业、其他

只返回类别名称。"""

            messages = [
                {"role": "system", "content": "你是专业的文章分类助手。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages, temperature=0.3, max_tokens=100)
            return response.strip()

        except Exception as e:
            logger.error(f"Error categorizing article: {e}")
            return "科技"
