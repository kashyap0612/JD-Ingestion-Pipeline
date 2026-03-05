from io import BytesIO

import fitz
from PIL import Image
import pytesseract


def _ocr_pdf_document(doc: fitz.Document) -> str:
    pages_text: list[str] = []
    for page in doc:
        pix = page.get_pixmap(dpi=220)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages_text.append(pytesseract.image_to_string(image))
    return "\n".join(pages_text)


def extract_text_from_pdf(content: bytes) -> str:
    with fitz.open(stream=BytesIO(content), filetype="pdf") as doc:
        text = "\n".join(page.get_text("text") for page in doc)
        if text.strip():
            return text
        return _ocr_pdf_document(doc)
