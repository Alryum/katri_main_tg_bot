from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from .keyboards import inline_menu_keyboard

main_router = Router()

@main_router.message(Command('start'))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    builder = inline_menu_keyboard()
    await message.answer('📍 Главное меню', reply_markup=builder.as_markup())