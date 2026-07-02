import hashlib
from datetime import datetime, timezone


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def generate_document_id(content: bytes) -> str:
    digest = compute_sha256(content)[:12]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"doc_{timestamp}_{digest}"
