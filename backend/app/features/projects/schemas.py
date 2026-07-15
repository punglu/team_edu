from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ProjectStatus(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"


class ProjectPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    owner_id: str = Field(min_length=1)
    owner_name: str = Field(min_length=1)
    description: str | None = Field(default=None, max_length=1000)
    start_date: date
    due_date: date
    priority: ProjectPriority = ProjectPriority.MEDIUM
    invited_member_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "ProjectInput":
        if self.due_date < self.start_date:
            raise ValueError("마감일은 시작일보다 빠를 수 없습니다.")
        return self


class Project(ProjectInput):
    id: str
    status: ProjectStatus = ProjectStatus.IN_PROGRESS
    progress: int = Field(default=0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime


class Member(BaseModel):
    id: str
    name: str
    department: str | None = None
    role: str | None = None
    active: bool = True
