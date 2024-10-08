import io
from PIL import Image
from pyzbar.pyzbar import decode


class PhotoBarcodeParser:
    def __init__(self, photo: io.BytesIO) -> None:
        self.photo = photo

    def get_barcode(self):
        image = Image.open(self.photo)
        decoded_objects = decode(image)
        if self._is_single_barcode(decoded_objects) and decoded_objects[-1].type == 'EAN13':
            return decoded_objects[-1].data.decode()

    def _is_single_barcode(self, decoded_data: list) -> bool:
        return len(decoded_data) == 1
