from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.features.projects.repository import ProjectRepository
from app.features.projects.schemas import ProjectInput
from app.features.projects.service import ProjectService, ProjectServiceError


class FailingRepository(ProjectRepository):
    def list_projects(self):
        raise NotImplementedError

    def get_project(self, project_id: str):
        raise NotImplementedError

    def create_project(self, payload: ProjectInput):
        raise SQLAlchemyError("boom")

    def update_project(self, project_id: str, payload: ProjectInput):
        raise NotImplementedError

    def delete_project(self, project_id: str):
        raise NotImplementedError

    def list_members(self):
        raise NotImplementedError


def test_service_rolls_back_on_sqlalchemy_error() -> None:
    session = Mock()
    service = ProjectService(FailingRepository(), session=session)

    with pytest.raises(ProjectServiceError):
        service.create_project(
            ProjectInput(
                name="신규 프로젝트",
                owner_id="member-kim",
                owner_name="김지훈",
                description=None,
                start_date="2026-07-15",
                due_date="2026-07-20",
                priority="MEDIUM",
                invited_member_ids=[],
            )
        )

    session.rollback.assert_called_once()
    session.commit.assert_not_called()
