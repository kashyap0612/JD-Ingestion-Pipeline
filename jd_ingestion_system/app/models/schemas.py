from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: str
    num_jds_detected: int
    num_chunks_created: int
    status: str


class JobRecord(BaseModel):
    id: str
    source: str
    text: str
    chunks: List[str]
    created_at: datetime
    extra: dict[str, Any] = Field(default_factory=dict)


class JobListResponse(BaseModel):
    jobs: List[JobRecord]


class StatsResponse(BaseModel):
    total_documents: int
    total_jobs: int
    total_chunks: int
    last_updated: Optional[datetime] = None
