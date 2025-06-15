from datetime import datetime, timezone
from torch_snippets import ifnone, AD

from sqlmodel import SQLModel, Field, Relationship, Column, SmallInteger, select
from typing import Optional, List, Union
from uuid import uuid4, UUID
from enum import Enum
from sqlalchemy import Index
from pydantic import BaseModel, model_validator


class NodeType(int, Enum):
    sector = 1
    area = 100
    project = 200
    section = 300
    task = 400
    subtask = 500

    def __str__(self):
        return NODE_TYPE_ALIASES.get(self, self.name)


NODE_TYPE_ALIASES = {
    NodeType.sector: "sr",
    NodeType.area: "a",
    NodeType.project: "p",
    NodeType.section: "sn",
    NodeType.task: "t",
    NodeType.subtask: "st",
}


class NodeStatus(int, Enum):
    active = 0
    completed = 10
    archived = 20


class Node(SQLModel, table=True):
    __tablename__ = "node"
    __table_args__ = (
        Index("idx_node_title_type", "title", "type"),
        Index("idx_node_path", "path"),
        Index("idx_node_path_title", "path", "title"),
        Index("idx_node_path_title_unique", "path", "title", unique=True),
        {"extend_existing": True, "sqlite_autoincrement": True},
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    title: str
    type: NodeType = Field(sa_column=Column(SmallInteger))
    status: NodeStatus = Field(
        sa_column=Column(SmallInteger), default=NodeStatus.active
    )
    parent_id: Optional[UUID] = Field(default=None, foreign_key="node.id", index=True)
    order: Optional[float] = Field(default=0)
    meta: Optional[str] = Field(default="{}")
    path: Optional[str] = Field(
        default=None
    )  # the path to the node in the tree of todos
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # One-to-many relationship (parent to children)
    children: List["Node"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


class NodePathMixin(BaseModel):
    @model_validator(mode="before")
    @classmethod
    def infer_type_path_and_title(cls, values):
        node_type_sequence = [
            NodeType.sector,
            NodeType.area,
            NodeType.project,
            NodeType.section,
            NodeType.task,
            NodeType.subtask,
        ]
        path = values.get("path")
        path = ifnone(path, "").strip("/")
        if not values.get("title") and not path:
            raise ValueError("Either title or path must be provided")
        elif values.get("title") and not path:
            assert "/" not in values["title"], "Title cannot contain '/'"
            values["path"] = ""
            values["type"] = NodeType.sector
            return values
        elif path and not values.get("title"):
            path_parts = path.split("/")
            depth = len(path_parts) - 1
            values["type"] = node_type_sequence[depth]
            values["title"] = path_parts[-1]
            values["path"] = "/".join(path_parts[:-1])
        else:
            assert "/" not in values["title"], "Title cannot contain '/'"
            path_parts = path.split("/")
            depth = len(path_parts)
            values["type"] = node_type_sequence[depth]
            values["path"] = path.strip("/")
        assert values["title"] != "d", (
            "For some stupid reason, 'd' is not allowed as a title"
        )
        return values


class NodeCreate(NodePathMixin):
    title: Optional[str] = None  # title can sometimes be inferred from the path itself
    type: Optional[NodeType] = None
    path: Optional[str] = ""
    status: Optional[NodeStatus] = NodeStatus.active
    order: Optional[float] = None
    meta: Optional[str] = None
    parent_id: Optional[UUID] = None


class NodeRead(NodePathMixin):
    path: str
    title: Optional[str] = None


class NodeUpdate(NodeRead):
    status: Optional[NodeStatus] = None
    order: Optional[float] = None
    meta: Optional[str] = None
    new_title: Optional[str] = None
    new_path: Optional[str] = None
    new_status: Optional[NodeStatus] = None
    new_order: Optional[float] = None
    new_meta: Optional[str] = None

    def make_old_and_new_nodes(self):
        old_node = NodeRead(
            title=self.title,
            path=self.path,
        )
        """
        NU(path='')
        
        """
        if self.new_path is None and self.new_title is None:
            self.new_path = self.path
            self.new_title = self.title
        elif self.new_path is None and self.new_title is not None:
            self.new_path = self.path

        new_node = NodeCreate(
            title=self.new_title,
            path=self.new_path,
            status=self.new_status if self.new_status is not None else self.status,
            order=self.new_order if self.new_order is not None else self.order,
            meta=self.new_meta if self.new_meta is not None else self.meta,
            parent_id=None,
        )
        # print(f"Old Node: {old_node}\nNew Node: {new_node}\n\n")
        return old_node, new_node


class NodeDelete(NodeRead): ...


class NodeOutput(BaseModel):
    path: str
    id: UUID
    title: str
    type: NodeType
    status: NodeStatus
    order: float = None
    meta: str = None
    parent_id: UUID | None
    updated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = False

    def __repr__(self):
        parent_id = "" if not hasattr(self, "parent_id") else str(self.parent_id)[:4]
        return f"🧩{self.title[:4]}... ({self.type}) # {str(self.id)[:4]} @ {parent_id}"

    __str__ = __repr__

    def __repr0__(self):
        indent = "  "
        depth = 0 if not self.path else self.path.strip("/").count("/") + 1
        prefix = indent * depth
        repr_str = f"{prefix}{self.title}"
        if hasattr(self, "children") and self.children:
            child_reprs = "\n".join(repr(child) for child in self.children)
            return f"{repr_str}\n{child_reprs}"
        return repr_str


class SubtaskOutput(NodeOutput):
    type: NodeType = NodeType.subtask
    parent_id: UUID


class TaskOutput(NodeOutput):
    type: NodeType = NodeType.task
    parent_id: UUID
    children: List[SubtaskOutput]


class SectionOutput(NodeOutput):
    type: NodeType = NodeType.section
    children: List[TaskOutput]


class ProjectOutput(NodeOutput):
    type: NodeType = NodeType.project
    children: List[SectionOutput]


class AreaOutput(NodeOutput):
    type: NodeType = NodeType.area
    children: List[ProjectOutput]


class SectorOutput(NodeOutput):
    type: NodeType = NodeType.sector
    children: List[AreaOutput] = []
    parent_id: None = None

    def __init__(self, **data):
        if "parent_id" in data and data["parent_id"] is not None:
            raise ValueError("SectorOutput should not have a parent_id")
        super().__init__(**data)


NodeOutputType = Union[
    SectorOutput, AreaOutput, ProjectOutput, SectionOutput, TaskOutput
]

OUTPUT_TYPE_REGISTRY = {
    NodeType.sector: SectorOutput,
    NodeType.area: AreaOutput,
    NodeType.project: ProjectOutput,
    NodeType.section: SectionOutput,
    NodeType.task: TaskOutput,
    NodeType.subtask: SubtaskOutput,
}
