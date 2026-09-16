import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_line_notify(message: str, token: str = None) -> bool:
    """
    Sends a notification message via LINE Notify.
    """
    # In a real app, token would be fetched from settings or user preferences
    # token = token or settings.LINE_NOTIFY_TOKEN
    
    if not token:
        logger.warning("No LINE Notify token provided. Notification skipped.")
        return False
        
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"message": message}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Failed to send LINE notification: {e}")
        return False

async def send_email_notification(to_email: str, subject: str, html_content: str) -> bool:
    """
    Sends an email notification. 
    (Mock implementation - integrate with SMTP or SendGrid here)
    """
    logger.info(f"Sending email to {to_email} | Subject: {subject}")
    # SMTP logic goes here
    return True
