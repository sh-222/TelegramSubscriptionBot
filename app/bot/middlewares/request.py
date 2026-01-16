import asyncio
from typing import Any, Callable

from aiogram import Bot
from aiogram.client.session.middlewares.base import BaseRequestMiddleware
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods import TelegramMethod
from aiogram.methods.base import TelegramType
from structlog import get_logger

logger = get_logger()


class RetryRequestMiddleware(BaseRequestMiddleware):
    """Retry requests on TelegramNetworkError"""

    def __init__(self, max_retries: int = 3, sleep_time: float = 1.0):
        self.max_retries = max_retries
        self.sleep_time = sleep_time

    async def __call__(
        self,
        make_request: Callable[[Bot, TelegramMethod[TelegramType]], Any],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Any:
        """Call the request with retry logic"""
        for attempt in range(1, self.max_retries + 1):
            try:
                return await make_request(bot, method)
            except TelegramNetworkError as e:
                # If last attempt, raise
                if attempt == self.max_retries:
                    raise e

                logger.warning(
                    "Request failed, retrying",
                    method=method.__class__.__name__,
                    attempt=attempt,
                    max_retries=self.max_retries,
                    error=str(e),
                )
                await asyncio.sleep(self.sleep_time)
