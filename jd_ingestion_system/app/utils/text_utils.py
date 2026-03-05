import re
from typing import Iterable


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_lines_with_markers(text: str, markers: Iterable[str]) -> str:
    marker_set = {m.lower() for m in markers}
    cleaned_lines = [line for line in text.splitlines() if line.strip().lower() not in marker_set]
    return "\n".join(cleaned_lines)
