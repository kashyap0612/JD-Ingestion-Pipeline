from io import BytesIO

import pytesseract
from PIL import Image


def extract_text_from_image(content: bytes) -> str:
    with Image.open(BytesIO(content)) as image:
        return pytesseract.image_to_string(image)
