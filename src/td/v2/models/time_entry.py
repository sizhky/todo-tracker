from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class TimeEntryBase(BaseModel):
    task_id: UUID
    start: datetime
    end: Optional[datetime] = None
    note: Optional[str] = None


class TimeEntryCreate(TimeEntryBase):
    pass


class TimeEntryRead(TimeEntryBase):
    id: UUID
    duration: Optional[float] = None


class TimeEntryUpdate(BaseModel):
    end: Optional[datetime] = None
    note: Optional[str] = None
