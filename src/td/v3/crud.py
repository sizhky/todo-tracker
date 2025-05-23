from sqlmodel import Session, select
from .core import engine
from td.v3 import Node, NodeCreate, NodeOutputType, OUTPUT_TYPE_REGISTRY


class NodeCrud:
    def __init__(self, db=None):
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

    def _create_node(self, node: NodeCreate) -> NodeOutputType:
        """
        Create a node in the database.
        """
        NodeCreate.model_validate(node)
        parent = self._get_or_create_parent(node)
        if parent:
            node.parent_id = parent.id
        node = node.model_dump()
        node = Node(**node)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)  # refresh is an inplace op
        node = OUTPUT_TYPE_REGISTRY[node.type].from_orm(node)
        return node

    def _get_or_create_parent(self, node: NodeCreate) -> NodeOutputType:
        """
        Get or create the parent ID for the node.
        """
        if node.parent_id:
            return self.db.get(Node, node.parent_id)
        if node.path == "":
            return None
        elif "/" in node.path:
            _path, _title = node.path.rsplit("/", 1)
            parent = self.db.exec(
                select(Node).where(Node.path == _path).where(Node.title == _title)
            ).first()
            if not parent:
                parent = NodeCreate(
                    title=_title,
                    path=_path,
                )
                parent = self._create_node(parent)
            return parent
        else:
            parent = NodeCreate(title=node.path, path="")
            return self._create_node(parent)

    def _read_node(self, node_in: Node) -> NodeOutputType:
        """
        Read a node from the database.
        """
        if not node_in:
            return None
        node = self.db.exec(
            select(Node)
            .where(Node.title == node_in.title)
            .where(Node.path == node_in.path)
        ).first()
        if not node:
            raise ValueError(
                f"Node with title {node_in.title} and path {node_in.path} not found."
            )
        node = OUTPUT_TYPE_REGISTRY[node.type].from_orm(node)
        return node
