from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone


# Forward declaration for type hinting relationships
class Project(SQLModel):
    pass


class Area(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, unique=True)  # Assuming area names should be unique
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    projects: List["Project"] = Relationship(
        back_populates="area", sa_relationship_kwargs={"cascade": "all, delete"}
    )


class AreaCreate(SQLModel):
    name: str
    description: Optional[str] = None


class AreaRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    # projects: List["ProjectRead"] = [] # If you want to nest project details


class AreaUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class AreaDelete(SQLModel):
    id: int


# Update model references if needed
# Area.model_rebuild()
