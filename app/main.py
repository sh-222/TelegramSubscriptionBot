import asyncio

from app.bot.middlewares.container import ContainerMiddleware
from app.bot.middlewares.subscription import SubscriptionMiddleware
from app.bot.routers import admin
from app.container import Container
from app.logging import setup_logging


async def main():
    setup_logging()

    container = Container()

    try:
        container.dp.update.outer_middleware(ContainerMiddleware(container))
        container.dp.message.outer_middleware(SubscriptionMiddleware())
        container.dp.include_router(admin.router)

        await container.bot.delete_webhook(drop_pending_updates=True)
        await container.dp.start_polling(container.bot)

    finally:
        await container.dispose()


if __name__ == "__main__":
    asyncio.run(main())
