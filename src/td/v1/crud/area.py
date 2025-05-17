from sqlmodel import Session, select
from typing import List

from ..models import Area, AreaCreate

__all__ = ["create_area_in_db", "get_all_areas_from_db", "delete_area_from_db"]


def create_area_in_db(db: Session, area: AreaCreate) -> Area:
    """
    Create a new area in the database.
    """
    # Create an Area model instance from the AreaCreate schema
    # SQLModel handles the conversion and validation.
    db_area = Area.model_validate(area)

    db.add(db_area)
    db.commit()
    db.refresh(db_area)  # Refresh to get the auto-generated ID and other DB defaults
    return db_area


def get_all_areas_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[Area]:
    """
    Retrieve all areas from the database with optional pagination.
    """
    statement = select(Area).offset(skip).limit(limit)
    results = db.exec(statement)
    areas = results.all()
    return areas


def delete_area_from_db(db: Session, area_id: int) -> None:
    """
    Delete an area from the database by its ID.
    """
    statement = select(Area).where(Area.id == area_id)
    results = db.exec(statement)
    area = results.one_or_none()
    if area:
        db.delete(area)
        db.commit()
        return area.id
    else:
        raise ValueError(f"Area with ID {area_id} not found.")
