from ..crud.node import make_crud_for
from ..models.nodes import (
    NodeType,
    SectionCreate,
    BlankModel,
    SectionOut,
    SectionRead,
    SectionUpdate,
    SectionDelete,
    SectionSearch,
)
from .sector import _list_sectors

from .__pre_init__ import register_cli_command

section_crud = make_crud_for(NodeType.section, SectionOut)

register_cli_command(
    "Sc",
    "create_section",
    section_crud.Create,
    SectionCreate,
    autocompletions={"sector_name": _list_sectors},
    shorthands={"sector_name": "-s"},
)
register_cli_command("Sl", "list_sections", section_crud.ReadAll, BlankModel)
register_cli_command("Sd", "delete_section", section_crud.Delete, SectionDelete)
register_cli_command("Su", "update_section", section_crud.Update, SectionUpdate)
register_cli_command("Sr", "read_section", section_crud.Read, SectionRead)
register_cli_command("Ss", "search_sections", section_crud.SearchByTitle, SectionSearch)


def _list_sections():
    o = section_crud._read_all()
    return [s.title for s in o]


section_crud.crud.get_or_create(SectionCreate(title="_"))
