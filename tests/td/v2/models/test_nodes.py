import pytest
from uuid import UUID
import json

from src.td.v2.models.nodes import Node, NodeType, NodeStatus


def test_node_creation(test_session):
    """Test that a Node can be created correctly."""
    # Create a node
    node = Node(title="Test Node", type=NodeType.sector)
    test_session.add(node)
    test_session.commit()
    test_session.refresh(node)

    # Verify the node was created properly
    assert node.id is not None
    assert isinstance(node.id, UUID)
    assert node.title == "Test Node"
    assert node.type == NodeType.sector
    assert node.status == NodeStatus.active
    assert node.parent_id is None
    assert node.meta == "{}"

    # Retrieve the node from DB to ensure it was saved
    retrieved_node = test_session.get(Node, node.id)
    assert retrieved_node is not None
    assert retrieved_node.title == "Test Node"


def test_node_hierarchy(test_session, sample_sector, sample_area, sample_project):
    """Test that nodes can form a proper hierarchy."""
    # Verify the hierarchy is correct
    assert sample_area.parent_id == sample_sector.id
    assert sample_project.parent_id == sample_area.id

    # Query to verify parent-child relationships
    # Query to find all children of the sector
    sector_children = (
        test_session.query(Node).filter(Node.parent_id == sample_sector.id).all()
    )
    assert len(sector_children) == 1
    assert sector_children[0].id == sample_area.id

    # Query to find all children of the area
    area_children = (
        test_session.query(Node).filter(Node.parent_id == sample_area.id).all()
    )
    assert len(area_children) == 1
    assert area_children[0].id == sample_project.id


def test_node_status_update(test_session, sample_task):
    """Test that a node's status can be updated."""
    # Update the task status to completed
    sample_task.status = NodeStatus.completed
    test_session.commit()
    test_session.refresh(sample_task)

    # Verify the status was updated
    assert sample_task.status == NodeStatus.completed

    # Update the task status to archived
    sample_task.status = NodeStatus.archived
    test_session.commit()
    test_session.refresh(sample_task)

    # Verify the status was updated
    assert sample_task.status == NodeStatus.archived


def test_node_meta_field(test_session):
    """Test that the meta field can store and retrieve JSON data."""
    # Create test metadata
    meta_data = {"key1": "value1", "key2": 42, "nested": {"inner": "value"}}

    # Create a node with meta data
    node = Node(title="Meta Test", type=NodeType.task, meta=json.dumps(meta_data))
    test_session.add(node)
    test_session.commit()
    test_session.refresh(node)

    # Verify the meta field contains the correct JSON data
    loaded_meta = json.loads(node.meta)
    assert loaded_meta == meta_data
    assert loaded_meta["key1"] == "value1"
    assert loaded_meta["key2"] == 42
    assert loaded_meta["nested"]["inner"] == "value"
