from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def wb_menu_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🔄 Обновить заказы',
        callback_data='load_wb_orders'),
    )
    builder.add(InlineKeyboardButton(
        text='⬇️ Получить текущий заказ',
        callback_data='get_next_wb_order'),
    )
    builder.add(InlineKeyboardButton(
        text='🦖 Остатки (в разработке)',
        callback_data='testquery'),
    )
    builder.adjust(1)
    return builder


def wb_next_inline_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🟦 Следующий заказ',
        callback_data='get_next_wb_order'),
    )
    builder.adjust(1)
    return builder


def wb_reprint_keyboard(id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🌌 Перепечатать заказ',
        callback_data=f'repr_w {id}'),
    )
    builder.adjust(1)
    return builder


def wb_print_barcode(id: int, amount: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='🌌 Напечатать штрих-код',
        callback_data=f'print_barcode_w {id} {amount}'),
    )
    builder.adjust(1)
    return builder
