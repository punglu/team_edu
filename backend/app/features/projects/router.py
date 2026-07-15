from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.database import get_db_session
from app.features.projects.schemas import Member, Project, ProjectInput
from app.features.projects.repository import InMemoryProjectRepository, SqlProjectRepository
from app.features.projects.service import ProjectService, ProjectServiceError
from app.core.config import get_settings


router = APIRouter(tags=["projects"])

def get_project_service_dependency(session: Session | None = Depends(get_db_session)) -> ProjectService:
    settings = get_settings()
    if settings.use_in_memory_repository:
        return ProjectService(InMemoryProjectRepository())
    if session is None:
        raise RuntimeError("Database session is required for PostgreSQL repository")
    return ProjectService(SqlProjectRepository(session), session=session)


@router.get("/projects", response_model=list[Project])
def list_projects(service: ProjectService = Depends(get_project_service_dependency)) -> list[Project]:
    return service.list_projects()


@router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectInput,
    service: ProjectService = Depends(get_project_service_dependency),
) -> Project:
    try:
        return service.create_project(payload)
    except ProjectServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/projects/{project_id}", response_model=Project)
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service_dependency),
) -> Project:
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.put("/projects/{project_id}", response_model=Project)
def update_project(
    project_id: str,
    payload: ProjectInput,
    service: ProjectService = Depends(get_project_service_dependency),
) -> Project:
    try:
        project = service.update_project(project_id, payload)
    except ProjectServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service_dependency),
) -> Response:
    try:
        deleted = service.delete_project(project_id)
    except ProjectServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/members", response_model=list[Member])
def list_members(service: ProjectService = Depends(get_project_service_dependency)) -> list[Member]:
    return service.list_members()
