from torch_snippets import AD, in_debug_mode, line
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel
from sqlmodel import Session, select
from uuid import UUID
from ..models.nodes import (
    Node,
    NodeType,
    SCHEMA_OUT_MAPPING,
    NodeRead,
    SectorCreate,
    AreaCreate,
    ProjectCreate,
    SectionCreate,
    NodeCreate,
)
from ..core.db import engine  # Import the engine to create a session if needed

# from rich import print

SchemaIn = TypeVar("SchemaIn")
SchemaOut = TypeVar("SchemaOut")


class NodeCrud:
    def __init__(
        self,
        node_type: NodeType,
        schema_out: Type[SchemaOut] = None,
        db: Optional[Session] = None,
    ):
        self.node_type = node_type
        self.schema_out = schema_out if schema_out else SCHEMA_OUT_MAPPING[node_type]
        self.db = db if db is not None else Session(engine)
        self.should_close_db = db is None  # Track if we created the session

    def __del__(self):
        # Close the session if we created it
        if (
            hasattr(self, "should_close_db")
            and self.should_close_db
            and hasattr(self, "db")
        ):
            self.db.close()

    @property
    def source(self):
        return getattr(self, "_source", None)

    def create_hierarchy(self, data: SchemaIn) -> Optional[SchemaOut]:
        title = data.title if isinstance(data, SectorCreate) else data.sector_name
        sector = self.get_or_create(SectorCreate(title=title))
        if not getattr(data, "area_name", None) and not isinstance(data, AreaCreate):
            return SCHEMA_OUT_MAPPING[sector.type](**sector.dict())
        title = data.title if isinstance(data, AreaCreate) else data.area_name
        area = self.get_or_create(
            AreaCreate(title=title, parent_id=sector.id, parent_type=NodeType.sector)
        )
        if not getattr(data, "project_name", None) and not isinstance(
            data, ProjectCreate
        ):
            return SCHEMA_OUT_MAPPING[area.type](**area.dict())
        title = data.title if isinstance(data, ProjectCreate) else data.project_name
        project = self.get_or_create(
            ProjectCreate(title=title, parent_id=area.id, parent_type=NodeType.area)
        )
        if not getattr(data, "section_name", None) and not isinstance(
            data, SectionCreate
        ):
            return SCHEMA_OUT_MAPPING[project.type](**project.dict())
        title = data.title if isinstance(data, SectionCreate) else data.section_name
        section = self.get_or_create(
            SectionCreate(
                title=title, parent_id=project.id, parent_type=NodeType.project
            )
        )
        return SCHEMA_OUT_MAPPING[section.type](**section.dict())

    def _create(self, data: SchemaIn) -> SchemaOut:
        data_dict = data.dict()
        parent_type = data_dict.pop("parent_type", None)
        if parent_type:
            parent_type = parent_type.name
            if "parent_id" in data_dict:
                parent_id = data_dict.pop("parent_id")
                parent_node = self.db.exec(
                    select(Node)
                    .where(Node.id == parent_id)
                    .where(Node.type == NodeType[parent_type])
                ).first()
                if not parent_node:
                    raise ValueError(f"Parent node with ID {parent_id} not found")
            elif "parent_name" in data_dict:
                parent_node_name = data_dict.pop(f"{parent_type}_name")
                parent_node = self.db.exec(
                    select(Node)
                    .where(Node.title == parent_node_name)
                    .where(Node.type == NodeType[parent_type])
                ).first()
                if not parent_node:
                    parent_node = self._create(
                        NodeCreate(
                            title=parent_node_name,
                            type=NodeType[parent_type],
                            parent_id=None,
                        )
                    )
            data_dict["parent_id"] = parent_node.id

        if "type" not in data_dict:
            data_dict["type"] = self.node_type
        if "," in data_dict["title"]:
            for title in data_dict["title"].split(","):
                _data = data.copy()
                _data.title = title.strip()
                self.create(_data)
            return
        node = Node(**data_dict)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        o = self.schema_out.from_orm(node)
        if in_debug_mode():
            line()
            print(f"_CREATE\nInput: {data}\nOutput: {o}")
        return o

    def create(self, data: SchemaIn) -> Optional[SchemaOut]:
        o = self._create(data)
        if self.source == "cli":
            print(o)
        return o

    def __getitem__(self, input):
        # if input is like a uuid
        if isinstance(input, UUID):
            o = self.read(NodeRead(id=str(input)))
            return SCHEMA_OUT_MAPPING[o.type](**o.dict())

    def get_children(self, data: SchemaIn, recursive: bool = False) -> List[SchemaOut]:
        """Get children of a node by its ID"""
        node_id = data.dict().get("id")
        if not node_id:
            return []
        node = self.db.get(Node, node_id)
        if node is None:
            return []
        children = self.db.exec(select(Node).where(Node.parent_id == node.id)).all()
        if recursive:
            for child in children:
                child.children = self.get_children(child.id, recursive=True)
        return [self.schema_out.from_orm(child) for child in children]

    def _read(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        node_id = data_dict.pop("id", None)
        if node_id is None:
            raise ValueError("Node ID is required for read")
        node = self.db.get(Node, node_id)
        if node is None:
            return None
        o = self.schema_out.from_orm(node)
        return o

    def read(self, data: SchemaIn) -> Optional[SchemaOut]:
        o = self._read(data)
        if self.source == "cli":
            print(o)
        return o

    def get_or_create(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        title = data_dict.pop("title", None)
        type = data_dict.pop("type", None)
        parent_id = data_dict.pop("parent_id", None)
        results = self._search_by_title(title=title, type=type, parent_id=parent_id)
        if in_debug_mode():
            line()
            print(f"get_or_create\nInput: {data}\n\nResults: {results}")
        if not results:
            return self._create(data)
        return results[0]

    def _read_all(self):
        nodes = self.db.exec(select(Node).where(Node.type == self.node_type)).all()
        o = [self.schema_out.from_orm(n) for n in nodes]
        return o

    def read_all(self) -> List[SchemaOut]:
        o = self._read_all()
        if self.source == "cli":
            print(o)
        return o

    def _search_by_title(
        self, title: str, type: NodeType, parent_id: Optional[UUID]
    ) -> List[SchemaOut]:
        """Search for nodes by title (case-insensitive)
        This will use the composite index on (title, type) for efficient searches.
        """

        # Using LIKE for case-insensitive search with wildcard
        statement = select(Node).where(Node.type == type, Node.title == title)
        if parent_id:
            statement = statement.where(Node.parent_id == parent_id)
        nodes = self.db.exec(statement).all()
        result = [self.schema_out.from_orm(n) for n in nodes]
        return result

    def search_by_title(self, data: SchemaIn) -> List[SchemaOut]:
        data_dict = data.dict()
        query = data_dict.get("query", "")
        result = self._search_by_title(query)
        if self.source == "cli":
            print(result)
        return result

    def update(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        node_id = data_dict.pop("id", None)
        if node_id is None:
            raise ValueError("Node ID is required for update")
        node = self.db.get(Node, node_id)
        if node is None or node.type != self.node_type:
            return None
        for key, value in data_dict.items():
            setattr(node, key, value)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        o = self.schema_out.from_orm(node)
        if self.source == "cli":
            print(o)
        return o

    def delete(self, data: SchemaIn) -> bool:
        data_dict = data.dict()
        node_id = data_dict.pop("id", None)
        if node_id is None:
            raise ValueError("Node ID is required for deletion")

        node = self.db.get(Node, node_id)
        if node is None or node.type != self.node_type:
            return False
        self.db.delete(node)
        self.db.commit()
        if self.source == "cli":
            print(f"Node with ID {node_id} deleted")
        return True


def make_crud_for(node_type: NodeType, schema_out: Type[BaseModel]):
    crud = NodeCrud(node_type, schema_out)
    return AD(
        {
            "Create": crud.create,
            "Read": crud.read,
            "ReadAll": crud.read_all,
            "Update": crud.update,
            "Delete": crud.delete,
            "ReadOrCreate": crud.get_or_create,
            "SearchByTitle": crud.search_by_title,
            "_read_all": crud._read_all,
            "crud": crud,
        }
    )
