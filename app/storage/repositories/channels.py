from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel


# queries to db
class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_channels(self) -> list[Channel]:
        """
        Retrieve all active channels from the database.

        Returns:
            list[Channel]: List of active Channel objects
        """
        stmt = select(Channel).where(Channel.is_active.is_(True))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_channels(self) -> list[Channel]:
        """
        Retrieve all channels from the database regardless of active status.

        Returns:
            list[Channel]: List of all Channel objects
        """
        stmt = select(Channel)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_channel(
        self,
        *,
        telegram_id: str,
        title: str,
        invite_link: str | None = None,
        channel_username: str | None = None,
        added_by: int,
    ) -> Channel:
        # Сначала попробуем найти существующий канал
        stmt = select(Channel).where(Channel.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        channel = result.scalar_one_or_none()

        if channel:
            # Обновляем существующий канал
            channel.title = title
            if invite_link:
                channel.invite_link = invite_link
            if channel_username:
                channel.channel_username = channel_username
        else:
            # Создаем новый канал
            channel = Channel(
                telegram_id=telegram_id,
                title=title,
                invite_link=invite_link,
                channel_username=channel_username,
                added_by=added_by,
            )
            self._session.add(channel)

        await self._session.commit()
        await self._session.refresh(channel)
        return channel

    async def delete_channel(self, telegram_id: str) -> bool:
        stmt = update(Channel).where(Channel.telegram_id == telegram_id).values(is_active=False)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0
