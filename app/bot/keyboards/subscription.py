from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.channel import Channel


def get_subscription_keyboard(channels: Sequence[Channel]) -> InlineKeyboardMarkup:
    buttons = []
    for channel in channels:
        url = (
            channel.invite_link or f"https://t.me/c/{str(channel.telegram_id)[4:]}/1"
        )  # Fallback if no link

        btn = InlineKeyboardButton(text=channel.title, url=url)
        buttons.append([btn])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
