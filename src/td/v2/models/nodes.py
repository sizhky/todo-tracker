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


class TimeEntryV2(SQLModel, table=True):
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
    parent_id: Optional[UUID] = None
    type: Optional[NodeType] = None
    path: Optional[str] = None


class NodeDelete(BlankModel):
    id: Optional[UUID] = None
    path: Optional[str] = None


class NodeRead(BaseModel):
    id: Optional[UUID] = None
    path: Optional[str] = None


class NodeSearch(BlankModel):
    query: str = PField(position=1)
    path: Optional[str] = None


class NodeUpdate(NodeCreate):
    id: Optional[UUID] = None
    title: Optional[str] = None
    meta: Optional[str] = None
    path: Optional[str] = None


class NodeOut(NodeRead):
    title: str
    type: Optional[NodeType]
    status: NodeStatus
    parent_id: Optional[UUID]
    order: Optional[float]
    meta: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = False


class SectorMixin(BlankModel):
    type: NodeType = PField(default=NodeType.sector, frozen=True)


class SectorCreate(SectorMixin, NodeCreate): ...


class SectorRead(SectorMixin, NodeRead): ...


class SectorUpdate(SectorMixin, NodeUpdate): ...


class SectorDelete(SectorMixin, NodeDelete): ...


class SectorOut(SectorMixin, NodeOut): ...


class SectorSearch(SectorMixin, NodeSearch): ...


class AreaMixin(BlankModel):
    type: NodeType = PField(default=NodeType.area, frozen=True)
    parent_type: NodeType = PField(default=NodeType.sector, frozen=True)


class AreaCreate(AreaMixin, NodeCreate):
    sector_name: str = PField(default="_")


class AreaRead(AreaMixin, NodeRead): ...


class AreaUpdate(AreaMixin, NodeUpdate): ...


class AreaDelete(AreaMixin, NodeDelete): ...


class AreaSearch(AreaMixin, NodeSearch):
    sector_name: str = PField(default="_")


class AreaOut(AreaMixin, NodeOut): ...


class ProjectMixin(BlankModel):
    type: NodeType = PField(default=NodeType.project, frozen=True)
    parent_type: NodeType = PField(default=NodeType.area, frozen=True)


class ProjectCreate(ProjectMixin, NodeCreate):
    area_name: str = PField(default="_")
    sector_name: str = PField(default="_")


class ProjectRead(ProjectMixin, NodeRead): ...


class ProjectUpdate(ProjectMixin, NodeUpdate): ...


class ProjectDelete(ProjectMixin, NodeDelete): ...


class ProjectSearch(ProjectMixin, NodeSearch):
    area_name: str = PField(default="_")


class ProjectOut(ProjectMixin, NodeOut): ...


class SectionMixin(BlankModel):
    type: NodeType = PField(default=NodeType.section, frozen=True)
    parent_type: NodeType = PField(default=NodeType.project, frozen=True)


class SectionCreate(SectionMixin, NodeCreate):
    project_name: str = PField(default="_")
    area_name: str = PField(default="_")
    sector_name: str = PField(default="_")


class SectionRead(SectionMixin, NodeRead): ...


class SectionUpdate(SectionMixin, NodeUpdate): ...


class SectionDelete(SectionMixin, NodeDelete): ...


class SectionSearch(SectionMixin, NodeSearch):
    area_name: str = PField(default="_")


class SectionOut(SectionMixin, NodeOut): ...


class TaskMixin(BlankModel):
    type: NodeType = PField(default=NodeType.task, frozen=True)
    parent_type: NodeType = PField(default=NodeType.section, frozen=True)


class TaskCreate(TaskMixin, NodeCreate):
    section_name: str = PField(default="_")
    project_name: str = PField(default="_")
    area_name: str = PField(default="_")
    sector_name: str = PField(default="_")


class TaskRead(TaskMixin, NodeRead): ...


class TaskUpdate(TaskMixin, NodeUpdate): ...


class TaskDelete(TaskMixin, NodeDelete): ...


class TaskSearch(TaskMixin, NodeSearch): ...


class TaskOut(TaskMixin, NodeOut): ...


SCHEMA_OUT_MAPPING = {
    NodeType.sector: SectorOut,
    NodeType.area: AreaOut,
    NodeType.project: ProjectOut,
    NodeType.section: SectionOut,
    NodeType.task: TaskOut,
}
