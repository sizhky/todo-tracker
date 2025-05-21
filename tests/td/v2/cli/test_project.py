import pytest
from unittest.mock import patch, MagicMock

from src.td.v2.cli.project import project_crud
from src.td.v2.models.nodes import NodeType, ProjectCreate


@patch("src.td.v2.cli.project.sector_crud")
@patch("src.td.v2.cli.project.area_crud")
@patch("src.td.v2.cli.project.project_crud")
def test_create_project_hierarchy(mock_project_crud, mock_area_crud, mock_sector_crud):
    """Test that creating a project correctly sets up the hierarchy."""
    from src.td.v2.cli.project import add_project

    # Setup the mocks
    mock_sector_crud.get_or_create.return_value.id = "sector-id"
    mock_area_crud.get_or_create.return_value.id = "area-id"
    mock_project_crud.create.return_value.id = "project-id"
    mock_project_crud.create.return_value.title = "Test Project"

    # Call the function
    result = add_project(
        title="Test Project", sector_name="Test Sector", area_name="Test Area"
    )

    # Verify the calls were made correctly
    mock_sector_crud.get_or_create.assert_called_once()
    mock_area_crud.get_or_create.assert_called_once()
    mock_project_crud.create.assert_called_once()

    # Verify the parent_id is passed correctly
    area_call = mock_area_crud.get_or_create.call_args[0][0]
    assert area_call.parent_id == "sector-id"

    project_call = mock_project_crud.create.call_args[0][0]
    assert project_call.parent_id == "area-id"


@patch("src.td.v2.cli.project.project_crud")
def test_list_projects(mock_project_crud, mock_area_crud):
    """Test the list_projects command."""
    from src.td.v2.cli.project import list_projects

    # Setup the mocks
    project1 = MagicMock()
    project1.id = "project1-id"
    project1.title = "Project 1"
    project1.status = 0  # active

    project2 = MagicMock()
    project2.id = "project2-id"
    project2.title = "Project 2"
    project2.status = 0  # active

    mock_project_crud.list.return_value = [project1, project2]

    # Call with no filters
    result = list_projects()

    # Verify project_crud.list was called correctly
    mock_project_crud.list.assert_called_once()

    # Call with area filter
    mock_project_crud.list.reset_mock()
    result = list_projects(area_id="area-id")

    # Verify project_crud.list was called with the area filter
    mock_project_crud.list.assert_called_once()
    assert mock_project_crud.list.call_args[1].get("parent_id") == "area-id"


@patch("src.td.v2.cli.project.project_crud")
def test_update_project(mock_project_crud):
    """Test the update_project command."""
    from src.td.v2.cli.project import update_project

    # Setup the mocks
    mock_project_crud.update.return_value.id = "project-id"
    mock_project_crud.update.return_value.title = "Updated Project"

    # Call the function
    result = update_project(id="project-id", title="Updated Project")

    # Verify project_crud.update was called correctly
    mock_project_crud.update.assert_called_once()
    update_call = mock_project_crud.update.call_args
    assert update_call[0][0] == "project-id"
    assert update_call[0][1].title == "Updated Project"


@patch("src.td.v2.cli.project.project_crud")
def test_delete_project(mock_project_crud):
    """Test the delete_project command."""
    from src.td.v2.cli.project import delete_project

    # Setup the mocks
    mock_project_crud.delete.return_value = True

    # Call the function
    result = delete_project(id="project-id")

    # Verify project_crud.delete was called correctly
    mock_project_crud.delete.assert_called_once_with("project-id")
