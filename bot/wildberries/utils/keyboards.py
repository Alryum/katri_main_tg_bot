from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def wb_menu_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🟪 Обновить заказы',
        callback_data='load_wb_orders'),
    )
    builder.add(InlineKeyboardButton(
        text='🟦 TBA',
        callback_data='testquery'),
    )
    builder.add(InlineKeyboardButton(
        text='🦖 TBA',
        callback_data='testquery'),
    )
    builder.adjust(1)
    return builder