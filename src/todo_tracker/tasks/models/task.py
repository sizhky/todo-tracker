from datetime import datetime
from typing import Optional, Union
import math
from pydantic import BaseModel, Field, field_validator
import enum

class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in-progress'
    COMPLETED = 'completed'

class Task(BaseModel):
    id: int = Field(default=None)
    title: str
    description: Optional[Union[str,float]] = Field(default=None)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('description')
    def handle_nan_description(cls, v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return ''
        return v

    class Config:
        from_attributes = True

    def render(self):
        print(f"[{self.id}] {self.title} - {self.status}")
        description = self.description
        if description and description == description:
            print(f"    {self.description}")