from ..crud.node import make_crud_for
from ..models.nodes import (
    NodeType,
    ProjectCreate,
    BlankModel,
    ProjectOut,
    ProjectRead,
    ProjectUpdate,
    ProjectDelete,
    ProjectSearch,
)
from .sector import _list_sectors
from .area import _list_areas
from .display import fetch_all_paths

from .__pre_init__ import register_cli_command

project_crud = make_crud_for(NodeType.project, ProjectOut)

register_cli_command(
    "pc",
    "create_project",
    project_crud.Create,
    ProjectCreate,
    autocompletions={
        "area_name": _list_areas,
        "sector_name": _list_sectors,
        "path": fetch_all_paths,
    },
    shorthands={"area_name": "-a", "sector_name": "-s", "path": "-P"},
)
register_cli_command("pl", "list_projects", project_crud.ReadAll, BlankModel)
register_cli_command("pd", "delete_project", project_crud.Delete, ProjectDelete)
register_cli_command("pu", "update_project", project_crud.Update, ProjectUpdate)
register_cli_command("pr", "read_project", project_crud.Read, ProjectRead)
register_cli_command("ps", "search_projects", project_crud.SearchByTitle, ProjectSearch)


def _list_projects():
    o = project_crud._read_all()
    return [s.title for s in o]


project_crud.crud.get_or_create(ProjectCreate(title="_"))
