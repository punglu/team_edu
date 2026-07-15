from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.features.projects.schemas import Member, Project, ProjectInput
from app.features.projects.service import ProjectService


router = APIRouter(tags=["projects"])


def get_project_service() -> ProjectService:
    from app.main import project_service
    return project_service


@router.get("/projects", response_model=list[Project])
def list_projects(service: ProjectService = Depends(get_project_service)) -> list[Project]:
    return service.list_projects()


@router.post("/projects", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectInput,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    return service.create_project(payload)


@router.get("/projects/{project_id}", response_model=Project)
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.put("/projects/{project_id}", response_model=Project)
def update_project(
    project_id: str,
    payload: ProjectInput,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    project = service.update_project(project_id, payload)
    if project is None:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> Response:
    if not service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/members", response_model=list[Member])
def list_members(service: ProjectService = Depends(get_project_service)) -> list[Member]:
    return service.list_members()
