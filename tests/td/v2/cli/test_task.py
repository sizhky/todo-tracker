import pytest
from unittest.mock import patch, MagicMock
import uuid

from src.td.v2.cli.task import task_crud, create_heirarchy
from src.td.v2.models.nodes import NodeType, NodeStatus


@patch("src.td.v2.cli.task.sector_crud")
@patch("src.td.v2.cli.task.area_crud")
@patch("src.td.v2.cli.task.project_crud")
@patch("src.td.v2.cli.task.section_crud")
def test_create_hierarchy(
    mock_section_crud, mock_project_crud, mock_area_crud, mock_sector_crud
):
    """Test that create_hierarchy correctly creates the hierarchy."""
    # Setup the mocks with actual UUIDs
    sector_id = uuid.uuid4()
    area_id = uuid.uuid4()
    project_id = uuid.uuid4()
    section_id = uuid.uuid4()

    mock_sector = MagicMock()
    mock_sector.id = sector_id
    mock_sector_crud.get_or_create.return_value = mock_sector

    mock_area = MagicMock()
    mock_area.id = area_id
    mock_area_crud.get_or_create.return_value = mock_area

    mock_project = MagicMock()
    mock_project.id = project_id
    mock_project_crud.get_or_create.return_value = mock_project

    mock_section = MagicMock()
    mock_section.id = section_id
    mock_section_crud.get_or_create.return_value = mock_section

    # Create a task with hierarchy
    class MockTask:
        title = "Test Task"
        sector_name = "Test Sector"
        area_name = "Test Area"
        project_name = "Test Project"
        section_name = "Test Section"

    # Call the function
    result = create_heirarchy(MockTask())

    # Verify the calls were made correctly
    mock_sector_crud.get_or_create.assert_called_once()
    mock_area_crud.get_or_create.assert_called_once()
    mock_project_crud.get_or_create.assert_called_once()
    mock_section_crud.get_or_create.assert_called_once()


@patch("src.td.v2.cli.task.task_crud._read_all")
def test_list_tasks_internal(mock_read_all):
    """Test the _list_tasks internal function."""
    from src.td.v2.cli.task import _list_tasks

    # Setup the mocks
    task1 = MagicMock()
    task1.title = "Task 1"

    task2 = MagicMock()
    task2.title = "Task 2"

    mock_read_all.return_value = [task1, task2]

    # Call the function
    result = _list_tasks()

    # Verify task_crud._read_all was called correctly
    mock_read_all.assert_called_once()

    # Verify the result contains the expected task titles
    assert "Task 1" in result
    assert "Task 2" in result


@patch("src.td.v2.cli.task.task_crud.Create")
@patch("src.td.v2.cli.task.create_heirarchy")
def test_task_crud_create(mock_create_hierarchy, mock_create):
    """Test the task_crud.Create method that's registered to the CLI."""
    # Setup the mocks
    section_id = uuid.uuid4()
    mock_section = MagicMock()
    mock_section.id = section_id
    mock_create_hierarchy.return_value = mock_section

    task_id = uuid.uuid4()
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.title = "Test Task"
    mock_create.return_value = mock_task

    # Create a data object similar to what the CLI would provide
    data = MagicMock()
    data.title = "Test Task"
    data.sector_name = "Test Sector"
    data.area_name = "Test Area"
    data.project_name = "Test Project"
    data.section_name = "Test Section"

    # Call the registered CLI command handler
    handler = task_crud.Create
    result = handler(data)

    # Verify create_hierarchy was called and the task was created
    mock_create_hierarchy.assert_called_once()


@patch("src.td.v2.cli.task.task_crud.ReadAll")
def test_task_crud_read_all(mock_read_all):
    """Test the task_crud.ReadAll method that's registered to the CLI."""
    # Setup the mocks
    task1 = MagicMock()
    task1.id = uuid.uuid4()
    task1.title = "Task 1"
    task1.status = NodeStatus.active

    task2 = MagicMock()
    task2.id = uuid.uuid4()
    task2.title = "Task 2"
    task2.status = NodeStatus.completed

    mock_read_all.return_value = [task1, task2]

    # Create a data object similar to what the CLI would provide
    data = MagicMock()

    # Call the registered CLI command handler
    handler = task_crud.ReadAll
    result = handler(data)

    # Verify read_all was called correctly
    mock_read_all.assert_called_once()


@patch("src.td.v2.cli.task.task_crud.Update")
def test_task_crud_update(mock_update):
    """Test the task_crud.Update method that's registered to the CLI."""
    # Setup the mocks
    task_id = uuid.uuid4()
    mock_task = MagicMock()
    mock_task.id = task_id
    mock_task.title = "Updated Task"
    mock_update.return_value = mock_task

    # Create a data object similar to what the CLI would provide
    data = MagicMock()
    data.id = task_id
    data.title = "Updated Task"

    # Call the registered CLI command handler
    handler = task_crud.Update
    result = handler(data)

    # Verify update was called correctly
    mock_update.assert_called_once_with(data)


