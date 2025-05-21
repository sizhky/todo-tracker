from ..crud.node import make_crud_for
from ..models.nodes import (
    NodeType,
    TaskCreate,
    BlankModel,
    TaskOut,
    TaskRead,
    TaskUpdate,
    TaskDelete,
    TaskSearch,
)
from .sector import _list_sectors
from .area import _list_areas
from .project import _list_projects
from .section import _list_sections
from .display import fetch_all_paths

from .__pre_init__ import register_cli_command

task_crud = make_crud_for(NodeType.task, TaskOut)


register_cli_command(
    "tc",
    "create_task",
    task_crud.Create,
    TaskCreate,
    autocompletions={
        "section_name": _list_sections,
        "project_name": _list_projects,
        "area_name": _list_areas,
        "sector_name": _list_sectors,
        "path": fetch_all_paths,
    },
    shorthands={
        "section_name": "-S",
        "project_name": "-p",
        "area_name": "-a",
        "sector_name": "-s",
        "path": "-P",
    },
)
register_cli_command("tl", "list_tasks", task_crud.ReadAll, BlankModel)
register_cli_command("td", "delete_task", task_crud.Delete, TaskDelete)
register_cli_command(
    "tu",
    "update_task",
    task_crud.Update,
    TaskUpdate,
    autocompletions={"path": fetch_all_paths},
    shorthands={"path": "-P"},
)
register_cli_command("tr", "read_task", task_crud.Read, TaskRead)
register_cli_command("ts", "search_tasks", task_crud.SearchByTitle, TaskSearch)


def _list_tasks():
    o = task_crud._read_all()
    return [s.title for s in o]
