import logging
from itertools import islice
from typing import List
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.common.session import SingletoneSession
from bot.wildberries.utils.keyboards import wb_next_inline_keyboard, wb_reprint_keyboard
from bot.wildberries.utils.request_utils import WbQrCode, WildberriesBackendAPI

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
        await out_msg.edit_text('Загрузка завершена ✅')
    await state.clear()


@wb_fsm_router.message(WildberriesProcessState.show_orders)
async def show_orders(message: types.Message, state: FSMContext):
    session = await SingletoneSession.get_session()
    wb_api = WildberriesBackendAPI(session)
    orders_list = await wb_api.get_orders()
    if orders_list == 404:
        await message.answer('Все заказы были собраны')
        await state.clear()
        return
    orders_ids = [i['order_id'] for i in orders_list]
    barcodes = [i['barcodes'] for i in islice(orders_list, 3)]
    await state.update_data(
        {
            'orders_ids': orders_ids,
            'barcodes': barcodes,
            'total_amount': len(orders_list),
            'product_id': orders_list[0]['product']['id'],
            'article': orders_list[0]['product']['article'],
        }
    )
    m = f'''
Штрих-код: {barcodes[0]}
Артикул: {orders_list[0]['product']['article']}
Категория: {orders_list[0]['product']['category']}
*Количество: {len(orders_list)}*
'''
    await message.answer_photo(orders_list[0]['product']['photo'], m, parse_mode='MARKDOWN')
    logging.log(logging.INFO, m)
    await state.set_state(WildberriesProcessState.input_barcodes)


@wb_fsm_router.message(WildberriesProcessState.input_barcodes)
async def input_barcodes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    barcodes: List[str] = data['barcodes']
    msg = message.text.strip()
    if msg in barcodes:
        barcodes.remove(msg)
        await state.update_data(barcodes=barcodes)
        await message.reply('✅')
        if not barcodes:
            session = await SingletoneSession.get_session()
            wb_api = WildberriesBackendAPI(session)
            list_of_stickers = await wb_api.complete_orders_and_get_stickers(data['orders_ids'])
            WbQrCode().print_pdf_sticker(list_of_stickers, data['article'])
            wb_next_builder = wb_next_inline_keyboard()
            reprint_builder = wb_reprint_keyboard(data['product_id'])
            await message.answer(f'Перепечатать {data['article']}', reply_markup=reprint_builder.as_markup())
            await message.answer(f'Заказ {data['article']} выполнен', reply_markup=wb_next_builder.as_markup())
            logging.log(logging.INFO, f'Заказ выполнен.')
            # remain_msg = await message.answer(f'Осталось обработать товаров {incomplete_prods_count}', reply_markup=next_keyboard())
            await state.clear()
    else:
        await message.reply('Такого штрих-кода в списке нет')


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
