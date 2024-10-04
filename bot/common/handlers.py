import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message

from bot.common.printer import IOBarcode, PDFBarcode, PrinterConfig, print_sticker
from bot.common.session import SingletoneSession
from bot.wildberries.utils.request_utils import WildberriesBackendAPI
from .keyboards import inline_menu_keyboard

main_router = Router()


@main_router.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    builder = inline_menu_keyboard()
    await message.answer('📍 Главное меню', reply_markup=builder.as_markup())


@main_router.callback_query(lambda callback: any(x in callback.data for x in ['print_barcode_o', 'print_barcode_y', 'print_barcode_w']))
async def print_barcode_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = callback.data.split()
    operation_type = data[0]
    pk = data[1]
    amount = int(data[2])
    session = await SingletoneSession.get_session()
    wb_backend = WildberriesBackendAPI(session)
    product = await wb_backend.get_products(id=pk)

    if not isinstance(product, dict):
        await callback.message.answer(f'Ошибка запроса, код {product}')
        await callback.answer()
        return

    if operation_type == 'print_barcode_o':
        ...
    elif operation_type == 'print_barcode_y':
        ...
    elif operation_type == 'print_barcode_w':
        l = [IOBarcode(product['article'], product['barcode'], amount)]
        pdf_rel_path = PDFBarcode(l).create_pdf_file()
        pdf_abs_path = os.path.abspath(pdf_rel_path)
        config = PrinterConfig()
        width = config.get_config_value('barcode', 'WIDTHPOINTS')
        height = config.get_config_value('barcode', 'HEIGHTPOINTS')
        print_sticker(pdf_abs_path, width, height)
    await callback.answer()
