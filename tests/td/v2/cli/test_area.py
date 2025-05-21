import pytest
from unittest.mock import patch, MagicMock

from src.td.v2.cli.area import area_crud
from src.td.v2.models.nodes import NodeType, AreaCreate


@patch("src.td.v2.cli.area.sector_crud")
@patch("src.td.v2.cli.area.area_crud")
def test_create_area_hierarchy(mock_area_crud, mock_sector_crud):
    """Test that creating an area correctly sets up the hierarchy."""
    from src.td.v2.cli.area import add_area

    # Setup the mocks
    mock_sector_crud.get_or_create.return_value.id = "sector-id"
    mock_area_crud.create.return_value.id = "area-id"
    mock_area_crud.create.return_value.title = "Test Area"

    # Call the function
    result = add_area(title="Test Area", sector_name="Test Sector")

    # Verify the calls were made correctly
    mock_sector_crud.get_or_create.assert_called_once()
    mock_area_crud.create.assert_called_once()

    # Verify the parent_id is passed correctly
    area_call = mock_area_crud.create.call_args[0][0]
    assert area_call.parent_id == "sector-id"


@patch("src.td.v2.cli.area.area_crud")
def test_list_areas(mock_area_crud, mock_sector_crud):
    """Test the list_areas command."""
    from src.td.v2.cli.area import list_areas

    # Setup the mocks
    area1 = MagicMock()
    area1.id = "area1-id"
    area1.title = "Area 1"
    area1.status = 0  # active

    area2 = MagicMock()
    area2.id = "area2-id"
    area2.title = "Area 2"
    area2.status = 0  # active

    mock_area_crud.list.return_value = [area1, area2]

    # Call with no filters
    result = list_areas()

    # Verify area_crud.list was called correctly
    mock_area_crud.list.assert_called_once()

    # Call with sector filter
    mock_area_crud.list.reset_mock()
    result = list_areas(sector_id="sector-id")

    # Verify area_crud.list was called with the sector filter
    mock_area_crud.list.assert_called_once()
    assert mock_area_crud.list.call_args[1].get("parent_id") == "sector-id"


@patch("src.td.v2.cli.area.area_crud")
def test_update_area(mock_area_crud):
    """Test the update_area command."""
    from src.td.v2.cli.area import update_area

    # Setup the mocks
    mock_area_crud.update.return_value.id = "area-id"
    mock_area_crud.update.return_value.title = "Updated Area"

    # Call the function
    result = update_area(id="area-id", title="Updated Area")

    # Verify area_crud.update was called correctly
    mock_area_crud.update.assert_called_once()
    update_call = mock_area_crud.update.call_args
    assert update_call[0][0] == "area-id"
    assert update_call[0][1].title == "Updated Area"


@patch("src.td.v2.cli.area.area_crud")
def test_delete_area(mock_area_crud):
    """Test the delete_area command."""
    from src.td.v2.cli.area import delete_area

    # Setup the mocks
    mock_area_crud.delete.return_value = True

    # Call the function
    result = delete_area(id="area-id")

    # Verify area_crud.delete was called correctly
    mock_area_crud.delete.assert_called_once_with("area-id")
