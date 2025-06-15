from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship, Column, SmallInteger
from typing import Optional, List
from uuid import uuid4, UUID
from enum import Enum


class NodeType(int, Enum):
    sector = 0
    area = 100
    project = 200
    section = 300
    task = 400
    subtask = 500


class Node(SQLModel, table=True):
    __tablename__ = "node"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str
    type: NodeType = Field(sa_column=Column(SmallInteger), index=True)
    parent_id: Optional[UUID] = Field(default=None, foreign_key="node.id", index=True)
    order: Optional[float] = Field(default=None)
    meta: Optional[str] = Field(default="{}")  # renamed from 'metadata'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    children: List["Node"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"cascade": "all, delete"},
    )
    parent: Optional["Node"] = Relationship(back_populates="children")


class TimeEntry(SQLModel, table=True):
    __tablename__ = "time_entry"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    task_id: UUID = Field(foreign_key="node.id", index=True)
    start: datetime
    end: Optional[datetime] = None
    duration: Optional[float] = None  # seconds, computed on close
    note: Optional[str] = None
