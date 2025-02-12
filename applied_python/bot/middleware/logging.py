import logging
from aiogram import BaseMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        message = event.message if hasattr(event, "message") else None
        if message:
            user_id = message.from_user.id
            text = message.text or "Нет текста"
        logger.info(f"{user_id} отправил: {text}")

        return await handler(event, data)
