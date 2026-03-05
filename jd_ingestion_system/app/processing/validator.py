import re


REQUIRED_HINTS = ["Responsibilities", "Requirements", "Skills", "Experience"]
MIN_CHARACTERS = 300


def is_valid_job_description(text: str) -> bool:
    if len(text.strip()) < MIN_CHARACTERS:
        return False
    return any(re.search(rf"\b{hint}\b", text, flags=re.IGNORECASE) for hint in REQUIRED_HINTS)
