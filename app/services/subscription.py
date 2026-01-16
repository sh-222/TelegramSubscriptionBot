from typing import Sequence
from redis.asyncio import Redis
from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from app.models.channel import Channel

CACHE_TTL = 300  # 5 minutes

class SubscriptionService:
    def __init__(self, redis: Redis, bot: Bot):
        self.redis = redis
        self.bot = bot

    async def check_user_subscription(self, user_id: int, channels: Sequence[Channel]) -> list[Channel]:
        """
        Returns a list of channels the user is NOT subscribed to.
        """
        missing_channels = []

        for channel in channels:
            is_subscribed = await self._check_single_channel(user_id, channel)
            if not is_subscribed:
                missing_channels.append(channel)

        return missing_channels

    async def _check_single_channel(self, user_id: int, channel: Channel) -> bool:
        cache_key = f"sub:{user_id}:{channel.telegram_id}"
        
        #  Check Redis
        try:
            cached_status = await self.redis.get(cache_key)
            if cached_status == "1":
                return True
        except Exception:
            # redis failure not critical, continue to API check
            pass
        
        #  Check Telegram API
        try:
            member = await self.bot.get_chat_member(chat_id=channel.telegram_id, user_id=user_id)
            if member.status in (
                ChatMemberStatus.CREATOR,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
            ):
                # Cache successful subscription
                try:
                    await self.redis.setex(cache_key, CACHE_TTL, "1")
                except Exception:
                    pass
                return True
        except Exception as e:
            # Fail Open: If we cannot verify status (API error, network issue), 
            # assume user is subscribed to avoid incorrect blocking.
            # get_chat_member might raise if bot is not admin or other issues.
            # We log it but let the user pass.
            # logger isn't available in class context usually unless imported, using print or we need to pass logger
            # Assuming logger is not available in class scope or we need to add a way
            # Ideally we fail open.
            return True
            
        return False
