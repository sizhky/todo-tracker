from torch_snippets import AD

from ..crud.area import create_area_in_db, get_all_areas_from_db, delete_area_from_db
from ..core.db import session_scope

from .__pre_init__ import cli


@cli.command(name="ac")
def create_area(
    name: str,
    description: str = "",
):
    """
    Create a new area in the database.
    """
    if "," in name:
        names = name.split(",")
        return [create_area(name) for name in names]

    with session_scope() as session:
        area = {
            "name": name,
            "description": description,
        }
        created_area = create_area_in_db(session, area)
        print(f"Area created with ID: {created_area.id}")
        return created_area.id


def _list_areas(skip: int = 0, limit: int = 100, return_ids: bool = False):
    """
    List all areas in the database with optional pagination.
    """
    with session_scope() as session:
        areas = get_all_areas_from_db(session, skip=skip, limit=limit)
        id2area = {area.id: area.name for area in areas}
        area2id = {area.name: area.id for area in areas}
        if return_ids:
            return AD(area2id, id2area)
        for area in areas:
            print(
                f"Area ID: {area.id}, Name: {area.name}, Description: `{area.description}`"
            )

        if not areas:
            print("No areas found.")


@cli.command(name="al")
def list_areas(skip: int = 0, limit: int = 100, return_ids: bool = False):
    """
    List all areas in the database with optional pagination.
    """
    _list_areas(skip=skip, limit=limit, return_ids=return_ids)


@cli.command(name="ad")
def delete_area(
    area: str,
):
    """
    Delete an area from the database by its name.
    """
    if "," in area:
        areas = area.split(",")
        return [delete_area(area) for area in areas]

    with session_scope() as session:
        try:
            area_id = _list_areas(return_ids=True).area2id.get(area)
            if not area_id:
                raise ValueError(f"Area with name {area} not found.")
            delete_area_from_db(session, area_id)
            print(f"Area with name {area} deleted successfully.")
        except ValueError as e:
            print(e)
