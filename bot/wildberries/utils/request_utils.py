from reportlab.lib.utils import ImageReader
import base64
import io
import logging
import asyncio
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json
import os
from typing import Any, Dict, List
import aiohttp
import time

from bot.common.printer import PrinterConfig, print_sticker
from bot.common.request_headers import RequestConfig


class WildberriesBackendAPI:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session
        self.request_config = RequestConfig()
        self.HEADERS = self.request_config.get_request_headers()
        self.BASE_URL = self.request_config.get_base_url()

    async def ping_task_status(self, task_id, max_retries: int = 10, sleep_seconds: int = 10, context: str = ''):
        for _ in range(max_retries):
            status = await self.check_task_status(task_id)
            if status == 'SUCCESS':
                print(f'Задача {context} выполнена')
                return True
            elif status == 'STARTED':
                print('Задача выполняется, подождите')
            elif status == 'FAILURE':
                print(f'При выполнении задачи: {context} произошла ошибка')
                return False
            else:
                print(f'Задача {context} выполняется')
            await asyncio.sleep(sleep_seconds)

    async def init_update_products(self) -> bool:
        URL = f'{self.BASE_URL}/api/v1/wildberries/sync_products/'
        async with self.session.get(url=URL, headers=self.HEADERS) as response:
            if response.status != 200:
                text = await response.text()
                logging.log(logging.ERROR, f'Ошибка запроса обновления товаров: {
                            response.status}: {text}')
                print(f'Ошибка запроса {response.status}')
                return
            response_json = await response.json()
            task_id = response_json['task_id']
            return await self.ping_task_status(task_id, 10, 10, 'обновление товаров')

    async def update_orders(self, supply_id):
        """supply_id только цифры"""
        URL = f'{self.BASE_URL}/api/v1/wildberries/sync_orders/'
        data = {
            'supply_id': supply_id,
        }
        async with self.session.post(url=URL, headers=self.HEADERS, json=data) as response:
            if response.status != 200:
                text = await response.text()
                logging.log(logging.ERROR, f'Ошибка запроса обновления заказов {
                            response.status}: {text}')
                print(f'Ошибка запроса {response.status}, создан лог')
                return
            response_json = await response.json()
            task_id = response_json['task_id']
            return await self.ping_task_status(task_id, 5, 5, 'обновление заказов')

    async def check_task_status(self, task_id: str) -> str:
        URL = f'{self.BASE_URL}/api/v1/wildberries/task_status/{task_id}/'
        async with self.session.get(url=URL, headers=self.HEADERS) as response:
            if response.status != 200:
                text = await response.text()
                logging.log(logging.ERROR, f'Ошибка запроса статуса таски celery: {
                            response.status}: {text}')
                print(f'Ошибка запроса {response.status}, создан лог')
                return
            response_json = await response.json()
            task_status = response_json['status']
            return task_status

    async def get_orders(self):
        URL = f'{self.BASE_URL}/api/v1/wildberries/orders/'
        async with self.session.get(url=URL, headers=self.HEADERS) as response:
            if response.status == 404:
                return 404
            if response.status == 402:
                return 402
            if response.status not in [404, 200, 201]:
                text = await response.text()
                logging.log(logging.ERROR, f'Ошибка получения заказов {response.status}: {text}')
                print(f'Ошибка запроса {response.status}, создан лог')
                return
            return await response.json()

    async def complete_orders_and_get_stickers(self, orders_ids: list):
        URL = f'{self.BASE_URL}/api/v1/wildberries/orders/'
        data = {'ids': orders_ids}
        async with self.session.post(url=URL, headers=self.HEADERS, json=data) as response:
            if response.status != 200:
                text = await response.text()
                logging.log(logging.ERROR, f'Ошибка запроса на получение стикеров {
                            response.status}: {text}')
                print(f'Ошибка запроса {response.status}, создан лог')
                return
            stickers_response = await response.json()
            return stickers_response['stickers']


class WbQrCode:
    def print_pdf_sticker(self, list_of_stickers: list, article) -> None:
        for sticker in list_of_stickers:
            sticker_base_64 = sticker['file']
            img_binary = base64.b64decode(sticker_base_64)
            img_stream = io.BytesIO(img_binary)
            BASE_FILE_PATH = f'bot/wildberries/temp/temp_sticker'
            new_name = f'{BASE_FILE_PATH}_{time.time()}.pdf'
            sticker_pdf = canvas.Canvas(new_name, pagesize=(580, 400))
            sticker_pdf.drawImage(ImageReader(img_stream), 0, 0, 580, 400)
            self._draw_article_on_wbcode(sticker_pdf, article)
            sticker_pdf.save()
            pdf_sticker_abs_path = os.path.abspath(new_name)
            printer_conf = PrinterConfig()
            width = printer_conf.get_config_value('wb_printer', 'WIDTHPOINTS')
            height = printer_conf.get_config_value('wb_printer', 'HEIGHTPOINTS')
            print_sticker(pdf_sticker_abs_path, width, height)

    def _draw_article_on_wbcode(self, canvas_obj: canvas.Canvas, article):
        '''
        Рисует артикул на QR-коде WB с возможностью переноса текста
        '''
        pdfmetrics.registerFont(TTFont('OpenSans-SemiBold', 'fonts/OpenSans-SemiBold.ttf'))
        pdfmetrics.registerFont(TTFont('OpenSans-Regular', 'fonts/OpenSans-Regular.ttf'))
        font_size = 22
        max_width = 340  # Максимальная ширина текста без переноса
        max_lines = 3  # Максимальное количество строк текста
        canvas_obj.setFont('OpenSans-SemiBold', font_size)
        rect_width = 115
        rect_height = 22
        rect_position = (45, 120)  # Позиция верхнего левого угла прямоугольника
        canvas_obj.setFillColor(colors.white)
        canvas_obj.rect(rect_position[0] * mm, rect_position[1] * mm,
                        rect_width * mm, rect_height * mm, fill=1)
        # Подготовка текста для переноса
        lines = []
        words = article.split()
        line = ''
        canvas_obj.setFillColor(colors.black)
        for word in words:
            if canvas_obj.stringWidth(line + ' ' + word) <= max_width:
                line += ' ' + word if line else word
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        # Ограничение количества строк
        lines = lines[:max_lines]
        # Рисование текста с учетом переноса
        text_position = (rect_position[0] + 1, rect_position[1] +
                         rect_height - 8)  # Начальная позиция текста
        for line in lines:
            canvas_obj.drawString(text_position[0] * mm, text_position[1] * mm, line.strip())
            text_position = (text_position[0], text_position[1] - 8)  # Учитываем высоту текста
