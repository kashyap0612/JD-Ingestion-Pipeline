import re

from bs4 import BeautifulSoup

from app.utils.text_utils import normalize_whitespace, remove_lines_with_markers


NOISE_MARKERS = ["Apply now", "Share this job", "Recommended jobs"]


def clean_text(raw_text: str) -> str:
    without_html = BeautifulSoup(raw_text, "html.parser").get_text("\n")
    without_noise = remove_lines_with_markers(without_html, NOISE_MARKERS)
    without_artifacts = re.sub(r"\u00a0", " ", without_noise)
    return normalize_whitespace(without_artifacts)
