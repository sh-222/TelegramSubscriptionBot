from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.models.channel import Channel

class ChannelRepository:
    """Repository for managing channels"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_channel(self, telegram_id: int, title: str, invite_link: str | None) -> Channel:
        stmt = insert(Channel).values(
            telegram_id=telegram_id,
            title=title,
            invite_link=invite_link
        ).on_conflict_do_update(
            index_elements=[Channel.telegram_id],
            set_={"title": title, "invite_link": invite_link}
        ).returning(Channel)
        
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete_channel(self, telegram_id: int) -> None:
        stmt = delete(Channel).where(Channel.telegram_id == telegram_id)
        await self.session.execute(stmt)

    async def get_all_channels(self) -> Sequence[Channel]:
        stmt = select(Channel)
        result = await self.session.execute(stmt)
        return result.scalars().all()
