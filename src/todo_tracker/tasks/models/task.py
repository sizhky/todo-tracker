from datetime import datetime
from typing import Optional, Union
import math
from pydantic import BaseModel, Field, field_validator
import enum

class TaskStatus(str, enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in-progress'
    COMPLETED = 'completed'

    def emoji_map(self):
        return {
            TaskStatus.PENDING: '⏳',
            TaskStatus.IN_PROGRESS: '🏗️',
            TaskStatus.COMPLETED: '✅'
        }

    def __str__(self):
        return f'{self.emoji_map().get(self, "❓")}'

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
        print(f"[{self.id}] - {self.status} - {self.title}")
        description = self.description
        if description and description == description:
            print(f"    {self.description}")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }