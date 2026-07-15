from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.features.projects.repository import (
    FirestoreProjectRepository,
    InMemoryProjectRepository,
)
from app.features.projects.router import router as projects_router
from app.features.projects.service import ProjectService


settings = get_settings()

if settings.use_in_memory_repository:
    repository = InMemoryProjectRepository()
else:
    repository = FirestoreProjectRepository(settings)

project_service = ProjectService(repository)

app = FastAPI(
    title="ProjectFlow Education API",
    version="0.1.0",
)

app.include_router(projects_router, prefix="/api")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "workspace": settings.workspace_id,
    }


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
ASSETS_DIR = STATIC_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(request: Request, full_path: str):
    if full_path.startswith("api/"):
        return {"detail": "Not Found"}
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        return {"message": "Frontend build is not available."}
    return FileResponse(index_file)
