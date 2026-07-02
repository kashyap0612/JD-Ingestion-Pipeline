from math import ceil


def chunk_text(text: str, chunk_size_words: int = 500) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    for idx in range(ceil(len(words) / chunk_size_words)):
        start = idx * chunk_size_words
        end = start + chunk_size_words
        chunks.append(" ".join(words[start:end]))
    return chunks
