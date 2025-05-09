from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone

from td.models.area import Area  # Assuming Area is in area.py


# Forward declaration for type hinting relationships
class Task(SQLModels):
    pass


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    area_id: Optional[int] = Field(default=None, foreign_key="area.id", index=True)
    area: Optional["Area"] = Relationship(back_populates="projects")

    tasks: List["Task"] = Relationship(back_populates="project")


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
    # area: Optional["AreaRead"] = None # If you want to nest area details
    # tasks: List["TaskRead"] = [] # If you want to nest task details


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    area_id: Optional[int] = None


# Update model references if needed
# Project.model_rebuild()
