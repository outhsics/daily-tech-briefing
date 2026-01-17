"""
Telegram推送通知
"""
from typing import Optional
import aiohttp
from telegram import Bot
from telegram.error import TelegramError

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramNotifier:
    """Telegram推送通知器"""

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.bot = Bot(token=self.token) if self.token else None

    async def send_message(
        self,
        message: str,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        发送文本消息
        :param message: 消息内容
        :param parse_mode: 解析模式（HTML/Markdown）
        :return: 是否发送成功
        """
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Telegram message sent successfully")
            return True
        except TelegramError as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_briefing(
        self,
        title: str,
        summary: str,
        url: Optional[str] = None,
        articles_count: int = 0
    ) -> bool:
        """
        发送简报通知
        :param title: 简报标题
        :param summary: 简报摘要
        :param url: 简报链接
        :param articles_count: 文章数量
        :return: 是否发送成功
        """
        message = f"""
📰 <b>{title}</b>

📊 {summary}

📝 文章数：{articles_count}
        """

        if url:
            message += f"\n\n🔗 查看完整简报：{url}"

        return await self.send_message(message)

    async def test_connection(self) -> bool:
        """测试Telegram连接"""
        if not self.bot or not self.chat_id:
            logger.warning("Telegram bot not configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ Telegram通知测试成功！"
            )
            return True
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
