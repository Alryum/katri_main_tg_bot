from itertools import islice
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
import logging

from bot.common.session import SingletoneSession
from bot.wildberries.orders_processing import WildberriesProcessState
from bot.wildberries.utils.keyboards import wb_menu_keyboard
from bot.wildberries.utils.request_utils import WildberriesBackendAPI

wb_handlers_router = Router()


@wb_handlers_router.callback_query(F.data == 'load_wb_orders')
async def wb_load_orders_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    '''
    Обработка заказов WB callback
    '''
    await state.clear()
    await callback.message.answer(f'ВАЖНО: Убедитесь, что вы добавили все нужные товары в сборочное задание. Их можно добавить сейчас, до ввода номера поставки. После ввода номера бот соберет заказы из поставки.')
    await callback.message.answer('Введите номер поставки (только цифры)')
    logging.log(logging.INFO, 'Начата обработка заказов WILDBERRIES')
    await state.set_state(WildberriesProcessState.orders_update)
    await callback.answer()


@wb_handlers_router.callback_query(F.data == 'wb_menu')
async def wb_menu_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    builder = wb_menu_keyboard()
    await callback.message.answer('WB Menu', reply_markup=builder.as_markup())
    await callback.answer()

@wb_handlers_router.callback_query(F.data == 'get_next_wb_order')
async def wb_get_next_order_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    session = await SingletoneSession.get_session()
    wb_api = WildberriesBackendAPI(session)
    orders_list = await wb_api.get_orders()
    if orders_list == 404:
        await callback.message.answer('Все заказы были собраны')
        await state.clear()
        return
    orders_ids = [i['order_id'] for i in orders_list]
    barcodes = [i['product']['barcode'] for i in islice(orders_list, 3)]
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
    await callback.message.answer_photo(orders_list[0]['product']['photo'], m, parse_mode='MARKDOWN')
    logging.log(logging.INFO, m)
    await state.set_state(WildberriesProcessState.input_barcodes)


# @wb_router.callback_query(F.data == 'regenerate_table_wb')
# async def wb_regen_orders_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
#     '''
#     Регенерация таблицы заказов WB
#     '''
#     await state.clear()
#     logging.log(logging.INFO, 'Регенерация таблицы заказов')
#     session = await SingletoneSession.get_session()
#     await WildberriesOrdersManager().clear_db()
#     await callback.message.answer(f'ВАЖНО: Убедитесь, что вы добавили все нужные товары в сборочное задание. Их можно добавить сейчас, до ввода номера поставки. После ввода номера бот соберет заказы из поставки.')
#     await callback.message.answer('Введите номер поставки (только цифры)')
#     await state.set_state(WildberriesProcessState.orders_init)
#     await callback.answer()


# @wb_router.callback_query(F.data == 'skip_orders_wb')
# async def wb_skip_orders(callback: types.CallbackQuery, state: FSMContext) -> None:
#     '''
#     Пропускает заказы WB
#     '''
#     await state.clear()
#     logging.log(logging.INFO, f'Пропуск заказов WB')
#     await callback.message.answer(f'Введите штрих-код заказа до которого нужно пропустить')
#     await state.set_state(WildberriesProcessState.input_barcode_for_skip)
#     await callback.answer()
