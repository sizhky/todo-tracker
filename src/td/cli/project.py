from torch_snippets import AD

from ..core.db import session_scope
from ..crud.project import (
    create_project_in_db,
    get_all_projects_from_db,
    delete_project_from_db,
)

from .__pre_init__ import cli
from .area import _list_areas, create_area


@cli.command(name="pc")
def create_project(
    name: str,
    description: str = "",
    area: str = "default",
    area_id: int = None,
):
    """
    Create a new project in the database.
    """

    if area_id is None and area:
        # Check if the area exists
        area_id = _list_areas(return_ids=True).area2id.get(area)
        if not area_id:
            area_id = create_area(name=area, description="Auto-created area")
    elif area_id is None and area is None:
        raise ValueError("Either area or area_id must be provided.")

    if "," in name:
        return [create_project(name, area_id=area_id) for name in name.split(",")]

    with session_scope() as session:
        project = {
            "name": name,
            "description": description,
            "area_id": area_id,
        }
        created_project = create_project_in_db(session, project)
        print(f"Project created with ID: {created_project.id}")
        return created_project.id


def _list_projects(skip: int = 0, limit: int = 100):
    """
    List all projects in the database with optional pagination.
    """
    from torch_snippets import pd

    with session_scope() as session:
        projects = get_all_projects_from_db(session, skip=skip, limit=limit)
        id2project = {project.id: project.name for project in projects}
        project2id = {project.name: project.id for project in projects}
        projects = pd.DataFrame(
            [
                (project.name, project.description, project.area.name)
                if project.area
                else None
                for project in projects
            ],
            columns=["project_name", "description", "area_name"],
        )
        return AD(id2project, project2id, projects)


@cli.command(name="pl")
def list_projects(skip: int = 0, limit: int = 100):
    """
    List all projects in the database with optional pagination.
    """
    x = _list_projects(skip=skip, limit=limit)
    if hasattr(list_projects, "from_mcp"):
        return x.projects.to_json(orient="records")
    else:
        print(x.projects)
    if not len(x.projects):
        print("No projects found.")


@cli.command(name="pd")
def delete_project(
    project: str,
):
    """
    Delete a project from the database by its name.
    """
    if "," in project:
        return [delete_project(name) for name in project.split(",")]
    with session_scope() as session:
        try:
            project_id = _list_projects(return_ids=True).project2id.get(project)
            if not project_id:
                raise ValueError(f"Project with name {project} not found.")
            # Assuming you have a function to delete a project
            delete_project_from_db(session, project_id)
            print(f"Project with ID {project_id} deleted.")
        except Exception as e:
            print(f"Error deleting project: {e}")
