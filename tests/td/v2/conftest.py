import pytest
from sqlmodel import SQLModel, create_engine, Session
from uuid import uuid4
from datetime import datetime

from src.td.v2.models.nodes import Node, NodeType, NodeStatus, TimeEntry


# Create an in-memory SQLite database for testing
@pytest.fixture
def test_engine():
    """Create a SQLite in-memory database engine for testing."""
    return create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture
def test_session(test_engine):
    """Create database tables and return a new session for testing."""
    SQLModel.metadata.create_all(test_engine)

    with Session(test_engine) as session:
        yield session


@pytest.fixture
def sample_sector(test_session):
    """Create a sample sector for testing."""
    sector = Node(title="Test Sector", type=NodeType.sector)
    test_session.add(sector)
    test_session.commit()
    test_session.refresh(sector)
    return sector


@pytest.fixture
def sample_area(test_session, sample_sector):
    """Create a sample area for testing."""
    area = Node(title="Test Area", type=NodeType.area, parent_id=sample_sector.id)
    test_session.add(area)
    test_session.commit()
    test_session.refresh(area)
    return area


@pytest.fixture
def sample_project(test_session, sample_area):
    """Create a sample project for testing."""
    project = Node(
        title="Test Project", type=NodeType.project, parent_id=sample_area.id
    )
    test_session.add(project)
    test_session.commit()
    test_session.refresh(project)
    return project


@pytest.fixture
def sample_task(test_session, sample_project):
    """Create a sample task for testing."""
    task = Node(title="Test Task", type=NodeType.task, parent_id=sample_project.id)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task


@pytest.fixture
def sample_time_entry(test_session, sample_task):
    """Create a sample time entry for testing."""
    time_entry = TimeEntry(
        task_id=sample_task.id,
        start=datetime.fromisoformat("2023-01-01T10:00:00+00:00"),
        end=datetime.fromisoformat("2023-01-01T11:00:00+00:00"),
        duration=3600,
    )
    test_session.add(time_entry)
    test_session.commit()
    test_session.refresh(time_entry)
    return time_entry


@pytest.fixture
def sample_sector(test_session):
    """Create a sample sector for testing."""
    sector = Node(title="Test Sector", type=NodeType.sector)
    test_session.add(sector)
    test_session.commit()
    test_session.refresh(sector)
    return sector


@pytest.fixture
def sample_area(test_session, sample_sector):
    """Create a sample area for testing."""
    area = Node(title="Test Area", type=NodeType.area, parent_id=sample_sector.id)
    test_session.add(area)
    test_session.commit()
    test_session.refresh(area)
    return area


@pytest.fixture
def sample_project(test_session, sample_area):
    """Create a sample project for testing."""
    project = Node(
        title="Test Project", type=NodeType.project, parent_id=sample_area.id
    )
    test_session.add(project)
    test_session.commit()
    test_session.refresh(project)
    return project


@pytest.fixture
def sample_task(test_session, sample_project):
    """Create a sample task for testing."""
    task = Node(title="Test Task", type=NodeType.task, parent_id=sample_project.id)
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task


@pytest.fixture
def sample_time_entry(test_session, sample_task):
    """Create a sample time entry for testing."""
    time_entry = TimeEntry(
        task_id=sample_task.id,
        start=datetime.fromisoformat("2023-01-01T10:00:00+00:00"),
        end=datetime.fromisoformat("2023-01-01T11:00:00+00:00"),
        duration=3600,
    )
    test_session.add(time_entry)
    test_session.commit()
    test_session.refresh(time_entry)
    return time_entry
