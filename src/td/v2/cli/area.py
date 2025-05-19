from ..crud.node import make_crud_for
from ..models.nodes import (
    NodeType,
    AreaCreate,
    BlankModel,
    AreaOut,
    AreaRead,
    AreaUpdate,
    AreaDelete,
    AreaSearch,
)
from .sector import _list_sectors

from .__pre_init__ import register_cli_command

area_crud = make_crud_for(NodeType.area, AreaOut)

register_cli_command(
    "ac",
    "create_area",
    area_crud.Create,
    AreaCreate,
    autocompletions={"sector_name": _list_sectors},
    shorthands={"sector_name": "-s"},
)
register_cli_command("al", "list_areas", area_crud.ReadAll, BlankModel)
register_cli_command("ad", "delete_area", area_crud.Delete, AreaDelete)
register_cli_command("au", "update_area", area_crud.Update, AreaUpdate)
register_cli_command("ar", "read_area", area_crud.Read, AreaRead)
register_cli_command("as", "search_areas", area_crud.SearchByTitle, AreaSearch)


def _list_areas():
    o = area_crud._read_all()
    return [s.title for s in o]


area_crud.crud.get_or_create(AreaCreate(title="_"))
