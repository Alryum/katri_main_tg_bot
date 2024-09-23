import configparser
import win32api
import win32print
import logging
import os
from reportlab.lib.units import mm
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics import renderPDF
from typing import List, Dict
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


class PrinterConfig:

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read('print_config.ini')

    def get_config_value(self, section: str, key: str):
        try:
            return self.config[section][key]
        except KeyError as key_err:
            logging.log(logging.ERROR, f'{key_err}')


class IOBarcode:
    def __init__(self, article: str, barcode: str, amount: int, name=''):
        self.article = article
        self.barcode = barcode
        self.amount = amount
        self.name = name
        self.barcode_io = self.__create_barcode()

    def __create_barcode(self) -> BytesIO:
        barcode_io = BytesIO()
        EAN13(self.barcode, writer=ImageWriter()).write(barcode_io)
        return barcode_io


class PDFBarcode:
    def __init__(self, IOBarcodes: List[IOBarcode]):
        self.IOBarcodes = IOBarcodes

    def create_pdf_file(self) -> str:
        pdf_buffer = BytesIO()
        pdfmetrics.registerFont(TTFont('OpenSans-SemiBold', 'fonts/OpenSans-SemiBold.ttf'))
        pdfmetrics.registerFont(TTFont('OpenSans-Regular', 'fonts/OpenSans-Regular.ttf'))
        c = canvas.Canvas(pdf_buffer, pagesize=(580, 400))

        for product in self.IOBarcodes:
            barcode_drawing = createBarcodeDrawing(
                'EAN13', value=product.barcode, format='png', width=200*mm, height=90*mm)
            for _ in range(product.amount):
                c.setFont('OpenSans-SemiBold', 25)
                c.drawCentredString(290, 350, f'{product.name}'.encode('utf-8'))
                if len(product.article) > 40:
                    split_list = product.article.split()
                    c.drawCentredString(290, 50, f'{" ".join(split_list[:-3])}'.encode('utf-8'))
                    c.drawCentredString(290, 25, f'{" ".join(split_list[-3:])}'.encode('utf-8'))
                else:
                    c.drawCentredString(290, 50, f'{product.article}'.encode('utf-8'))
                renderPDF.draw(barcode_drawing, c, 10, 80)
                c.showPage()

        c.save()
        pdf_name = f'bot/common/temp/current_sticker.pdf'
        with open(pdf_name, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        pdf_buffer.close()
        return pdf_name


def print_sticker(pdf_sticker_abs_path, widthpoints: float, heightpoints: float) -> None:
    '''
    Печать этикетки
    '''
    current_directory = os.getcwd()
    GHOSTSCRIPT_PATH = os.path.join(current_directory, 'bot', 'gsprint', 'bin', 'gswin32.exe')
    GSPRINT_PATH = os.path.join(current_directory, 'bot', 'gsprint', 'gsprint.exe')

    currentprinter = win32print.GetDefaultPrinter()
    params = f'-ghostscript "{GHOSTSCRIPT_PATH}" -printer "{currentprinter}" -dDEVICEWIDTHPOINTS={widthpoints} -dDEVICEHEIGHTPOINTS={heightpoints} -dPDFFitPage "{pdf_sticker_abs_path}"'

    win32api.ShellExecute(0, 'open', GSPRINT_PATH, params, '.', 0)
    logging.log(logging.INFO, f'Печать стикера {pdf_sticker_abs_path}')
