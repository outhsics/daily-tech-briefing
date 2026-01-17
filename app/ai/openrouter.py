"""
OpenRouter AI服务实现
支持多种大模型通过OpenRouter API
"""
import json
from typing import List, Dict, Any
import aiohttp

from app.ai.base import AIServiceBase
from app.ai.prompts import ZHIPU_PROMPTS
from app.models.article import Article, AIAnalysisResult
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenRouterAIService(AIServiceBase):
    """OpenRouter AI服务实现"""

    def __init__(self):
        super().__init__()
        self.name = "openrouter"
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"
        # 默认使用高质量的模型
        self.model = getattr(settings, 'OPENROUTER_MODEL', 'anthropic/claude-3-haiku:beta')

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """调用OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://daily-tech-briefing.local",
                "X-Title": "Daily Tech Briefing"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"API error: {response.status}")

                    data = await response.json()
                    return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            raise

    async def analyze_article(self, article: Article) -> AIAnalysisResult:
        """分析单篇文章"""
        try:
            prompt = ZHIPU_PROMPTS["analyze_article"].format(
                article=self._build_article_context(article)
            )

            messages = [
                {"role": "system", "content": "你是一个专业的科技资讯分析师。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages)

            # 解析JSON响应
            try:
                # 尝试提取JSON部分
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

                result = json.loads(response)
                return AIAnalysisResult(
                    summary=result.get("summary", response[:200]),
                    keywords=result.get("keywords", []),
                    category=result.get("category"),
                    sentiment=result.get("sentiment"),
                    score=result.get("score", 0.5)
                )
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回基础结果
                return AIAnalysisResult(
                    summary=response[:200] if len(response) > 50 else response,
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
            # 构建文章列表上下文
            articles_context = "\n\n".join([
                f"{i+1}. {article.title}\n   {article.content or article.url}"
                for i, article in enumerate(articles[:20])
            ])

            prompt = ZHIPU_PROMPTS["summarize_articles"].format(
                articles=articles_context,
                max_length=max_summary_length,
                count=len(articles)
            )

            messages = [
                {"role": "system", "content": "你是一个专业的科技资讯分析师。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages, temperature=0.5)

            # 解析响应
            try:
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()

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
            prompt = f"请从以下文本中提取{max_keywords}个最重要的技术关键词，只返回关键词列表，用逗号分隔：\n\n{text[:500]}"

            messages = [
                {"role": "system", "content": "你是一个专业的关键词提取助手。"},
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
            prompt = ZHIPU_PROMPTS["categorize_article"].format(
                title=article.title,
                content=article.content or article.url
            )

            messages = [
                {"role": "system", "content": "你是一个专业的文章分类助手。"},
                {"role": "user", "content": prompt}
            ]

            response = await self._call_api(messages, temperature=0.3, max_tokens=100)
            return response.strip()

        except Exception as e:
            logger.error(f"Error categorizing article: {e}")
            return "科技"
