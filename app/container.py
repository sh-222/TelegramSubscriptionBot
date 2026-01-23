from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import Redis, from_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from structlog import get_logger

from app.bot.middlewares.request import RetryRequestMiddleware
from app.config import settings

logger = get_logger()


# create container class for aiogram and sqlalchemy
class Container:
    def __init__(self):
        self.bot = Bot(
            token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        self.bot.session.middleware.register(RetryRequestMiddleware())

        self.dp = Dispatcher(storage=MemoryStorage())

        self.engine: AsyncEngine = create_async_engine(
            str(settings.POSTGRES_DSN), echo=False, future=True
        )
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.redis: Redis = from_url(
            str(settings.REDIS_DSN), encoding="utf-8", decode_responses=True
        )

    async def dispose(self):
        await self.bot.session.close()
        await self.engine.dispose()
        await self.redis.close()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with self.session_factory() as session:
            yield session
