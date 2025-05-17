from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .task import Task  # Forward reference for type hinting


class TimeEntryBase(SQLModel):
    task_id: int = Field(foreign_key="task.id", index=True)
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)


class TimeEntry(TimeEntryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    task: Optional["Task"] = Relationship(back_populates="time_entries")


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryRead(TimeEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime


class TimeEntryUpdate(SQLModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
