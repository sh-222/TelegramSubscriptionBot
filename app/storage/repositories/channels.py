from typing import List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel


# queries to db
class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active_channels(self) -> list[Channel]:
        """
        Retrieve all channels from the database.
        Note: logic simplified, treated same as get_all_channels since we do hard deletes.

        Returns:
            list[Channel]: List of Channel objects
        """
        return await self.get_all_channels()

    async def get_all_channels(self) -> list[Channel]:
        """
        Retrieve all channels from the database.

        Returns:
            list[Channel]: List of all Channel objects
        """
        stmt = select(Channel)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_channel(
        self,
        *,
        telegram_id: int,
        title: str,
        invite_link: str | None = None,
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
        else:
            # Создаем новый канал
            channel = Channel(
                telegram_id=telegram_id,
                title=title,
                invite_link=invite_link,
            )
            self._session.add(channel)

        await self._session.commit()
        await self._session.refresh(channel)
        return channel

    async def delete_channel(self, telegram_id: int) -> bool:
        stmt = delete(Channel).where(Channel.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0
