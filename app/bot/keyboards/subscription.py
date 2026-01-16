from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Sequence
from app.models.channel import Channel

def get_subscription_keyboard(channels: Sequence[Channel]) -> InlineKeyboardMarkup:
    buttons = []
    for channel in channels:
        url = channel.invite_link or f"https://t.me/c/{str(channel.telegram_id)[4:]}/1" # Fallback if no link
        # Better fallback: if we don't have a link, we can't really invite them easily unless it's public. 
        # But assuming invite_link is populated.
        
        btn = InlineKeyboardButton(text=channel.title, url=url)
        buttons.append([btn])
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)
