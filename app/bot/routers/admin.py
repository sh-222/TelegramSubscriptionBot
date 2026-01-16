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
            # Fetch full chat details to get the primary invite link
            chat_info = await event.bot.get_chat(event.chat.id)
            invite_link = chat_info.invite_link
            
            if not invite_link:
                # Create a permanent invite link (expire_date=None, member_limit=None)
                link_obj = await event.bot.create_chat_invite_link(
                    event.chat.id, 
                    name="Subscription Bot Link",
                    expire_date=None,
                    member_limit=None
                )
                invite_link = link_obj.invite_link
        except Exception as e:
            logger.warning("Could not create/retrieve invite link", error=str(e))
            
    await repo.upsert_channel(
        telegram_id=event.chat.id,
        title=event.chat.title or "Unknown Channel",
        invite_link=invite_link
    )
    # upsert_channel already commits, but we can do it again or leave it
    # ensure atomic if needed, but repo commits so it is fine.


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED | LEFT))
async def on_bot_removed(event: ChatMemberUpdated, session: AsyncSession):
    if event.chat.type != ChatType.CHANNEL:
        return

    logger.info("Bot removed from channel", chat_id=event.chat.id)
    repo = ChannelRepository(session)
    await repo.delete_channel(event.chat.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=~PROMOTED_TRANSITION))
async def on_bot_demoted(event: ChatMemberUpdated, session: AsyncSession):
    """
    Handle cases where bot loses admin rights but is not kicked/left
    (e.g. demoted to regular member).
    Although in channels bots MUST be admins to properly function usually,
    if it is not admin, we should probably remove it from our active list.
    """
    if event.chat.type != ChatType.CHANNEL:
        return
    
    # Check if correct new status is not administrator
    # PROMOTED_TRANSITION covers NONE/MEMBER/RESTRICTED -> ADMINISTRATOR/CREATOR
    # We want to catch ADMINISTRATOR/CREATOR -> MEMBER/RESTRICTED
    
    new_status = event.new_chat_member.status
    if new_status not in ["administrator", "creator"]:
         logger.info("Bot demoted in channel", chat_id=event.chat.id)
         repo = ChannelRepository(session)
         await repo.delete_channel(event.chat.id)


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


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для управления подписками на каналы.\n\n"
                         "Просто добавьте меня администратором в канал, и я автоматически сохраню его.\n"
                         "Если убрать меня из администраторов или удалить из канала, я удалю его из базы.\n\n"
                         "Команды:\n"
                         " /channels - список подключенных каналов")