@patch("src.td.v2.cli.task.task_crud._read_all")
def test_list_tasks_internal(mock_read_all):
    """Test the _list_tasks internal function."""
    from src.td.v2.cli.task import _list_tasks

    # Setup the mocks
    task1 = MagicMock()
    task1.id = "task1-id"
    task1.title = "Task 1"

    task2 = MagicMock()
    task2.id = "task2-id"
    task2.title = "Task 2"

    mock_read_all.return_value = [task1, task2]

    # Call the function
    result = _list_tasks()

    # Verify task_crud._read_all was called correctly
    mock_read_all.assert_called_once()

    # Verify the result contains the expected task titles
    assert "Task 1" in result
    assert "Task 2" in result


@patch("src.td.v2.cli.task.create_heirarchy")
@patch("src.td.v2.cli.task.task_crud")
def test_add_task_command(mock_task_crud, mock_create_hierarchy):
    """Test the add_task command."""
    from src.td.v2.cli.task import add_task

    # Setup the mocks
    mock_create_hierarchy.return_value = {
        "section_id": "section-id",
        "project_id": "project-id",
        "area_id": "area-id",
        "sector_id": "sector-id",
    }

    mock_task_crud.create.return_value.id = "task-id"
    mock_task_crud.create.return_value.title = "Test Task"

    # Call the function
    result = add_task(
        title="Test Task",
        sector_name="Test Sector",
        area_name="Test Area",
        project_name="Test Project",
        section_name="Test Section",
    )

    # Verify create_hierarchy was called
    mock_create_hierarchy.assert_called_once()

    # Verify task_crud.create was called with the correct parent_id
    mock_task_crud.create.assert_called_once()
    create_call = mock_task_crud.create.call_args[0][0]
    assert create_call.title == "Test Task"


@patch("src.td.v2.cli.task.task_crud")
def test_list_tasks(mock_task_crud, mock_project_crud):
    """Test the list_tasks command."""
    from src.td.v2.cli.task import list_tasks

    # Setup the mocks
    task1 = MagicMock()
    task1.id = "task1-id"
    task1.title = "Task 1"
    task1.status = 0  # active

    task2 = MagicMock()
    task2.id = "task2-id"
    task2.title = "Task 2"
    task2.status = 10  # completed

    mock_task_crud.list.return_value = [task1, task2]

    # Call with no filters
    result = list_tasks()

    # Verify task_crud.list was called correctly
    mock_task_crud.list.assert_called_once()

    # Call with project filter
    mock_task_crud.list.reset_mock()
    result = list_tasks(project_id="project-id")

    # Verify task_crud.list was called with the project filter
    mock_task_crud.list.assert_called_once()
    assert mock_task_crud.list.call_args[1].get("parent_id") == "project-id"


@patch("src.td.v2.cli.task.task_crud")
def test_update_task(mock_task_crud):
    """Test the update_task command."""
    from src.td.v2.cli.task import update_task

    # Setup the mocks
    mock_task_crud.update.return_value.id = "task-id"
    mock_task_crud.update.return_value.title = "Updated Task"

    # Call the function
    result = update_task(id="task-id", title="Updated Task")

    # Verify task_crud.update was called correctly
    mock_task_crud.update.assert_called_once()
    update_call = mock_task_crud.update.call_args
    assert update_call[0][0] == "task-id"
    assert update_call[0][1].title == "Updated Task"


@patch("src.td.v2.cli.task.task_crud")
def test_delete_task(mock_task_crud):
    """Test the delete_task command."""
    from src.td.v2.cli.task import delete_task

    # Setup the mocks
    mock_task_crud.delete.return_value = True

    # Call the function
    result = delete_task(id="task-id")

    # Verify task_crud.delete was called correctly
    mock_task_crud.delete.assert_called_once_with("task-id")


@patch("src.td.v2.cli.task.task_crud")
def test_complete_task(mock_task_crud):
    """Test the complete_task command."""
    from src.td.v2.cli.task import complete_task
    from src.td.v2.models.nodes import NodeStatus

    # Setup the mocks
    mock_task_crud.update.return_value.id = "task-id"
    mock_task_crud.update.return_value.status = NodeStatus.completed

    # Call the function
    result = complete_task(id="task-id")

    # Verify task_crud.update was called with the correct status
    mock_task_crud.update.assert_called_once()
    update_call = mock_task_crud.update.call_args
    assert update_call[0][0] == "task-id"
    assert update_call[0][1].status == NodeStatus.completed
