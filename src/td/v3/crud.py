from torch_snippets import AD
from sqlmodel import Session, select
from sqlalchemy import text
from .core import engine
from td.v3 import (
    Node,
    NodeRead,
    NodeCreate,
    NodeUpdate,
    NodeOutputType,
    OUTPUT_TYPE_REGISTRY,
    NodeStatus,
)


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
        if "," in node.title:
            parent = self._get_or_create_parent(node)
            if parent:
                node.parent_id = parent.id
            o = []
            for _title in node.title.split(","):
                _node = NodeCreate(
                    title=_title.strip(),
                    path=node.path,
                    type=node.type,
                    parent_id=node.parent_id,
                )
                o.append(self._create_node(_node))
            return o
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
            try:
                return self._read_node(node)
            except ValueError:
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
            try:
                return self._read_node(NodeRead(title=node.path, path=""))
            except ValueError:
                parent = NodeCreate(title=node.path, path="")
                return self._create_node(parent)

    def _read_node(self, node_in: NodeRead) -> NodeOutputType:
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

    def _read_nodes(self) -> list[NodeOutputType]:
        nodes = self.db.exec(select(Node).where(Node.path == "")).all()
        return [OUTPUT_TYPE_REGISTRY[node.type].from_orm(node) for node in nodes]

    @property
    def tree(self) -> AD:
        def build_tree(nodes: list[NodeOutputType], visited: set) -> AD:
            o = AD()
            for s in nodes:
                if s.id in visited:
                    continue
                visited.add(s.id)
                if not hasattr(s, "children") or not s.children:
                    o[s.title] = s
                else:
                    o[s.title] = AD()
                    o[s.title]["__node"] = s
                    o[s.title].update(build_tree(s.children, visited))
            return o

        nodes = self._read_nodes()
        return build_tree(nodes, set())

    def _update_node(self, node_in: NodeUpdate) -> NodeOutputType:
        """
        Update a node in the database.
        """
        if not node_in:
            return None
        old_node, new_node = node_in.make_old_and_new_nodes()
        node = self.db.exec(
            select(Node)
            .where(Node.title == old_node.title)
            .where(Node.path == old_node.path)
        ).first()
        if not node:
            raise ValueError(
                f"Node with title {old_node.title} and path {old_node.path} not found."
            )
        if new_node.path:
            _path_parts = new_node.path.strip("/").split("/")
            if _path_parts:
                _parent_path = "/".join(_path_parts[:-1])
                _parent_title = _path_parts[-1] if _parent_path else _path_parts[0]
                parent = self.db.exec(
                    select(Node)
                    .where(Node.path == _parent_path)
                    .where(Node.title == _parent_title)
                ).first()
                if parent:
                    node.parent_id = parent.id
        for key, value in new_node.model_dump(exclude_unset=True).items():
            key = key.replace("new_", "")
            if value is None:
                continue
            setattr(node, key, value)
        self.db.add(node)
        self.db.commit()
        self.db.refresh(node)
        node = OUTPUT_TYPE_REGISTRY[node.type].from_orm(node)
        return node

    def promote_node(self, node: NodeRead) -> NodeOutputType:
        """
        Promote a node and its children one level up in the hierarchy.
        """
        raw_node = self.db.exec(
            select(Node).where(Node.title == node.title).where(Node.path == node.path)
        ).first()
        if not raw_node:
            raise ValueError(
                f"Node with title {node.title} and path {node.path} not found."
            )
        parent_node = (
            self.db.get(Node, raw_node.parent_id) if raw_node.parent_id else None
        )
        grandparent_node = (
            self.db.get(Node, parent_node.parent_id) if parent_node else None
        )
        if not parent_node or not grandparent_node:
            raise ValueError("Cannot promote top-level or orphaned node.")

        # Update the node's path and type
        old_path = raw_node.path
        new_path = grandparent_node.path
        if new_path:
            new_path += f"/{grandparent_node.title}"
        raw_node.path = new_path
        raw_node.type = parent_node.type  # promote to parent's level
        raw_node.parent_id = grandparent_node.id
        self.db.add(raw_node)

        # Update all children recursively
        def update_descendants(current_node, old_prefix, new_prefix):
            children = self.db.exec(
                select(Node).where(Node.parent_id == current_node.id)
            ).all()
            for child in children:
                if child.path.startswith(old_prefix):
                    child.path = child.path.replace(old_prefix, new_prefix, 1)
                child.parent_id = current_node.id
                self.db.add(child)
                update_descendants(child, old_prefix, new_prefix)

        update_descendants(raw_node, old_path, raw_node.path)
        self.db.commit()
        self.db.refresh(raw_node)
        return OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node)

    def toggle_critical(self, node: NodeRead) -> NodeOutputType:
        """
        Toggle the critical status of a node.
        """
        raw_node = self.db.exec(
            select(Node).where(Node.title == node.title).where(Node.path == node.path)
        ).first()
        if not raw_node:
            raise ValueError(
                f"Node with title {node.title} and path {node.path} not found."
            )
        raw_node.title = (
            f"*{raw_node.title}*"
            if not raw_node.title.startswith("*")
            else raw_node.title.strip("*")
        )
        self.db.add(raw_node)
        self.db.commit()
        self.db.refresh(raw_node)
        return OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node)

    def toggle_complete(self, node: NodeRead) -> NodeOutputType:
        """
        Toggle the completion status of a node.
        """
        raw_node = self.db.exec(
            select(Node).where(Node.title == node.title).where(Node.path == node.path)
        ).first()
        if not raw_node:
            raise ValueError(
                f"Node with title {node.title} and path {node.path} not found."
            )
        raw_node.status = (
            NodeStatus.completed
            if raw_node.status != NodeStatus.completed
            else NodeStatus.active
        )
        self.db.add(raw_node)
        self.db.commit()
        self.db.refresh(raw_node)
        return OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node)

    def WIPE_DB(self):
        """
        Delete all nodes from the database.
        """
        self.db.exec(text("DELETE FROM node"))
        self.db.commit()
