from torch_snippets import AD
from typing import Type, TypeVar, Optional, List
from pydantic import BaseModel
from sqlmodel import Session, select
from ..models.nodes import Node, NodeType
from ..core.db import engine  # Import the engine to create a session if needed

from rich import print

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
        self.schema_out = schema_out
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

    def create(self, data: SchemaIn) -> SchemaOut:
        data_dict = data.dict()
        parent_type = data_dict.pop("parent_title", None)
        if parent_type:
            parent_node = self.db.exec(
                select(Node).where(Node.title == parent_type)
            ).first()
            if not parent_node:
                raise ValueError(f"Parent node with title '{parent_type}' not found")
            data_dict["parent_id"] = parent_node.id

        if "type" not in data_dict:
            data_dict["type"] = self.node_type
        node = Node(**data_dict)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        o = self.schema_out.from_orm(node)
        if self.source == "cli":
            print(o)
        return o

    def read(self, data: SchemaIn) -> Optional[SchemaOut]:
        data_dict = data.dict()
        node_id = data_dict.pop("id", None)
        if node_id is None:
            raise ValueError("Node ID is required for read")
        node = self.db.get(Node, node_id)
        if node is None or node.type != self.node_type:
            return None
        o = self.schema_out.from_orm(node)
        if self.source == "cli":
            print(o)
        return o

    def read_all(self) -> List[SchemaOut]:
        nodes = self.db.exec(select(Node).where(Node.type == self.node_type)).all()
        o = [self.schema_out.from_orm(n) for n in nodes]
        if self.source == "cli":
            print(o)
        return o

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
        }
    )
