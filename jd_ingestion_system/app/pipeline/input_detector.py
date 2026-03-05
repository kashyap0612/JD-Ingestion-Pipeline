from enum import Enum
from pathlib import Path


class InputType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    IMAGE = "image"
    URL = "url"
    RAW_TEXT = "raw_text"


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def detect_input_type(filename: str | None = None, url: str | None = None, text: str | None = None) -> InputType:
    if url:
        return InputType.URL
    if text and not filename:
        return InputType.RAW_TEXT
    ext = Path(filename or "").suffix.lower()
    if ext == ".pdf":
        return InputType.PDF
    if ext == ".docx":
        return InputType.DOCX
    if ext in IMAGE_EXTENSIONS:
        return InputType.IMAGE
    raise ValueError(f"Unsupported input type: {filename or 'unknown'}")
