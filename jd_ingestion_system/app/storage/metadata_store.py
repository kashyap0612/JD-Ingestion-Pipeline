import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MetadataStore:
    def __init__(self, metadata_path: Path):
        self.metadata_path = metadata_path
        if not metadata_path.exists():
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.write_text(json.dumps({"documents": [], "jobs": []}, indent=2), encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        return json.loads(self.metadata_path.read_text(encoding="utf-8"))

    def _write(self, payload: dict[str, Any]) -> None:
        self.metadata_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def add_document(self, document: dict[str, Any]) -> None:
        payload = self._read()
        payload["documents"].append({**document, "created_at": datetime.now(timezone.utc).isoformat()})
        self._write(payload)

    def add_jobs(self, jobs: list[dict[str, Any]]) -> None:
        payload = self._read()
        now = datetime.now(timezone.utc).isoformat()
        payload["jobs"].extend([{**job, "created_at": now} for job in jobs])
        self._write(payload)

    def list_jobs(self) -> list[dict[str, Any]]:
        return self._read().get("jobs", [])

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return next((job for job in self.list_jobs() if job["id"] == job_id), None)

    def stats(self) -> dict[str, Any]:
        payload = self._read()
        jobs = payload.get("jobs", [])
        chunks = sum(len(job.get("chunks", [])) for job in jobs)
        last_updated = jobs[-1].get("created_at") if jobs else None
        return {
            "total_documents": len(payload.get("documents", [])),
            "total_jobs": len(jobs),
            "total_chunks": chunks,
            "last_updated": last_updated,
        }
