from datetime import datetime
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
    TaskCreate,
)
from ..core.db import engine  # Import the engine to create a session if needed

# from rich import print

SchemaIn = TypeVar("SchemaIn")
SchemaOut = TypeVar("SchemaOut")


class NodeCrud:
    def __init__(
        self,
        node_type: NodeType,
        schema_out: Type[SchemaOut],
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
        if data.path is not None:
            # If path is provided, split it and create nodes for each part
            path = data.path.strip("/").split("/")
            try:
                data.sector_name = path[0]
                data.area_name = path[1] if len(path) > 1 else "_"
                data.project_name = path[2] if len(path) > 2 else "_"
                data.section_name = path[3] if len(path) > 3 else "_"
                data.task_name = path[4] if len(path) > 4 else "_"
            except Exception as _:
                pass
        if "," in data.title:
            # If title contains a comma, split it and create nodes for each part
            for title in data.title.split(","):
                _data = data.copy()
                _data.title = title.strip()
                self.create_hierarchy(_data)
            return
        HIERARCHY = [
            (SectorCreate, "sector_name"),
            (AreaCreate, "area_name"),
            (ProjectCreate, "project_name"),
            (SectionCreate, "section_name"),
            (TaskCreate, "task_name"),
        ]

        parent_id = None
        node = None

        for schema_cls, attr in HIERARCHY:
            # Skip levels not present in input
            if not hasattr(data, attr) and not isinstance(data, schema_cls):
                break

            title = (
                data.title
                if isinstance(data, schema_cls)
                else getattr(data, attr, None)
            )
            if not title:
                break

            payload = schema_cls(title=title, parent_id=parent_id)
            node = self.get_or_create(payload)
            parent_id = node.id

        return SCHEMA_OUT_MAPPING[node.type](**node.dict()) if node else None

    def _fetch_from_hierarchy(self, path):
        # Fetch the hierarchy from the database
        path = path.strip("/").split("/")
        HIERARCHY = []
        try:
            sector_name = path[0]
            HIERARCHY.append((NodeType.sector, sector_name))
            area_name = path[1]
            HIERARCHY.append((NodeType.area, area_name))
            project_name = path[2]
            HIERARCHY.append((NodeType.project, project_name))
            section_name = path[3]
            HIERARCHY.append((NodeType.section, section_name))
            task_name = path[4]
            HIERARCHY.append((NodeType.task, task_name))
        except Exception as _:
            pass
        parent_id = None
        node = None
        for node_type, title in HIERARCHY:
            if not title:
                break
            node = self.db.exec(
                select(Node)
                .where(Node.type == node_type)
                .where(Node.title == title)
                .where(Node.parent_id == parent_id)
            ).first()
            if not node:
                break
            parent_id = node.id
        return node

    def _create(self, data: SchemaIn) -> SchemaOut:
        data_dict = data.dict()
        parent_type = data_dict.pop("parent_type", None)
        if parent_type:
            parent_type = parent_type.name
            parent_node = None
            if "parent_id" in data_dict and data_dict["parent_id"]:
                parent_id = data_dict.pop("parent_id")
                parent_node = self.db.exec(
                    select(Node)
                    .where(Node.id == parent_id)
                    .where(Node.type == NodeType[parent_type])
                ).first()
                if not parent_node:
                    raise ValueError(f"Parent node with ID {parent_id} not found")
            elif f"{parent_type}_name" in data_dict:
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

            if parent_node:
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
        if in_debug_mode():
            line()
            print(f"get_children\nInput: {data}\n\nResults: {children}")
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
        self, title: str, type: NodeType = None, parent_id: Optional[UUID] = None
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
        node_type = data_dict.get("type", None)
        result = self._search_by_title(query, type=node_type)
        if self.source == "cli":
            print(result)
        return result

    def update(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        if data_dict.get("path"):
            node = self._fetch_from_hierarchy(data_dict["path"])
        else:
            node_id = data_dict.pop("id", None)
            if node_id is None:
                raise ValueError("Node ID is required for update")
            node = self.db.get(Node, node_id)
        if node is None or node.type != self.node_type:
            return None
        for key, value in data_dict.items():
            if not hasattr(node, key) or value is None:
                continue
            setattr(node, key, value)
        node.updated_at = datetime.now()
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

    def toggle_critical(self, data: SchemaIn) -> Optional[SchemaOut]:
        if data.title.startswith("*"):
            data.title = data.title[1:-1]
        else:
            data.title = f"*{data.title}*"
        self.update(data)

    def toggle_complete(self, data: SchemaIn) -> Optional[SchemaOut]:
        data.status = 10 if data.status == 0 else 0
        self.update(data)


def make_crud_for(node_type: NodeType, schema_out: Type[BaseModel]):
    crud = NodeCrud(node_type, schema_out)
    return AD(
        {
            "Create": crud.create_hierarchy,
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
