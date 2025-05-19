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
from .sector import _list_sectors, sector_crud, SectorCreate
from .area import _list_areas, area_crud, AreaCreate
from .project import _list_projects, project_crud, ProjectCreate
from .section import _list_sections, section_crud, SectionCreate

from .__pre_init__ import register_cli_command

task_crud = make_crud_for(NodeType.task, TaskOut)


def create_heirarchy(
    task: TaskCreate,
):
    sector = sector_crud.get_or_create(SectorCreate(title=task.sector_name))
    area = area_crud.get_or_create(
        AreaCreate(title=task.area_name, parent_id=sector.id)
    )
    project = project_crud.get_or_create(
        ProjectCreate(title=task.project_name, parent_id=area.id)
    )
    section = section_crud.get_or_create(
        SectionCreate(title=task.section_name, parent_id=project.id)
    )
    return section


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
    },
    shorthands={
        "section_name": "-S",
        "project_name": "-p",
        "area_name": "-a",
        "sector_name": "-s",
    },
)
register_cli_command("tl", "list_tasks", task_crud.ReadAll, BlankModel)
register_cli_command("td", "delete_task", task_crud.Delete, TaskDelete)
register_cli_command("tu", "update_task", task_crud.Update, TaskUpdate)
register_cli_command("tr", "read_task", task_crud.Read, TaskRead)
register_cli_command("ts", "search_tasks", task_crud.SearchByTitle, TaskSearch)


def _list_tasks():
    o = task_crud._read_all()
    return [s.title for s in o]
