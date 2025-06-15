from torch_snippets import AD, write_json
from starlette.responses import Response
from starlette import status
from typing_extensions import Annotated
from typer import Argument

from ..crud import create_area_in_db, get_all_areas_from_db, delete_area_from_db
from ..core.db import session_scope

from .__pre_init__ import cli


@cli.command(name="ac")
def create_area(
    name: str,
    description: str = "",
):
    """
    Create a new area in the database.

    Args:
        name: Name of the area. Multiple areas can be created by providing comma-separated names.
        description: Optional description for the area.

    Returns:
        The ID of the created area, a Response object if called from API,
        or a dictionary containing the ID if called from MCP.
    """
    if "," in name:
        names = name.split(",")
        return [create_area(name, description) for name in names]

    with session_scope() as session:
        area = {
            "name": name,
            "description": description,
        }
        created_area = create_area_in_db(session, area)

        response = {"id": created_area.id}
        if hasattr(create_area, "from_api"):
            # return 201 created
            return Response(write_json(response), status_code=status.HTTP_201_CREATED)
        elif hasattr(create_area, "from_mcp"):
            return response
        else:
            print(f"Area `{created_area.name}` created with ID: {created_area.id}")
            return created_area.id


def _list_areas(skip: int = 0, limit: int = 100):
    """
    List all areas in the database with optional pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        An object containing area mappings (area2id, id2area) and area descriptions.
    """
    with session_scope() as session:
        areas = get_all_areas_from_db(session, skip=skip, limit=limit)
        id2area = {area.id: area.name for area in areas}
        area2id = {area.name: area.id for area in areas}
        area_descriptions = [area.model_dump() for area in areas]
        o = AD(area2id, id2area, area_descriptions)
        return o


def __list_areas():
    o = _list_areas()
    return list(o.area2id.keys())


@cli.command(name="al")
def list_areas(skip: int = 0, limit: int = 100):
    """
    List all areas in the database with optional pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of area descriptions if called from API, a dictionary with areas if called from MCP,
        or prints the area information to console.
    """
    x = _list_areas(skip=skip, limit=limit)

    if hasattr(list_areas, "from_api"):
        return x.area_descriptions
    if hasattr(list_areas, "from_mcp"):
        return {"areas": [ad.d for ad in x.area_descriptions]}

    # cli output
    for area in x.area_descriptions:
        print(f"ID: {area.id} - {area.name}: `{area.description}`")
    if not x.area_descriptions:
        print("No areas found.")


@cli.command(name="ad")
def delete_area(
    area: Annotated[
        str, Argument(help="Name of the area to delete.", autocompletion=__list_areas)
    ],
):
    """
    Delete an area from the database by its name.

    Args:
        area: Name of the area to delete. Multiple areas can be deleted by providing comma-separated names.

    Returns:
        None. Prints confirmation message or error to console.
    """
    if "," in area:
        areas = area.split(",")
        return [delete_area(area) for area in areas]

    with session_scope() as session:
        try:
            area_id = _list_areas().area2id.get(area)
            if not area_id:
                raise ValueError(f"Area with name {area} not found.")
            deleted_area_id = delete_area_from_db(session, area_id)
            if hasattr(delete_area, "from_api"):
                return Response(
                    write_json({"id": deleted_area_id}),
                    status_code=status.HTTP_202_ACCEPTED,
                )
            elif hasattr(delete_area, "from_mcp"):
                return {"id": deleted_area_id}
            else:
                print(f"Area `{area}` deleted with ID: {deleted_area_id}")
                return deleted_area_id
        except ValueError as e:
            print(e)
