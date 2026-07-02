import logging
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import Settings
from app.llm.gemini_segmenter import segment_with_llm
from app.pipeline.extractors.docx_extractor import extract_text_from_docx
from app.pipeline.extractors.image_extractor import extract_text_from_image
from app.pipeline.extractors.pdf_extractor import extract_text_from_pdf
from app.pipeline.extractors.url_extractor import extract_text_from_url
from app.pipeline.input_detector import InputType, detect_input_type
from app.processing.chunker import chunk_text
from app.processing.cleaner import clean_text
from app.processing.segmenter import segment_job_descriptions
from app.processing.validator import is_valid_job_description
from app.storage.file_store import save_binary, save_text
from app.storage.metadata_store import MetadataStore
from app.storage.vector_store import VectorStore
from app.utils.hashing import generate_document_id

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.metadata_store = MetadataStore(settings.metadata_path)
        self.vector_store = VectorStore(
            settings.faiss_index_path,
            settings.vector_metadata_path,
            settings.embedding_model_name,
        )

    def _extract_text(self, input_type: InputType, content: bytes | None = None, url: str | None = None) -> str:
        if input_type == InputType.PDF:
            return extract_text_from_pdf(content or b"")
        if input_type == InputType.DOCX:
            return extract_text_from_docx(content or b"")
        if input_type == InputType.IMAGE:
            return extract_text_from_image(content or b"")
        if input_type == InputType.URL:
            return extract_text_from_url(url or "")
        return (content or b"").decode("utf-8", errors="ignore")

    def ingest(
        self,
        *,
        filename: str | None,
        content: bytes | None,
        source_url: str | None = None,
        raw_text: str | None = None,
    ) -> dict:
        logger.info("input received filename=%s url=%s", filename, source_url)
        input_type = detect_input_type(filename=filename, url=source_url, text=raw_text)
        binary = content if content is not None else (raw_text or "").encode("utf-8")
        document_id = generate_document_id(binary)

        raw_target = self.settings.raw_dir / f"{document_id}_{filename or 'url.txt'}"
        if content:
            save_binary(raw_target, content)

        extracted = self._extract_text(input_type, content=binary if input_type != InputType.URL else None, url=source_url)
        logger.info("extraction success doc=%s chars=%d", document_id, len(extracted))

        cleaned = clean_text(extracted)
        rule_segments = segment_job_descriptions(cleaned)
        llm_segments = segment_with_llm(cleaned) if self.settings.use_llm_segmentation else rule_segments

        if self.settings.use_llm_segmentation and len(rule_segments) <= 1 < len(llm_segments):
            selected_segments = llm_segments
        else:
            selected_segments = rule_segments

        valid_segments = [seg for seg in selected_segments if is_valid_job_description(seg)]
        logger.info("segmentation count doc=%s valid=%d", document_id, len(valid_segments))

        processed_path = self.settings.processed_dir / f"{document_id}.txt"
        save_text(processed_path, "\n\n---\n\n".join(valid_segments))

        chunk_count = 0
        job_records: list[dict] = []
        for jd_idx, segment in enumerate(valid_segments, start=1):
            chunks = chunk_text(segment)
            timestamp = datetime.now(timezone.utc).isoformat()
            metadatas = [
                {
                    "job_id": f"{document_id}_job_{jd_idx}",
                    "chunk_id": f"{document_id}_job_{jd_idx}_chunk_{chunk_idx}",
                    "source": source_url or filename or "raw_text",
                    "timestamp": timestamp,
                }
                for chunk_idx, _ in enumerate(chunks, start=1)
            ]
            chunk_count += self.vector_store.add_chunks(chunks, metadatas)
            job_records.append(
                {
                    "id": f"{document_id}_job_{jd_idx}",
                    "source": source_url or filename or "raw_text",
                    "text": segment,
                    "chunks": chunks,
                    "extra": {
                        "rule_segment_count": len(rule_segments),
                        "llm_segment_count": len(llm_segments),
                    },
                }
            )

        self.metadata_store.add_document(
            {
                "id": document_id,
                "source": source_url or filename or "raw_text",
                "input_type": input_type.value,
                "processed_path": str(processed_path),
            }
        )
        self.metadata_store.add_jobs(job_records)
        logger.info("embedding stored doc=%s chunks=%d", document_id, chunk_count)

        return {
            "document_id": document_id,
            "num_jds_detected": len(valid_segments),
            "num_chunks_created": chunk_count,
            "status": "completed",
        }
