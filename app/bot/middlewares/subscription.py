import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.enums import ChatType, ChatMemberStatus
from structlog import get_logger

from app.services.subscription import SubscriptionService
from app.storage.repositories.channels import ChannelRepository
from app.bot.keyboards.subscription import get_subscription_keyboard

logger = get_logger()

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        
        if event.chat.type == ChatType.PRIVATE:
            return await handler(event, data)

        user = event.from_user
        if not user or user.is_bot:
            return await handler(event, data)

        bot = data["bot"]
        try:
            chat_member = await bot.get_chat_member(event.chat.id, user.id)
            if chat_member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR):
                return await handler(event, data)
        except Exception:
            pass

        session = data["session"]
        redis_client = data["redis"]
        
        repo = ChannelRepository(session)
        channels = await repo.get_all_channels()
        
        if not channels:
            return await handler(event, data)

        service = SubscriptionService(redis_client, bot)
        missing_channels = await service.check_user_subscription(user.id, channels)

        if not missing_channels:
             return await handler(event, data)

        try:
            await event.delete()
        except Exception as e:
            logger.warning("Failed to delete user message", error=str(e))

        keyboard = get_subscription_keyboard(missing_channels)
        warning_msg = await event.answer(
            f"Привет, {user.full_name}!\nДля общения в чате подпишись на наши каналы:",
            reply_markup=keyboard
        )

        asyncio.create_task(self._delete_later(warning_msg, 10)) # delete warning message after 'n(int)'seconds
        return

    async def _delete_later(self, message: Message, delay: int):
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except Exception:
            pass
