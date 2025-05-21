import pytest
from uuid import uuid4
from sqlmodel import select

from src.td.v2.crud.node import NodeCrud
from src.td.v2.models.nodes import (
    Node,
    NodeType,
    NodeStatus,
    AreaCreate,
    NodeRead,
    TaskCreate,
    ProjectCreate,
)


class TestNodeCrud:
    """Test suite for NodeCrud class."""

    def test_create_node(self, test_session):
        """Test creating a node."""
        # Initialize NodeCrud with area type
        node_crud = NodeCrud(node_type=NodeType.area, db=test_session)

        # Create a new area node using the proper schema class
        node_data = AreaCreate(title="Test Area")
        node = node_crud.create(node_data)

        # Verify the node was created properly
        assert node.id is not None
        assert node.title == "Test Area"
        assert node.type == NodeType.area
        assert node.status == NodeStatus.active

        # Check in database
        db_node = test_session.exec(select(Node).where(Node.id == node.id)).first()
        assert db_node is not None
        assert db_node.title == "Test Area"

    def test_read_node(self, test_session, sample_area):
        """Test reading a node."""
        # Initialize NodeCrud with area type
        node_crud = NodeCrud(node_type=NodeType.area, db=test_session)

        # Read the area
        node_read = NodeRead(id=sample_area.id)
        node = node_crud.read(node_read)

        # Verify the node
        assert node is not None
        assert node.id == sample_area.id
        assert node.title == sample_area.title
        assert node.type == NodeType.area

    def test_read_nonexistent_node(self, test_session):
        """Test reading a node that doesn't exist."""
        # Initialize NodeCrud
        node_crud = NodeCrud(node_type=NodeType.area, db=test_session)

        # Attempt to read a non-existent node
        non_existent_id = uuid4()
        node_read = NodeRead(id=non_existent_id)
        node = node_crud.read(node_read)

        # Verify no node was returned
        assert node is None

    def test_update_node(self, test_session, sample_project):
        """Test updating a node."""
        # Initialize NodeCrud with project type
        node_crud = NodeCrud(node_type=NodeType.project, db=test_session)

        # Update the project
        update_data = ProjectCreate(id=sample_project.id, title="Updated Project Title")
        updated_node = node_crud.update(update_data)

        # Verify the update
        assert updated_node is not None
        assert updated_node.id == sample_project.id
        assert updated_node.title == "Updated Project Title"

        # Check in database
        db_node = test_session.exec(
            select(Node).where(Node.id == sample_project.id)
        ).first()
        assert db_node.title == "Updated Project Title"

    def test_delete_node(self, test_session, sample_task):
        """Test deleting a node."""
        # Initialize NodeCrud with task type
        node_crud = NodeCrud(node_type=NodeType.task, db=test_session)

        # Delete the task
        delete_data = NodeRead(id=sample_task.id)
        node_crud.delete(delete_data)

        # Verify the node was deleted
        db_node = test_session.exec(
            select(Node).where(Node.id == sample_task.id)
        ).first()
        assert db_node is None

    def test_list_nodes(self, test_session, sample_sector, sample_area):
        """Test listing nodes of a specific type."""
        # Create another area
        new_area = Node(
            title="Another Area", type=NodeType.area, parent_id=sample_sector.id
        )
        test_session.add(new_area)
        test_session.commit()

        # Initialize NodeCrud with area type
        node_crud = NodeCrud(node_type=NodeType.area, db=test_session)

        # List all areas
        areas = node_crud.read_all()

        # Verify we got all areas
        assert len(areas) == 2
        area_titles = {area.title for area in areas}
        assert "Test Area" in area_titles
        assert "Another Area" in area_titles

    def test_list_children(self, test_session, sample_area, sample_project):
        """Test listing child nodes of a parent."""
        # Create another project under the same area
        new_project = Node(
            title="Another Project", type=NodeType.project, parent_id=sample_area.id
        )
        test_session.add(new_project)
        test_session.commit()

        # Initialize NodeCrud with project type
        node_crud = NodeCrud(node_type=NodeType.project, db=test_session)

        # List all projects under the area
        node_read = NodeRead(id=sample_area.id)
        projects = node_crud.get_children(node_read)

        # Verify we got all projects under the area
        assert len(projects) == 2
        project_titles = {project.title for project in projects}
        assert "Test Project" in project_titles
        assert "Another Project" in project_titles

    def test_list_nodes(self, test_session, sample_sector, sample_area):
        """Test listing nodes of a specific type."""
        # Create another area
        new_area = Node(
            title="Another Area", type=NodeType.area, parent_id=sample_sector.id
        )
        test_session.add(new_area)
        test_session.commit()

        # Initialize NodeCrud with area type
        node_crud = NodeCrud(node_type=NodeType.area, db=test_session)

        # List all areas
        areas = node_crud.list()

        # Verify we got all areas
        assert len(areas) == 2
        area_titles = {area.title for area in areas}
        assert "Test Area" in area_titles
        assert "Another Area" in area_titles

    def test_list_children(self, test_session, sample_area, sample_project):
        """Test listing child nodes of a parent."""
        # Create another project under the same area
        new_project = Node(
            title="Another Project", type=NodeType.project, parent_id=sample_area.id
        )
        test_session.add(new_project)
        test_session.commit()

        # Initialize NodeCrud with project type
        node_crud = NodeCrud(node_type=NodeType.project, db=test_session)

        # List all projects under the area
        projects = node_crud.list(parent_id=sample_area.id)

        # Verify we got all projects under the area
        assert len(projects) == 2
        project_titles = {project.title for project in projects}
        assert "Test Project" in project_titles
        assert "Another Project" in project_titles
