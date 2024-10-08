import datetime
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.common.session import SingletoneSession
from bot.common.utils import remove_files_except_gitignore
from bot.wildberries.utils.request_utils import WildberriesBackendAPI
from bot.wildberries.handlers import wb_handlers_router
from bot.wildberries.orders_processing import wb_fsm_router
from bot.common.handlers import main_router


async def main() -> None:
    load_dotenv('config.env')
    dp = Dispatcher()
    dp.include_routers(
        main_router,
        wb_handlers_router,
        wb_fsm_router,
    )
    print('Загрузка...')
    remove_files_except_gitignore('bot/wildberries/temp/')
    bot = Bot(os.getenv('TG_API_KEY'))
    session = await SingletoneSession.get_session()
    wb_api = WildberriesBackendAPI(session)
    wb_product_update_status = await wb_api.init_update_products()
    if wb_product_update_status:
        print('Обновление успешно завершено')
    await dp.start_polling(bot)


if __name__ == '__main__':
    logs_path = f'bot/logs/log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M.txt")}'
    logging.basicConfig(filename=logs_path, level=logging.INFO,
                        format='%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s', encoding='utf-8')
    asyncio.run(main())
