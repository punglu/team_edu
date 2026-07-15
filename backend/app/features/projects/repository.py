from abc import ABC, abstractmethod
from datetime import UTC, datetime
from uuid import uuid4

from google.cloud import firestore
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings
from app.features.projects.models import MemberModel, ProjectInvitedMemberModel, ProjectModel
from app.features.projects.schemas import Member, Project, ProjectInput, ProjectStatus


SAMPLE_MEMBERS = [
    Member(id="member-kim", name="김지훈", department="프로젝트팀", role="과장"),
    Member(id="member-lee", name="이수정", department="프로젝트팀", role="대리"),
    Member(id="member-park", name="박상민", department="운영팀", role="사원"),
]


def _project_from_model(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        name=model.name,
        owner_id=model.owner_id,
        owner_name=model.owner_name,
        description=model.description,
        status=ProjectStatus(model.status),
        progress=model.progress,
        start_date=model.start_date,
        due_date=model.due_date,
        priority=model.priority,
        invited_member_ids=[item.member_id for item in model.invited_members],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class ProjectRepository(ABC):
    @abstractmethod
    def list_projects(self) -> list[Project]:
        raise NotImplementedError

    @abstractmethod
    def get_project(self, project_id: str) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    def create_project(self, payload: ProjectInput) -> Project:
        raise NotImplementedError

    @abstractmethod
    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_members(self) -> list[Member]:
        raise NotImplementedError


class InMemoryProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        now = datetime.now(UTC)
        self.projects: dict[str, Project] = {
            "sample-project-01": Project(
                id="sample-project-01",
                name="신규 웹사이트 리뉴얼",
                owner_id="member-kim",
                owner_name="김지훈",
                description="교육용 가상 프로젝트입니다.",
                status=ProjectStatus.IN_PROGRESS,
                progress=65,
                start_date="2026-07-01",
                due_date="2026-08-31",
                priority="HIGH",
                invited_member_ids=["member-lee"],
                created_at=now,
                updated_at=now,
            ),
            "sample-project-02": Project(
                id="sample-project-02",
                name="모바일 앱 고도화",
                owner_id="member-lee",
                owner_name="이수정",
                description="교육용 가상 프로젝트입니다.",
                status=ProjectStatus.IN_PROGRESS,
                progress=40,
                start_date="2026-07-05",
                due_date="2026-09-15",
                priority="MEDIUM",
                invited_member_ids=["member-kim", "member-park"],
                created_at=now,
                updated_at=now,
            ),
            "sample-project-03": Project(
                id="sample-project-03",
                name="데이터 분석 대시보드",
                owner_id="member-park",
                owner_name="박상민",
                description="교육용 가상 프로젝트입니다.",
                status=ProjectStatus.ON_HOLD,
                progress=10,
                start_date="2026-07-10",
                due_date="2026-10-31",
                priority="LOW",
                invited_member_ids=[],
                created_at=now,
                updated_at=now,
            ),
        }

    def list_projects(self) -> list[Project]:
        return sorted(self.projects.values(), key=lambda item: item.updated_at, reverse=True)

    def get_project(self, project_id: str) -> Project | None:
        return self.projects.get(project_id)

    def create_project(self, payload: ProjectInput) -> Project:
        now = datetime.now(UTC)
        project = Project(
            id=str(uuid4()),
            **payload.model_dump(),
            status=ProjectStatus.IN_PROGRESS,
            progress=0,
            created_at=now,
            updated_at=now,
        )
        self.projects[project.id] = project
        return project

    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        current = self.projects.get(project_id)
        if current is None:
            return None
        updated = current.model_copy(
            update={
                **payload.model_dump(),
                "updated_at": datetime.now(UTC),
            }
        )
        self.projects[project_id] = updated
        return updated

    def delete_project(self, project_id: str) -> bool:
        return self.projects.pop(project_id, None) is not None

    def list_members(self) -> list[Member]:
        return SAMPLE_MEMBERS


class SqlProjectRepository(ProjectRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def _get_model(self, project_id: str) -> ProjectModel | None:
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.id == project_id)
            .options(selectinload(ProjectModel.invited_members))
        )
        return self.session.scalar(stmt)

    def list_projects(self) -> list[Project]:
        stmt = (
            select(ProjectModel)
            .options(selectinload(ProjectModel.invited_members))
            .order_by(ProjectModel.updated_at.desc())
        )
        return [_project_from_model(model) for model in self.session.scalars(stmt).all()]

    def get_project(self, project_id: str) -> Project | None:
        model = self._get_model(project_id)
        if model is None:
            return None
        return _project_from_model(model)

    def create_project(self, payload: ProjectInput) -> Project:
        now = datetime.now(UTC)
        project = ProjectModel(
            id=str(uuid4()),
            name=payload.name,
            owner_id=payload.owner_id,
            owner_name=payload.owner_name,
            description=payload.description,
            status=ProjectStatus.IN_PROGRESS.value,
            progress=0,
            start_date=payload.start_date,
            due_date=payload.due_date,
            priority=payload.priority.value,
            created_at=now,
            updated_at=now,
            invited_members=[
                ProjectInvitedMemberModel(position=index, member_id=member_id)
                for index, member_id in enumerate(payload.invited_member_ids)
            ],
        )
        self.session.add(project)
        self.session.flush()
        return _project_from_model(project)

    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        project = self._get_model(project_id)
        if project is None:
            return None

        project.name = payload.name
        project.owner_id = payload.owner_id
        project.owner_name = payload.owner_name
        project.description = payload.description
        project.start_date = payload.start_date
        project.due_date = payload.due_date
        project.priority = payload.priority.value
        project.updated_at = datetime.now(UTC)
        project.invited_members = [
            ProjectInvitedMemberModel(position=index, member_id=member_id)
            for index, member_id in enumerate(payload.invited_member_ids)
        ]
        self.session.flush()
        return _project_from_model(project)

    def delete_project(self, project_id: str) -> bool:
        project = self._get_model(project_id)
        if project is None:
            return False
        self.session.delete(project)
        self.session.flush()
        return True

    def list_members(self) -> list[Member]:
        stmt = select(MemberModel).where(MemberModel.active.is_(True)).order_by(MemberModel.name.asc())
        members = self.session.scalars(stmt).all()
        return [
            Member(
                id=member.id,
                name=member.name,
                department=member.department,
                role=member.role,
                active=member.active,
            )
            for member in members
        ]


