from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.features.projects.repository import ProjectRepository
from app.features.projects.schemas import Member, Project, ProjectInput


class ProjectServiceError(Exception):
    pass


class ProjectService:
    def __init__(self, repository: ProjectRepository, session: Session | None = None) -> None:
        self.repository = repository
        self.session = session

    def list_projects(self) -> list[Project]:
        return self.repository.list_projects()

    def get_project(self, project_id: str) -> Project | None:
        return self.repository.get_project(project_id)

    def create_project(self, payload: ProjectInput) -> Project:
        return self._run_in_transaction(lambda: self.repository.create_project(payload))

    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        return self._run_in_transaction(lambda: self.repository.update_project(project_id, payload))

    def delete_project(self, project_id: str) -> bool:
        return self._run_in_transaction(lambda: self.repository.delete_project(project_id))

    def list_members(self) -> list[Member]:
        return self.repository.list_members()

    def _run_in_transaction(self, action):
        try:
            result = action()
            if self.session is not None:
                self.session.commit()
            return result
        except SQLAlchemyError as exc:
            if self.session is not None:
                self.session.rollback()
            raise ProjectServiceError("프로젝트 데이터를 저장하지 못했습니다.") from exc
        except Exception:
            if self.session is not None:
                self.session.rollback()
            raise
