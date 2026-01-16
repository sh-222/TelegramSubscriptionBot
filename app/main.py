import asyncio
from typing import Any, Awaitable, Callable, Dict  # noqa: UP035

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.bot.middlewares.subscription import SubscriptionMiddleware
from app.bot.routers import admin, messages
from app.container import Container
from app.logging import setup_logging


class ContainerMiddleware(BaseMiddleware):
    def __init__(self, container: Container):
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["redis"] = self.container.redis
        data["bot"] = self.container.bot

        async with self.container.session() as session:
            data["session"] = session
            return await handler(event, data)


async def main():
    setup_logging()

    container = Container()

    try:
        # Middlewares
        container.dp.update.outer_middleware(ContainerMiddleware(container))
        container.dp.message.middleware(SubscriptionMiddleware())

        # Routers
        container.dp.include_router(admin.router)
        container.dp.include_router(messages.router)

        # Start
        await container.bot.delete_webhook(drop_pending_updates=True)
        await container.dp.start_polling(container.bot)

    finally:
        await container.dispose()


if __name__ == "__main__":
    asyncio.run(main())
