from torch_snippets import AD
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel
from sqlmodel import Session, select
from uuid import UUID
from ..models.nodes import Node, NodeType, SCHEMA_OUT_MAPPING, NodeRead
from ..core.db import engine  # Import the engine to create a session if needed

from rich import print

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

    def _create(self, data: SchemaIn) -> SchemaOut:
        data_dict = data.dict()
        parent_type = data_dict.pop("parent_type", None)
        if parent_type:
            parent_type = parent_type.name
            parent_node_name = data_dict.pop(f"{parent_type}_name")
            parent_node = self.db.exec(
                select(Node)
                .where(Node.title == parent_node_name)
                .where(Node.type == NodeType[parent_type])
            ).first()
            if not parent_node:
                raise ValueError(
                    f"Parent node with title '{parent_node_name}' not found"
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

    def read(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        node_id = data_dict.pop("id", None)
        if node_id is None:
            raise ValueError("Node ID is required for read")
        node = self.db.get(Node, node_id)
        if node is None:
            return None
        o = self.schema_out.from_orm(node)
        if self.source == "cli":
            print(o)
        return o

    def read_or_create(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        title = data_dict.pop("title", None)
        results = self._search_by_title(title=title)
        if not results:
            return self._create(data)

    def _read_all(self):
        nodes = self.db.exec(select(Node).where(Node.type == self.node_type)).all()
        o = [self.schema_out.from_orm(n) for n in nodes]
        return o

    def read_all(self) -> List[SchemaOut]:
        o = self._read_all()
        if self.source == "cli":
            print(o)
        return o

    def _search_by_title(self, title: str) -> List[SchemaOut]:
        """Search for nodes by title (case-insensitive)
        This will use the composite index on (title, type) for efficient searches.
        """

        # Using LIKE for case-insensitive search with wildcard
        statement = select(Node).where(Node.type == self.node_type, Node.title == title)
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
            "ReadOrCreate": crud.read_or_create,
            "SearchByTitle": crud.search_by_title,
            "_read_all": crud._read_all,
            "crud": crud,
        }
    )
