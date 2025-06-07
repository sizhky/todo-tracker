import os
from datetime import datetime, timedelta, timezone

from sqlmodel import select

from td.v3.crud import NodeCrud
from td.v3.models import NodeCreate, NodeUpdate, NodeRead, NodeStatus, Node


def test_update_node_keeps_children(session):
    crud = NodeCrud(db=session)
    crud._create_node(NodeCreate(title="s"))
    crud._create_node(NodeCreate(title="a", path="s"))
    crud._create_node(NodeCreate(title="p", path="s/a"))

    crud._update_node(NodeUpdate(title="a", path="s", new_title="a1"))

    child = session.exec(select(Node).where(Node.title == "p")).first()
    assert child is not None
    assert child.path == "s/a1"


def test_hide_old_completed_tasks(session):
    crud = NodeCrud(db=session)
    crud._create_node(NodeCreate(title="s"))
    crud._create_node(NodeCreate(title="t1", path="s"))
    crud._create_node(NodeCreate(title="t2", path="s"))

    n1 = crud.get_node(NodeRead(title="t1", path="s"))
    n1.status = NodeStatus.completed
    n1.updated_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    session.add(n1)
    session.commit()

    crud.toggle_complete(NodeRead(title="t2", path="s"))

    tree = crud.tree
    subtree = tree["s"]
    assert "t1" not in subtree
    assert "t2" in subtree
