import trafilatura
from bs4 import BeautifulSoup


def extract_text_from_url(url: str) -> str:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        if text:
            return text
    soup = BeautifulSoup(downloaded or "", "html.parser")
    return soup.get_text("\n", strip=True)
