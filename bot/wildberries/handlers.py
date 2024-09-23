from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
import logging

from bot.wildberries.orders_processing import WildberriesProcessState
from bot.wildberries.utils.keyboards import wb_menu_keyboard

wb_handlers_router = Router()


@wb_handlers_router.callback_query(F.data == 'load_wb_orders')
async def wb_menu_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
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
