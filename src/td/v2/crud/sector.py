__all__ = [
    "db_create_sector",
    "db_get_sector",
    "db_get_all_sectors",
    "db_update_sector",
    "db_delete_sector",
]


from ..models.nodes import Sector as SectorIn, NodeType
from ..crud.node import NodeCrud, make_crud_for
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List


class SectorOut(BaseModel):
    id: UUID
    title: str
    meta: Optional[str]

    class Config:
        from_attributes = True


sector_crud = NodeCrud(NodeType.sector, SectorOut)
# sector_ops = make_crud_for(NodeType.sector, SectorIn, SectorOut)


def db_create_sector(sector: SectorIn) -> SectorOut:
    return sector_crud.create(sector)


def db_get_sector(sector_id: UUID) -> Optional[SectorOut]:
    return sector_crud.read(sector_id)


def db_get_all_sectors() -> List[SectorOut]:
    return sector_crud.read_all()


def db_update_sector(sector_id: UUID, sector: SectorIn) -> Optional[SectorOut]:
    return sector_crud.update(sector_id, sector)


def db_delete_sector(sector_id: UUID) -> bool:
    return sector_crud.delete(sector_id)
