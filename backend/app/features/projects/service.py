from app.features.projects.repository import ProjectRepository
from app.features.projects.schemas import Member, Project, ProjectInput


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self.repository = repository

    def list_projects(self) -> list[Project]:
        return self.repository.list_projects()

    def get_project(self, project_id: str) -> Project | None:
        return self.repository.get_project(project_id)

    def create_project(self, payload: ProjectInput) -> Project:
        return self.repository.create_project(payload)

    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        return self.repository.update_project(project_id, payload)

    def delete_project(self, project_id: str) -> bool:
        return self.repository.delete_project(project_id)

    def list_members(self) -> list[Member]:
        return self.repository.list_members()
