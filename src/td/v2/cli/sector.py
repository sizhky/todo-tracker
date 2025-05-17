from ..crud.node import make_crud_for
from ..models.nodes import (
    NodeType,
    SectorCreate,
    SectorOut,
    BlankModel,
    SectorDelete,
    SectorUpdate,
    SectorRead,
    SectorSearch,
)

from .__pre_init__ import register_cli_command

sector_crud = make_crud_for(NodeType.sector, SectorOut)


register_cli_command("sc", "create_sector", sector_crud.Create, SectorCreate)
register_cli_command("sl", "list_sectors", sector_crud.ReadAll, BlankModel)
register_cli_command("sd", "delete_sector", sector_crud.Delete, SectorDelete)
register_cli_command("su", "update_sector", sector_crud.Update, SectorUpdate)
register_cli_command("sr", "read_sector", sector_crud.Read, SectorRead)
register_cli_command("ss", "search_sectors", sector_crud.SearchByTitle, SectorSearch)


def _list_sectors():
    o = sector_crud._read_all()
    return [s.title for s in o]


sector_crud.crud.read_or_create(SectorCreate(title="_default"))
