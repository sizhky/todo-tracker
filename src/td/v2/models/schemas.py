from sqlmodel import Session


class SectorCreate: ...


class SectorRead: ...


def create_area_in_db(db: Session, sector: SectorCreate) -> SectorRead: ...
