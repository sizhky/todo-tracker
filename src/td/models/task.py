from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone  # Removed timedelta

if TYPE_CHECKING:
    from .project import Project, ProjectRead  # Assuming Project is in project.py
    from .time_entry import TimeEntry  # Added for forward reference


class TaskBase(SQLModel):  # Fields common to creation and reading, not a table
    title: str
    description: Optional[str] = Field(default=None)
    status: bool = Field(default=False)  # 0 is pending, 1 is done
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", index=True
    )


class Task(TaskBase, table=True):  # This is your DB table model
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    project: Optional["Project"] = Relationship(back_populates="tasks")
    time_entries: List["TimeEntry"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete"}
    )


# Schemas for API/CLI input and output if they differ from the table model
# For now, we can often use the table models directly or the Base models
class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    project: Optional["ProjectRead"] = None  # Added project field
    total_time_seconds: float = Field(default=0.0)  # New field for total time spent


class TaskUpdate(SQLModel):  # Only fields that are updatable
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None
    project_id: Optional[int] = None


# To handle the forward references for relationships, update them after all models are defined.
# This is often needed if models reference each other.
# However, SQLModel is usually good at resolving string type hints like "Project".
# If you encounter issues, you might explicitly call:
# Project.model_rebuild()
# Area.model_rebuild()
# Task.model_rebuild()
# TaskStatusTable.model_rebuild()
