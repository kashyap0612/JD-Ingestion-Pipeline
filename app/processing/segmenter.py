import re


MARKERS = ["Job Title", "Position", "Responsibilities", "Requirements", "Qualifications"]


def segment_job_descriptions(text: str) -> list[str]:
    marker_pattern = "|".join(re.escape(marker) for marker in MARKERS)
    split_pattern = rf"(?=(?:^|\n)\s*(?:{marker_pattern})\s*[:\-])"
    segments = [chunk.strip() for chunk in re.split(split_pattern, text, flags=re.IGNORECASE) if chunk.strip()]

    # Keep only non-trivial segments and merge spillover blocks
    normalized: list[str] = []
    for seg in segments:
        if len(seg) < 80 and normalized:
            normalized[-1] = f"{normalized[-1]}\n{seg}".strip()
        else:
            normalized.append(seg)
    return normalized or [text]
