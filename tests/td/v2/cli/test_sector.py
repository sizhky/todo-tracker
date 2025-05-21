import pytest
from unittest.mock import patch, MagicMock

from src.td.v2.cli.sector import sector_crud
from src.td.v2.models.nodes import NodeType, SectorCreate


@patch("src.td.v2.cli.sector.sector_crud")
def test_add_sector(mock_sector_crud):
    """Test the add_sector command."""
    from src.td.v2.cli.sector import add_sector

    # Setup the mocks
    mock_sector_crud.create.return_value.id = "sector-id"
    mock_sector_crud.create.return_value.title = "Test Sector"

    # Call the function
    result = add_sector(title="Test Sector")

    # Verify sector_crud.create was called correctly
    mock_sector_crud.create.assert_called_once()
    sector_call = mock_sector_crud.create.call_args[0][0]
    assert sector_call.title == "Test Sector"


@patch("src.td.v2.cli.sector.sector_crud")
def test_list_sectors(mock_sector_crud):
    """Test the list_sectors command."""
    from src.td.v2.cli.sector import list_sectors

    # Setup the mocks
    sector1 = MagicMock()
    sector1.id = "sector1-id"
    sector1.title = "Sector 1"
    sector1.status = 0  # active

    sector2 = MagicMock()
    sector2.id = "sector2-id"
    sector2.title = "Sector 2"
    sector2.status = 0  # active

    mock_sector_crud.list.return_value = [sector1, sector2]

    # Call the function
    result = list_sectors()

    # Verify sector_crud.list was called correctly
    mock_sector_crud.list.assert_called_once()


@patch("src.td.v2.cli.sector.sector_crud")
def test_update_sector(mock_sector_crud):
    """Test the update_sector command."""
    from src.td.v2.cli.sector import update_sector

    # Setup the mocks
    mock_sector_crud.update.return_value.id = "sector-id"
    mock_sector_crud.update.return_value.title = "Updated Sector"

    # Call the function
    result = update_sector(id="sector-id", title="Updated Sector")

    # Verify sector_crud.update was called correctly
    mock_sector_crud.update.assert_called_once()
    update_call = mock_sector_crud.update.call_args
    assert update_call[0][0] == "sector-id"
    assert update_call[0][1].title == "Updated Sector"


@patch("src.td.v2.cli.sector.sector_crud")
def test_delete_sector(mock_sector_crud):
    """Test the delete_sector command."""
    from src.td.v2.cli.sector import delete_sector

    # Setup the mocks
    mock_sector_crud.delete.return_value = True

    # Call the function
    result = delete_sector(id="sector-id")

    # Verify sector_crud.delete was called correctly
    mock_sector_crud.delete.assert_called_once_with("sector-id")
