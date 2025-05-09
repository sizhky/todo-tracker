from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
import enum


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

    def emoji_map(self):
        return {
            TaskStatus.PENDING: "⏳",
            TaskStatus.IN_PROGRESS: "🏗️",
            TaskStatus.COMPLETED: "✅",
        }

    def __str__(self):
        return f"{self.emoji_map().get(self, '❓')}"


# Forward declaration for type hinting relationships
class Project(SQLModel):  # Removed table=True
    pass


class Area(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)  # Assuming area names should be unique
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    projects: List["Project"] = Relationship(back_populates="area")


class Project(SQLModel, table=True):  # Full definition of Project # noqa: F811
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    area_id: Optional[int] = Field(default=None, foreign_key="area.id", index=True)
    area: Optional["Area"] = Relationship(back_populates="projects")

    tasks: List["Task"] = Relationship(back_populates="project")


class TaskBase(SQLModel):  # Fields common to creation and reading, not a table
    title: str
    description: Optional[str] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    project_id: Optional[int] = Field(
        default=None, foreign_key="project.id", index=True
    )


class Task(TaskBase, table=True):  # This is your DB table model
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    project: Optional["Project"] = Relationship(back_populates="tasks")


# Schemas for API/CLI input and output if they differ from the table model
# For now, we can often use the table models directly or the Base models


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # project: Optional[ProjectRead] = None # If you want to nest project details


class TaskUpdate(SQLModel):  # Only fields that are updatable
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    project_id: Optional[int] = None


class ProjectCreate(SQLModel):
    name: str
    description: Optional[str] = None
    area_id: Optional[int] = None


class ProjectRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    area_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # area: Optional[AreaRead] = None # If you want to nest area details
    # tasks: List[TaskRead] = [] # If you want to nest task details


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    area_id: Optional[int] = None


class AreaCreate(SQLModel):
    name: str
    description: Optional[str] = None


class AreaRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # projects: List[ProjectRead] = [] # If you want to nest project details


class AreaUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


# To handle the forward references for relationships, update them after all models are defined.
# This is often needed if models reference each other.
# However, SQLModel is usually good at resolving string type hints like "Project".
# If you encounter issues, you might explicitly call:
# Project.model_rebuild()
# Area.model_rebuild()
# Task.model_rebuild()
