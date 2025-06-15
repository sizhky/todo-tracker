from typing import Optional, List, TYPE_CHECKING  # Added TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone

# Assuming Area is in area.py
if TYPE_CHECKING:  # Added this block
    from .area import Area, AreaRead


# Forward declaration for type hinting relationships
class Task(SQLModel):
    pass


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    area_id: Optional[int] = Field(default=None, foreign_key="area.id", index=True)
    area: Optional["Area"] = Relationship(back_populates="projects")

    tasks: List["Task"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"cascade": "all, delete"}
    )


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
    area: Optional["AreaRead"] = None  # Ensure AreaRead is available
    # tasks: List["TaskRead"] = [] # If you want to nest task details


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    area_id: Optional[int] = None


# Update model references if needed
# Project.model_rebuild()
