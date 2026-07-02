import json
import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)


def segment_with_llm(text: str) -> list[str]:
    """Split text using Gemini API. Falls back to single block on API errors."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not configured; skipping LLM segmentation")
        return [text]

    prompt = (
        "Split this document into separate job descriptions and return JSON list. "
        "Return only a JSON array of strings.\n\n"
        f"Document:\n{text[:30000]}"
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload: dict[str, Any] = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        segments = json.loads(raw_text)
        return [s.strip() for s in segments if isinstance(s, str) and s.strip()] or [text]
    except Exception as exc:  # best-effort optional stage
        logger.warning("LLM segmentation failed: %s", exc)
        return [text]
