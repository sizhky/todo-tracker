from datetime import datetime, timedelta, timezone
from torch_snippets import AD, flatten
from uuid import UUID
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
    NodeType,
)


def rollback_on_fail(fn):
    def wrapper(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except Exception:
            self.db.rollback()
            raise

    return wrapper


class NodeCrud:
    NODE_TYPE_SEQUENCE = [
        NodeType.sector,
        NodeType.area,
        NodeType.project,
        NodeType.section,
        NodeType.task,
        NodeType.subtask,
    ]
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

    @rollback_on_fail
    def _create_node(self, node: NodeCreate) -> NodeOutputType:
        """
        Create a node in the database.
        """
        existing = self.db.exec(
            select(Node).where(Node.title == node.title).where(Node.path == node.path)
        ).first()
        if existing:
            return OUTPUT_TYPE_REGISTRY[existing.type].from_orm(existing)
        if ";" in node.title:
            parent = self._get_or_create_parent(node)
            if parent:
                node.parent_id = parent.id
            o = []
            for _title in node.title.split(";"):
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

    def _read_root_nodes(self) -> list[NodeOutputType]:
        nodes = self.db.exec(select(Node).where(Node.path == "")).all()
        return [OUTPUT_TYPE_REGISTRY[node.type].from_orm(node) for node in nodes]

    def get_lineage(self, node: NodeRead) -> list[NodeOutputType]:
        """
        Return the lineage of a node from itself up to the root.
        """
        raw_node = self.db.exec(
            select(Node).where(Node.title == node.title).where(Node.path == node.path)
        ).first()
        if not raw_node:
            raise ValueError(
                f"Node with title {node.title} and path {node.path} not found."
            )

        lineage = []
        while raw_node:
            lineage.append(OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node))
            raw_node = (
                self.db.get(Node, raw_node.parent_id) if raw_node.parent_id else None
            )

        return lineage

    def _tree(self, ids: list[UUID] = None) -> AD:
        """
        Build a tree of nodes, optionally filtered by node IDs.
        """
        all_nodes = self.db.exec(select(Node)).all()
        if ids is not None:
            all_nodes = [n for n in all_nodes if n.id in ids]
        all_nodes = [OUTPUT_TYPE_REGISTRY[n.type].from_orm(n) for n in all_nodes]

        id_to_node = {n.id: n for n in all_nodes}
        parent_to_children = {}
        root_nodes = []

        for n in all_nodes:
            if n.parent_id:
                parent_to_children.setdefault(n.parent_id, []).append(n)
            else:
                root_nodes.append(n)

        skipped_ids = set()

        def should_skip(n):
            return (
                n.status == NodeStatus.completed
                and n.updated_at
                and n.updated_at < (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=5))
            )

        def mark_skipped(n):
            skipped_ids.add(n.id)
            for child in parent_to_children.get(n.id, []):
                mark_skipped(child)

        for node in all_nodes:
            if should_skip(node):
                mark_skipped(node)

        def build_tree(nodes):
            o = AD()
            for n in nodes:
                if n.id in skipped_ids:
                    continue
                children = parent_to_children.get(n.id, [])
                if not children:
                    o[n.title] = n
                else:
                    o[n.title] = AD()
                    o[n.title]["__node"] = n
                    o[n.title].update(build_tree(children))
            return o

        return build_tree(root_nodes)

    @property
    def tree(self) -> AD:
        return self._tree()

    def critical_nodes(self) -> AD:
        t = self.tree
        df1 = t.flatten_and_make_dataframe()
        df = df1[
            df1.apply(
                lambda row: any(isinstance(x, str) and "*" in x for x in row), axis=1
            )
        ]
        paths = flatten(
            df.apply(
                lambda row: [f"{x.path}/{x.title}" for x in row if hasattr(x, "path")],
                axis=1,
            ).tolist()
        )
        ids = set(
            [
                n.id
                for n in flatten(
                    [self.get_lineage(self._read_node(NodeRead(path=p))) for p in paths]
                )
            ]
        )
        return self._tree(ids=ids)

    @rollback_on_fail
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
        # delete the old node
        self.db.delete(node)
        # create the new node
        _new_node = NodeCreate(**old_node.model_dump(exclude_unset=True))
        for key, value in new_node.model_dump(exclude_unset=True).items():
            key = key.replace("new_", "")
            if value is None:
                continue
            setattr(_new_node, key, value)
        # ensure the new node does not exist in the db
        existing = self.db.exec(
            select(Node)
            .where(Node.title == _new_node.title)
            .where(Node.path == _new_node.path)
        ).first()
        if existing:
            raise ValueError(
                f"Node with title {_new_node.title} and path {_new_node.path} already exists."
            )
        new_node = self._create_node(_new_node)
        # self.db.add(node)
        # self.db.commit()
        # self.db.refresh(node)
        node = OUTPUT_TYPE_REGISTRY[new_node.type].from_orm(new_node)
        return node

    @rollback_on_fail
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
        new_path = parent_node.path
        raw_node.path = new_path
        raw_node.type = parent_node.type  # promote to parent's level
        raw_node.parent_id = grandparent_node.id
        self.db.add(raw_node)

        # Update all children recursively
        # Updated promote_node method with updated update_descendants function
        def update_descendants(current_node, old_prefix, new_prefix):
            children = self.db.exec(
                select(Node).where(Node.parent_id == current_node.id)
            ).all()
            for child in children:
                if child.path.startswith(old_prefix):
                    suffix = child.path[len(old_prefix) :]
                    if suffix.startswith("/"):
                        suffix = suffix[1:]
                    child.path = f"{new_prefix}/{suffix}" if new_prefix else suffix
                child.parent_id = current_node.id
                depth = child.path.strip("/").count("/") + 1 if child.path else 0
                child.type = self.NODE_TYPE_SEQUENCE[depth]
                self.db.add(child)
                update_descendants(child, old_prefix, new_prefix)

        update_descendants(raw_node, old_path, raw_node.path)
        self.db.commit()
        self.db.refresh(raw_node)
        return OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node)

    @rollback_on_fail
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
        raw_node.updated_at = datetime.now(timezone.utc)
        self.db.add(raw_node)
        self.db.commit()
        self.db.refresh(raw_node)
        return OUTPUT_TYPE_REGISTRY[raw_node.type].from_orm(raw_node)

    @rollback_on_fail
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
        raw_node.updated_at = datetime.now(timezone.utc)
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

    def get_node(self, node_read: NodeRead) -> Node:
        node = self.db.exec(
            select(Node).where(Node.title == node_read.title).where(Node.path == node_read.path)
        ).first()
        if not node:
            raise ValueError(
                f"Node with title {node_read.title} and path {node_read.path} not found."
            )
        return node

    def compute_new_path_and_type(self, node: Node, new_parent: Node) -> tuple[str, NodeType]:
        new_path = f"{new_parent.path}/{new_parent.title}" if new_parent.path else new_parent.title
        depth = new_path.strip("/").count("/") + 1
        new_type = self.NODE_TYPE_SEQUENCE[min(depth, len(self.NODE_TYPE_SEQUENCE) - 1)]
        return new_path, new_type

    def apply_move(self, node: Node, new_path: str, new_parent_id: UUID, new_type: NodeType):
        node.path = new_path
        node.parent_id = new_parent_id
        node.type = new_type
        self.db.add(node)

    def update_descendants(self, node: Node, old_prefix: str, new_prefix: str):
        children = self.db.exec(select(Node).where(Node.parent_id == node.id)).all()
        for child in children:
            if child.path.startswith(old_prefix):
                suffix = child.path[len(old_prefix):]
                if suffix.startswith("/"):
                    suffix = suffix[1:]
                child.path = f"{new_prefix}/{suffix}" if new_prefix else suffix
            child.parent_id = node.id
            depth = child.path.strip("/").count("/") + 1 if child.path else 0
            child.type = self.NODE_TYPE_SEQUENCE[min(depth, len(self.NODE_TYPE_SEQUENCE) - 1)]
            self.db.add(child)
            self.update_descendants(child, old_prefix, new_prefix)

    @rollback_on_fail
    def move_node(self, node_update: NodeUpdate) -> NodeOutputType:
        node_read, new_node = node_update.make_old_and_new_nodes()
        node = self.get_node(node_read)

        # Extract new parent details from new_node.path
        path_parts = new_node.path.strip("/").split("/") if new_node.path else []
        if not path_parts:
            raise ValueError("Cannot move node to root without proper path")

        new_parent_path = "/".join(path_parts[:-1])
        new_parent_title = path_parts[-2] if len(path_parts) > 1 else path_parts[0]

        new_parent = self.get_node(NodeRead(title=new_parent_title, path=new_parent_path))
        old_path = node.path
        new_path, new_type = self.compute_new_path_and_type(node, new_parent)
        self.apply_move(node, new_path, new_parent.id, new_type)
        self.update_descendants(node, old_path, new_path)
        self.db.commit()
        self.db.refresh(node)
        return OUTPUT_TYPE_REGISTRY[node.type].from_orm(node)