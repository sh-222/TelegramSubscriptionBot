from aiogram import Router
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import Command, CommandObject, ChatMemberUpdatedFilter, PROMOTED_TRANSITION, KICKED, LEFT
from aiogram.enums import ChatType
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.storage.repositories.channels import ChannelRepository

router = Router()
logger = get_logger()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION))
async def on_bot_promoted(event: ChatMemberUpdated, session: AsyncSession):
    if event.chat.type != ChatType.CHANNEL:
        return

    logger.info("Bot promoted in channel", chat_id=event.chat.id, title=event.chat.title)
    repo = ChannelRepository(session)
    
    invite_link = None
    if event.chat.username:
        invite_link = f"https://t.me/{event.chat.username}"
    else:
        try:
            link_obj = await event.bot.create_chat_invite_link(event.chat.id, name="Subscription Bot Link")
            invite_link = link_obj.invite_link
        except Exception as e:
            logger.warning("Could not create invite link", error=str(e))
            
    await repo.upsert_channel(
        telegram_id=event.chat.id,
        title=event.chat.title or "Unknown Channel",
        invite_link=invite_link
    )
    await session.commit()

@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT))
async def on_bot_removed(event: ChatMemberUpdated, session: AsyncSession):
    if event.chat.type != ChatType.CHANNEL:
        return

    logger.info("Bot removed from channel", chat_id=event.chat.id)
    repo = ChannelRepository(session)
    await repo.delete_channel(event.chat.id)
    await session.commit()

@router.message(Command("channels"))
async def cmd_channels(message: Message, session: AsyncSession):
    repo = ChannelRepository(session)
    channels = await repo.get_all_channels()
    
    if not channels:
        await message.answer("Список каналов пуст.")
        return

    text = "<b>Список ваших каналов:</b>\n\n"
    for ch in channels:
        text += f"ID: <code>{ch.telegram_id}</code> | {ch.title}\n"
        
    await message.answer(text)

@router.message(Command("del_channel"))
async def cmd_del_channel(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.answer("Ошибка: не указан 'channel_id' \n"
                         "Использование: /del_channel 'channel_id'")
        return
        
    try:
        channel_id = int(command.args)
    except ValueError:
        await message.answer("Ошибка: 'channel_id' должен быть числом.")
        return

    repo = ChannelRepository(session)
    await repo.delete_channel(channel_id)
    await session.commit()
    
    await message.answer(f"Канал {channel_id} удален из БД.")


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для управления подписками на каналы.\n\n"
                         "Используйте команды:\n"
                         " /channels - список ваших каналов,\n"
                         "/del_channel 'channel_id' - удалить канал")