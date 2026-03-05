import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile

from app.core.config import Settings, get_settings
from app.models.schemas import IngestResponse
from app.pipeline.ingestion_pipeline import IngestionPipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingestion"])


def get_pipeline(settings: Settings = Depends(get_settings)) -> IngestionPipeline:
    return IngestionPipeline(settings)


def _run_pipeline(pipeline: IngestionPipeline, kwargs: dict) -> None:
    pipeline.ingest(**kwargs)


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile | None = File(default=None),
    url: str | None = Form(default=None),
    raw_text: str | None = Form(default=None),
    async_mode: bool = Form(default=False),
    pipeline: IngestionPipeline = Depends(get_pipeline),
) -> IngestResponse:
    if not any([file, url, raw_text]):
        raise HTTPException(status_code=400, detail="Provide a file, URL, or raw_text")

    content = None
    filename = None
    if file is not None:
        content = await file.read()
        filename = file.filename
        if len(content) > get_settings().max_file_size_bytes:
            raise HTTPException(status_code=413, detail="File exceeds 10MB limit")

    payload = {"filename": filename, "content": content, "source_url": url, "raw_text": raw_text}
    if async_mode:
        background_tasks.add_task(_run_pipeline, pipeline, payload)
        return IngestResponse(
            document_id="background-task",
            num_jds_detected=0,
            num_chunks_created=0,
            status="accepted",
        )

    try:
        result = pipeline.ingest(**payload)
        return IngestResponse(**result)
    except ValueError as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
