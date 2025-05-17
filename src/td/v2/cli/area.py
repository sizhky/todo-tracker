from ..crud.node import make_crud_for
from ..models.nodes import NodeType, AreaCreate, BlankModel, AreaOut
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

area_crud.crud.read_or_create(AreaCreate(title="_default"))
