from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.container import Container


class ContainerMiddleware(BaseMiddleware):
    def __init__(self, container: Container):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["redis"] = self.container.redis
        data["bot"] = self.container.bot

        async with self.container.session() as session:
            data["session"] = session
            return await handler(event, data)
