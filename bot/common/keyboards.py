from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_menu_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🟪 WILDBERRIES',
        callback_data='wb_menu'),
    )
    builder.add(InlineKeyboardButton(
        text='🟦 Установить токен',
        callback_data='set_token'),
    )
    builder.add(InlineKeyboardButton(
        text='🦖 Остатки на складе',
        callback_data='stocks'),
    )
    builder.adjust(1)
    return builder