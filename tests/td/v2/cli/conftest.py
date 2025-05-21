# This file contains fixtures specific to CLI testing
import pytest
from unittest.mock import MagicMock, patch

from src.td.v2.models.nodes import Node, NodeType, NodeStatus


@pytest.fixture
def mock_task_crud():
    """Create a mock for the task CRUD operations."""
    mock = MagicMock()

    # Mock the create method
    mock.create.return_value = Node(
        id="task-uuid", title="Test Task", type=NodeType.task, status=NodeStatus.active
    )

    # Mock the update method
    mock.update.return_value = Node(
        id="task-uuid",
        title="Updated Task",
        type=NodeType.task,
        status=NodeStatus.active,
    )

    # Mock the delete method
    mock.delete.return_value = True

    # Mock the list method
    mock.list.return_value = [
        Node(
            id="task1-uuid",
            title="Task 1",
            type=NodeType.task,
            status=NodeStatus.active,
        ),
        Node(
            id="task2-uuid",
            title="Task 2",
            type=NodeType.task,
            status=NodeStatus.completed,
        ),
    ]

    return mock


@pytest.fixture
def mock_project_crud():
    """Create a mock for the project CRUD operations."""
    mock = MagicMock()

    # Mock the create method
    mock.create.return_value = Node(
        id="project-uuid",
        title="Test Project",
        type=NodeType.project,
        status=NodeStatus.active,
    )

    # Mock the get_or_create method
    mock.get_or_create.return_value = Node(
        id="project-uuid",
        title="Test Project",
        type=NodeType.project,
        status=NodeStatus.active,
    )

    # Mock the list method
    mock.list.return_value = [
        Node(
            id="project1-uuid",
            title="Project 1",
            type=NodeType.project,
            status=NodeStatus.active,
        ),
        Node(
            id="project2-uuid",
            title="Project 2",
            type=NodeType.project,
            status=NodeStatus.active,
        ),
    ]

    return mock


@pytest.fixture
def mock_area_crud():
    """Create a mock for the area CRUD operations."""
    mock = MagicMock()

    # Mock the get_or_create method
    mock.get_or_create.return_value = Node(
        id="area-uuid", title="Test Area", type=NodeType.area, status=NodeStatus.active
    )

    # Mock the list method
    mock.list.return_value = [
        Node(
            id="area1-uuid",
            title="Area 1",
            type=NodeType.area,
            status=NodeStatus.active,
        ),
        Node(
            id="area2-uuid",
            title="Area 2",
            type=NodeType.area,
            status=NodeStatus.active,
        ),
    ]

    return mock


@pytest.fixture
def mock_sector_crud():
    """Create a mock for the sector CRUD operations."""
    mock = MagicMock()

    # Mock the get_or_create method
    mock.get_or_create.return_value = Node(
        id="sector-uuid",
        title="Test Sector",
        type=NodeType.sector,
        status=NodeStatus.active,
    )

    # Mock the list method
    mock.list.return_value = [
        Node(
            id="sector1-uuid",
            title="Sector 1",
            type=NodeType.sector,
            status=NodeStatus.active,
        ),
        Node(
            id="sector2-uuid",
            title="Sector 2",
            type=NodeType.sector,
            status=NodeStatus.active,
        ),
    ]

    return mock


@pytest.fixture
def mock_section_crud():
    """Create a mock for the section CRUD operations."""
    mock = MagicMock()

    # Mock the get_or_create method
    mock.get_or_create.return_value = Node(
        id="section-uuid",
        title="Test Section",
        type=NodeType.section,
        status=NodeStatus.active,
    )

    # Mock the list method
    mock.list.return_value = [
        Node(
            id="section1-uuid",
            title="Section 1",
            type=NodeType.section,
            status=NodeStatus.active,
        ),
        Node(
            id="section2-uuid",
            title="Section 2",
            type=NodeType.section,
            status=NodeStatus.active,
        ),
    ]

    return mock