class FirestoreProjectRepository(ProjectRepository):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = firestore.Client(
            project=settings.google_cloud_project,
            database=settings.firestore_database,
        )
        self.workspace = self.client.collection("workspaces").document(settings.workspace_id)

    def _projects(self):
        return self.workspace.collection("projects")

    def _members(self):
        return self.workspace.collection("members")

    def list_projects(self) -> list[Project]:
        docs = self._projects().order_by("updated_at", direction=firestore.Query.DESCENDING).stream()
        return [Project.model_validate({"id": doc.id, **doc.to_dict()}) for doc in docs]

    def get_project(self, project_id: str) -> Project | None:
        doc = self._projects().document(project_id).get()
        if not doc.exists:
            return None
        return Project.model_validate({"id": doc.id, **doc.to_dict()})

    def create_project(self, payload: ProjectInput) -> Project:
        now = datetime.now(UTC)
        ref = self._projects().document()
        project = Project(
            id=ref.id,
            **payload.model_dump(),
            status=ProjectStatus.IN_PROGRESS,
            progress=0,
            created_at=now,
            updated_at=now,
        )
        ref.set(project.model_dump(exclude={"id"}, mode="json"))
        return project

    def update_project(self, project_id: str, payload: ProjectInput) -> Project | None:
        current = self.get_project(project_id)
        if current is None:
            return None
        updated = current.model_copy(
            update={
                **payload.model_dump(),
                "updated_at": datetime.now(UTC),
            }
        )
        self._projects().document(project_id).set(
            updated.model_dump(exclude={"id"}, mode="json"),
            merge=False,
        )
        return updated

    def delete_project(self, project_id: str) -> bool:
        if self.get_project(project_id) is None:
            return False
        self._projects().document(project_id).delete()
        return True

    def list_members(self) -> list[Member]:
        docs = list(self._members().where("active", "==", True).stream())
        if not docs:
            return SAMPLE_MEMBERS
        return [Member.model_validate({"id": doc.id, **doc.to_dict()}) for doc in docs]
