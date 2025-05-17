from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship, Column, SmallInteger
from typing import Optional, List
from uuid import uuid4, UUID
from enum import Enum
from pydantic import BaseModel, Field as PField
from sqlalchemy import Index


class NodeType(int, Enum):
    sector = 1
    area = 100
    project = 200
    section = 300
    task = 400
    subtask = 500


class NodeStatus(int, Enum):
    active = 0
    completed = 10
    archived = 20


class Node(SQLModel, table=True):
    __tablename__ = "node"
    __table_args__ = (
        Index("idx_node_title_type", "title", "type"),
        {"extend_existing": True},
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str
    type: NodeType = Field(sa_column=Column(SmallInteger))
    status: NodeStatus = Field(
        sa_column=Column(SmallInteger), default=NodeStatus.active
    )
    parent_id: Optional[UUID] = Field(default=None, foreign_key="node.id", index=True)
    order: Optional[float] = Field(default=None)
    meta: Optional[str] = Field(default="{}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # One-to-many relationship (parent to children)
    children: List["Node"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entry"
    __table_args__ = {"extend_existing": True}

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    task_id: UUID = Field(foreign_key="node.id", index=True)
    start: datetime
    end: Optional[datetime] = None
    duration: Optional[float] = None  # seconds, computed on close
    note: Optional[str] = None


class BlankModel(BaseModel): ...


class NodeCreate(BlankModel):
    title: str = PField(position=1)
    meta: Optional[str] = "{}"


class NodeDelete(BlankModel):
    id: UUID


class NodeRead(BaseModel):
    id: UUID


class NodeSearch(BlankModel):
    query: str = PField(position=1)


class NodeUpdate(NodeCreate):
    id: UUID
    title: Optional[str] = None
    meta: Optional[str] = None


class NodeOut(NodeRead):
    title: str
    type: NodeType
    status: NodeStatus
    parent_id: Optional[UUID]
    order: Optional[float]
    meta: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SectorMixin(BlankModel):
    type: NodeType = PField(default=NodeType.sector, frozen=True)


class SectorCreate(NodeCreate, SectorMixin): ...


class SectorRead(NodeRead, SectorMixin): ...


class SectorUpdate(NodeUpdate, SectorMixin): ...


class SectorDelete(NodeDelete, SectorMixin): ...


class SectorOut(NodeOut, SectorMixin): ...


class SectorSearch(NodeSearch, SectorMixin): ...


class AreaMixin(BlankModel):
    type: NodeType = PField(default=NodeType.area, frozen=True)
    parent_type: NodeType = PField(default=NodeType.sector, frozen=True)


class AreaCreate(NodeCreate, AreaMixin):
    sector_name: str = PField(default="_default")


class AreaRead(NodeRead, AreaMixin): ...


class AreaOut(NodeOut, AreaMixin): ...


SCHEMA_OUT_MAPPING = {
    NodeType.sector: SectorOut,
    NodeType.area: AreaOut,
}
