from io import BytesIO

from docx import Document


def extract_text_from_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
