from fastapi import FastAPI

from app.api.routes_admin import router as admin_router
from app.api.routes_ingest import router as ingest_router
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.include_router(ingest_router)
app.include_router(admin_router)


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
