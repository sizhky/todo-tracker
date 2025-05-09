import pytest
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator

# Adjust the import paths based on your project structure
from td.models import (
    Task,
    TaskCreate,
    TaskStatus,
    Project,
    Area,
)  # Import all models used by metadata
from td.crud.task import create_task_in_db, get_all_tasks_from_db
# from td.core.settings import DATABASE_URL # We won't use the main DATABASE_URL for tests


# Fixture to create a new in-memory SQLite database and session for each test function
@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    # Use an in-memory SQLite database for testing
    # connect_args={"check_same_thread": False} is needed for SQLite in-memory when used in this way
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Create tables in the in-memory database
    # This ensures all models (Task, Project, Area) are known to SQLModel.metadata
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Optional: If you want to explicitly drop tables after each test, though for in-memory,
    # the database is discarded anyway when the connection closes or the engine is disposed.
    # SQLModel.metadata.drop_all(engine)


# Tests for create_task_db
def test_create_task_db(session: Session):
    """
    Test creating a task in the database.
    """
    task = TaskCreate(
        title="Test Task 1", description="Test Description 1", status=TaskStatus.PENDING
    )

    created_task = create_task_in_db(db=session, task=task)

    assert created_task is not None
    assert (
        created_task.id is not None
    )  # Check if an ID was assigned (meaning it was saved)
    assert created_task.title == task.title
    assert created_task.description == task.description
    assert created_task.status == task.status
    assert created_task.created_at is not None
    assert created_task.updated_at is not None

    # Optionally, verify by fetching the task from the DB directly
    fetched_task = session.get(Task, created_task.id)
    assert fetched_task is not None
    assert fetched_task.title == "Test Task 1"


# Tests for get_all_tasks_db
def test_get_all_tasks_db_empty(session: Session):
    """
    Test listing all tasks when the database is empty.
    """
    tasks = get_all_tasks_from_db(db=session)
    assert isinstance(tasks, list)
    assert len(tasks) == 0


def test_get_all_tasks_db_with_one_task(session: Session):
    """
    Test listing all tasks when there is one task in the database.
    """
    task = TaskCreate(title="Only Task", description="This is the only task.")
    created_task = create_task_in_db(db=session, task=task)

    tasks = get_all_tasks_from_db(db=session)

    assert len(tasks) == 1
    retrieved_task = tasks[0]
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == "Only Task"


def test_get_all_tasks_db_with_multiple_tasks(session: Session):
    """
    Test listing all tasks when there are multiple tasks in the database.
    """
    task1 = TaskCreate(title="Task Alpha")
    task2 = TaskCreate(title="Task Beta", description="Second task")

    create_task_in_db(db=session, task=task1)
    create_task_in_db(db=session, task=task2)

    tasks = get_all_tasks_from_db(db=session)

    assert len(tasks) == 2

    # Check if titles are present (order might not be guaranteed by default)
    titles_in_db = {task.title for task in tasks}
    assert "Task Alpha" in titles_in_db
    assert "Task Beta" in titles_in_db


def test_create_task_with_project(session: Session):
    """
    Test creating a task associated with a project.
    """
    # 1. Create a Project (and an Area if Project requires it)
    area_obj = Area(name="Work", description="Work related stuff")
    session.add(area_obj)
    session.commit()
    session.refresh(area_obj)

    project_obj = Project(
        name="Big Project", description="A very important project", area_id=area_obj.id
    )
    session.add(project_obj)
    session.commit()
    session.refresh(project_obj)

    # 2. Create the task with project_id
    task_in = TaskCreate(
        title="Task for Big Project",
        description="A sub-task",
        project_id=project_obj.id,
    )
    created_task = create_task_in_db(db=session, task=task_in)

    assert created_task is not None
    assert created_task.project_id == project_obj.id

    # Verify by fetching and checking the relationship (optional, if relationship is eager loaded or by separate query)
    fetched_task = session.get(Task, created_task.id)
    assert fetched_task is not None
    assert fetched_task.project_id == project_obj.id
    # If you want to test the actual project object:
    # assert fetched_task.project is not None # This depends on relationship loading strategy
    # assert fetched_task.project.name == "Big Project"
