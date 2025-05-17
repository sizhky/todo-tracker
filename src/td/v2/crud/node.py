from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from sqlmodel import Session, select

from ...models.v2.node import Node, NodeType

__all__ = [
    "create_node_in_db",
    "get_node_by_id",
    "get_children_of_node",
    "update_node_in_db",
    "delete_node_from_db",
    "get_nodes_by_type",
    "get_root_sectors",
    "update_node_order",
    "update_node_parent",
    "get_node_path",
]


def create_node_in_db(
    db: Session,
    title: str,
    type: NodeType,
    parent_id: Optional[UUID] = None,
    order: Optional[float] = None,
    meta: Dict[str, Any] = None,
) -> Node:
    """
    Create a new node (sector, area, project, section, task, subtask) in the database.
    """
    # Validate parent_id if provided
    if parent_id:
        parent = get_node_by_id(db, parent_id)
        if not parent:
            raise ValueError(f"Parent node with ID {parent_id} not found")

        # Check parent-child relationship logic
        if parent.type.value >= type.value:
            raise ValueError(f"A {type.name} cannot be a child of a {parent.type.name}")

    # Create node with metadata as JSON string
    meta_json = "{}" if meta is None else json.dumps(meta)

    node = Node(
        title=title, type=type, parent_id=parent_id, order=order, meta=meta_json
    )

    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_node_by_id(db: Session, node_id: UUID) -> Optional[Node]:
    """
    Retrieve a node by its ID.
    """
    return db.get(Node, node_id)


def get_children_of_node(
    db: Session, node_id: UUID, skip: int = 0, limit: int = 100
) -> List[Node]:
    """
    Retrieve all children of a specific node.
    """
    statement = (
        select(Node)
        .where(Node.parent_id == node_id)
        .order_by(Node.order)
        .offset(skip)
        .limit(limit)
    )
    results = db.exec(statement)
    return list(results.all())


def update_node_in_db(
    db: Session,
    node_id: UUID,
    title: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Optional[Node]:
    """
    Update an existing node's title and metadata.
    """
    node = get_node_by_id(db, node_id)
    if not node:
        return None

    if title is not None:
        node.title = title

    if meta is not None:
        node.meta = json.dumps(meta)

    node.updated_at = datetime.now(timezone.utc)

    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def delete_node_from_db(db: Session, node_id: UUID) -> bool:
    """
    Delete a node from the database by its ID.
    This will cascade delete all child nodes.
    Returns True if deleted, False otherwise.
    """
    node = get_node_by_id(db, node_id)
    if node:
        db.delete(node)
        db.commit()
        return True
    return False


def get_nodes_by_type(
    db: Session, node_type: NodeType, skip: int = 0, limit: int = 100
) -> List[Node]:
    """
    Retrieve all nodes of a specific type.
    """
    statement = (
        select(Node)
        .where(Node.type == node_type)
        .order_by(Node.order)
        .offset(skip)
        .limit(limit)
    )
    results = db.exec(statement)
    return list(results.all())


def get_root_sectors(db: Session, skip: int = 0, limit: int = 100) -> List[Node]:
    """
    Retrieve all root-level sectors (nodes with type=sector and no parent).
    """
    statement = (
        select(Node)
        .where(Node.type == NodeType.sector)
        .where(Node.parent_id.is_(None))
        .order_by(Node.order)
        .offset(skip)
        .limit(limit)
    )
    results = db.exec(statement)
    return list(results.all())


def update_node_order(db: Session, node_id: UUID, new_order: float) -> Optional[Node]:
    """
    Update the order of a node.
    """
    node = get_node_by_id(db, node_id)
    if not node:
        return None

    node.order = new_order
    node.updated_at = datetime.now(timezone.utc)

    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def update_node_parent(
    db: Session, node_id: UUID, new_parent_id: Optional[UUID]
) -> Optional[Node]:
    """
    Move a node to a new parent.
    """
    node = get_node_by_id(db, node_id)
    if not node:
        return None

    # Validate new parent if provided
    if new_parent_id:
        parent = get_node_by_id(db, new_parent_id)
        if not parent:
            raise ValueError(f"Parent node with ID {new_parent_id} not found")

        # Check parent-child relationship logic
        if parent.type.value >= node.type.value:
            raise ValueError(
                f"A {node.type.name} cannot be a child of a {parent.type.name}"
            )

    node.parent_id = new_parent_id
    node.updated_at = datetime.now(timezone.utc)

    db.add(node)
    db.commit()
    db.refresh(node)
    return node


def get_node_path(db: Session, node_id: UUID) -> List[Node]:
    """
    Get the full path from root to the specified node.
    Returns a list of nodes, starting with the root and ending with the specified node.
    """
    path = []
    current_node = get_node_by_id(db, node_id)

    while current_node:
        path.insert(0, current_node)
        if current_node.parent_id:
            current_node = get_node_by_id(db, current_node.parent_id)
        else:
            break

    return path
