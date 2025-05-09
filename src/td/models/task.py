from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone
import enum

from td.models.project import Project  # Assuming Project is in project.py


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


# To handle the forward references for relationships, update them after all models are defined.
# This is often needed if models reference each other.
# However, SQLModel is usually good at resolving string type hints like "Project".
# If you encounter issues, you might explicitly call:
# Project.model_rebuild()
# Area.model_rebuild()
# Task.model_rebuild()
