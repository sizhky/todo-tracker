import pytest
from unittest.mock import patch, MagicMock

from src.td.v2.cli.section import section_crud
from src.td.v2.models.nodes import NodeType, SectionCreate


@patch("src.td.v2.cli.section.sector_crud")
@patch("src.td.v2.cli.section.area_crud")
@patch("src.td.v2.cli.section.project_crud")
@patch("src.td.v2.cli.section.section_crud")
def test_create_section_hierarchy(
    mock_section_crud, mock_project_crud, mock_area_crud, mock_sector_crud
):
    """Test that creating a section correctly sets up the hierarchy."""
    from src.td.v2.cli.section import add_section

    # Setup the mocks
    mock_sector_crud.get_or_create.return_value.id = "sector-id"
    mock_area_crud.get_or_create.return_value.id = "area-id"
    mock_project_crud.get_or_create.return_value.id = "project-id"
    mock_section_crud.create.return_value.id = "section-id"
    mock_section_crud.create.return_value.title = "Test Section"

    # Call the function
    result = add_section(
        title="Test Section",
        sector_name="Test Sector",
        area_name="Test Area",
        project_name="Test Project",
    )

    # Verify the calls were made correctly
    mock_sector_crud.get_or_create.assert_called_once()
    mock_area_crud.get_or_create.assert_called_once()
    mock_project_crud.get_or_create.assert_called_once()
    mock_section_crud.create.assert_called_once()

    # Verify the parent_id is passed correctly
    area_call = mock_area_crud.get_or_create.call_args[0][0]
    assert area_call.parent_id == "sector-id"

    project_call = mock_project_crud.get_or_create.call_args[0][0]
    assert project_call.parent_id == "area-id"

    section_call = mock_section_crud.create.call_args[0][0]
    assert section_call.parent_id == "project-id"


@patch("src.td.v2.cli.section.section_crud")
def test_list_sections(mock_section_crud, mock_project_crud):
    """Test the list_sections command."""
    from src.td.v2.cli.section import list_sections

    # Setup the mocks
    section1 = MagicMock()
    section1.id = "section1-id"
    section1.title = "Section 1"
    section1.status = 0  # active

    section2 = MagicMock()
    section2.id = "section2-id"
    section2.title = "Section 2"
    section2.status = 0  # active

    mock_section_crud.list.return_value = [section1, section2]

    # Call with no filters
    result = list_sections()

    # Verify section_crud.list was called correctly
    mock_section_crud.list.assert_called_once()

    # Call with project filter
    mock_section_crud.list.reset_mock()
    result = list_sections(project_id="project-id")

    # Verify section_crud.list was called with the project filter
    mock_section_crud.list.assert_called_once()
    assert mock_section_crud.list.call_args[1].get("parent_id") == "project-id"


@patch("src.td.v2.cli.section.section_crud")
def test_update_section(mock_section_crud):
    """Test the update_section command."""
    from src.td.v2.cli.section import update_section

    # Setup the mocks
    mock_section_crud.update.return_value.id = "section-id"
    mock_section_crud.update.return_value.title = "Updated Section"

    # Call the function
    result = update_section(id="section-id", title="Updated Section")

    # Verify section_crud.update was called correctly
    mock_section_crud.update.assert_called_once()
    update_call = mock_section_crud.update.call_args
    assert update_call[0][0] == "section-id"
    assert update_call[0][1].title == "Updated Section"


@patch("src.td.v2.cli.section.section_crud")
def test_delete_section(mock_section_crud):
    """Test the delete_section command."""
    from src.td.v2.cli.section import delete_section

    # Setup the mocks
    mock_section_crud.delete.return_value = True

    # Call the function
    result = delete_section(id="section-id")

    # Verify section_crud.delete was called correctly
    mock_section_crud.delete.assert_called_once_with("section-id")
