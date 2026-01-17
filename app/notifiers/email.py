"""
邮件推送通知
"""
from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailNotifier:
    """邮件推送通知器"""

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.to_emails = settings.EMAIL_TO

    async def send_email(
        self,
        subject: str,
        html_content: str,
        to_emails: Optional[List[str]] = None
    ) -> bool:
        """
        发送邮件
        :param subject: 邮件主题
        :param html_content: HTML内容
        :param to_emails: 收件人列表
        :return: 是否发送成功
        """
        if not self.host or not self.from_email:
            logger.warning("Email not configured")
            return False

        recipients = to_emails or self.to_emails
        if not recipients:
            logger.warning("No recipients specified")
            return False

        try:
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = ", ".join(recipients)

            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                start_tls=True
            )

            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    async def send_briefing(
        self,
        title: str,
        summary: str,
        url: Optional[str] = None,
        articles_count: int = 0
    ) -> bool:
        """
        发送简报邮件
        :param title: 简报标题
        :param summary: 简报摘要
        :param url: 简报链接
        :param articles_count: 文章数量
        :return: 是否发送成功
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                a {{ color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    <h2>今日概览</h2>
                    <p>{summary}</p>
                    <p><strong>文章数量：</strong>{articles_count}</p>
                    {'<p><a href="' + url + '">查看完整简报</a></p>' if url else ''}
                </div>
                <div class="footer">
                    <p>由AI自动生成 | 每日科技简报</p>
                </div>
            </div>
        </body>
        </html>
        """

        subject = f"{title} - {summary[:30]}..."
        return await self.send_email(subject, html_content)
