from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.models.schemas import JobListResponse, JobRecord, StatsResponse
from app.storage.metadata_store import MetadataStore

router = APIRouter(tags=["admin"])


def get_metadata_store(settings: Settings = Depends(get_settings)) -> MetadataStore:
    return MetadataStore(settings.metadata_path)


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(store: MetadataStore = Depends(get_metadata_store)) -> JobListResponse:
    jobs = [JobRecord(**job) for job in store.list_jobs()]
    return JobListResponse(jobs=jobs)


@router.get("/jobs/{job_id}", response_model=JobRecord)
def get_job(job_id: str, store: MetadataStore = Depends(get_metadata_store)) -> JobRecord:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRecord(**job)


@router.get("/stats", response_model=StatsResponse)
def get_stats(store: MetadataStore = Depends(get_metadata_store)) -> StatsResponse:
    return StatsResponse(**store.stats())
