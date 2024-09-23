import logging
from itertools import islice
from typing import List
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.common.session import SingletoneSession
from bot.wildberries.utils.request_utils import WildberriesBackendAPI

# from bot.common.request_utils import increment_orders_stat
# from bot.common.sessions import SingletoneSession, get_db_session
# from bot.common.keyboards import inline_menu_keyboard, next_keyboard
# from bot.stocks.requests_utils import MpKatriProApi
# from bot.wildberries.keyboards import wb_print_barcode_keyboard, wb_reprint_keyboard
# from bot.wildberries.models import WildberriesOrderItem, WildberriesProduct
# from bot.wildberries.utils.common import skip_wb_orders
# from bot.wildberries.utils.db_requests import get_anchor_order_id
# from bot.wildberries.utils.orders import WildberriesOrdersManager
# from bot.wildberries.utils.request_utils import WbQrCode, WildberriesBackendAPI

wb_fsm_router = Router()


class WildberriesProcessState(StatesGroup):
    orders_update = State()
    show_orders = State()
    input_barcodes = State()
    input_barcode_for_skip = State()
    skip = State()


@wb_fsm_router.message(WildberriesProcessState.orders_update)
async def orders_init(message: types.Message, state: FSMContext):
    msg = message.text.strip()
    if not msg.isdigit():
        await message.answer('Введите только цифры поставки')
        return
    session = await SingletoneSession.get_session()
    wb_api = WildberriesBackendAPI(session)
    out_msg = await message.answer('Загрузка заказов')
    is_done = await wb_api.update_orders(msg)
    if is_done:
        await out_msg.edit_text('Загрузка завершена')
    await state.clear()


# @wb_fsm_router.message(WildberriesProcessState.show_orders)
# async def show_orders(message: types.Message, state: FSMContext):
#     anchor_order_id = await get_anchor_order_id()
#     async with get_db_session() as session:
#         result = (
#             await session.execute(
#                 select(WildberriesOrderItem)
#                 .options(
#                     selectinload(WildberriesOrderItem.product)
#                 )
#                 .filter_by(is_complete=False, product_id=anchor_order_id)
#                 .join(WildberriesProduct, WildberriesOrderItem.product_id == WildberriesProduct.id)
#                 .order_by(asc(WildberriesProduct.category), asc(WildberriesProduct.article))
#             )
#         )

#         products_list = result.scalars().all()
#     if not products_list:
#         builder = inline_menu_keyboard()
#         await state.clear()
#         await message.answer('Все заказы были собраны.', reply_markup=builder.as_markup())

#     products_barcodes = [p.product.barcode for p in islice(products_list, 3)]
#     data = {
#         'barcodes': products_barcodes,
#         'orders_ids': [int(p.order_id) for p in products_list],
#         'product_id': products_list[0].product.id,
#         'total_amount': len(products_list),
#         'article': products_list[0].product.article,
#     }
#     await state.update_data(data)

#     session = await SingletoneSession.get_session()
#     prod = products_list[0].product
#     mp_katri_web = MpKatriProApi(session)
#     current_stock = await mp_katri_web.get_current_product_balance(prod.barcode)
#     m = f'''
# Штрих-код: {prod.barcode}
# Артикул: {prod.article}
# Категория: {prod.category}

# *{current_stock}*

# *Количество: {len(products_list)}*
# '''
#     barcode_stock_k_builder = wb_print_barcode_keyboard(
#         products_list[0].product.id, len(products_list), prod.barcode)
#     await message.answer_photo(prod.photo, m, parse_mode='MARKDOWN', reply_markup=barcode_stock_k_builder.as_markup())
#     logging.log(logging.INFO, m)
#     await state.set_state(WildberriesProcessState.input_barcodes)


# @wb_fsm_router.message(WildberriesProcessState.input_barcodes)
# async def input_barcodes(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     barcodes: List[str] = data['barcodes']
#     msg = message.text.strip()
#     if msg in barcodes:
#         barcodes.remove(msg)
#         await state.update_data(barcodes=barcodes)
#         await message.reply('✅')
#         if not barcodes:
#             http_session = await SingletoneSession.get_session()
#             await WbQrCode(http_session).print_pdf_sticker(data['orders_ids'], data['article'])
#             async with get_db_session() as session:
#                 await session.execute(
#                     update(WildberriesOrderItem)
#                     .where(WildberriesOrderItem.product_id == data['product_id'])
#                     .values(is_complete=True)
#                 )
#                 await session.commit()
#             builder = wb_reprint_keyboard(data['product_id'])
#             await message.answer(f'Заказ выполнен', reply_markup=builder.as_markup())
#             logging.log(logging.INFO, f'Заказ выполнен. POSTING NUMBER:')
#             async with get_db_session() as session:
#                 incomplete_prods_count = await session.execute(
#                     select(func.count()).where(WildberriesOrderItem.is_complete == False)
#                 )
#                 incomplete_prods_count = incomplete_prods_count.scalar()
#             s = await SingletoneSession.get_session()
#             if not await increment_orders_stat('wildberries', data['total_amount'], s):
#                 await message.answer(f'Ошибка при обновлении статистики')
#             remain_msg = await message.answer(f'Осталось обработать товаров {incomplete_prods_count}', reply_markup=next_keyboard())
#             if not incomplete_prods_count:
#                 builder = inline_menu_keyboard()
#                 await remain_msg.edit_text('Сборка закончена 🗿', reply_markup=builder.as_markup())
#                 await state.clear()
#                 return
#             await state.set_state(WildberriesProcessState.show_orders)
#     else:
#         await message.reply('Такого штрих-кода в списке нет')


# @wb_fsm_router.message(WildberriesProcessState.input_barcode_for_skip)
# async def input_barcode_for_skip(message: types.Message, state: FSMContext):
#     msg = message.text.strip()
#     if not msg.isdecimal() or len(msg) != 13:
#         await message.answer('На вход ожидается штрих-код')
#         return
#     try:
#         await skip_wb_orders(msg)
#         await state.set_state(WildberriesProcessState.show_orders)
#         await message.answer('Заказы пропущены. Нажмите следующий заказ', reply_markup=next_keyboard())
#     except AttributeError as e:
#         logging.log(logging.ERROR, e)
#         await message.answer('Произошла ошибка пропуска заказов WB. Состояние обработки сброшено. Используйте /start')
#         await message.answer('Возможная ошибка: указанного штрих-кода нет в поставке')
#         await state.clear()
#     except Exception as e:
#         logging.log(logging.ERROR, e)
#         await message.answer('Произошла ошибка пропуска заказов WB. Состояние обработки сброшено. Используйте /start')
#         await state.clear()
