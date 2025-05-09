from sqlmodel import Session, select
from typing import List
from sqlalchemy.orm import joinedload

from ..models import Project, ProjectCreate, ProjectRead, ProjectUpdate


def create_project_in_db(db: Session, project: ProjectCreate) -> Project:
    """
    Create a new project in the database.
    """
    # Create a Project model instance from the ProjectCreate schema
    # SQLModel handles the conversion and validation.
    db_project = Project.model_validate(project)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)  # Refresh to get the auto-generated ID and other DB defaults
    return db_project


def get_all_projects_from_db(
    db: Session, skip: int = 0, limit: int = 100
) -> List[Project]:
    """
    Retrieve all projects from the database with optional pagination.
    """
    statement = (
        select(Project).offset(skip).limit(limit).options(joinedload(Project.area))
    )
    results = db.exec(statement)
    projects = results.all()
    return projects


def get_project_by_id(db: Session, project_id: int) -> ProjectRead:
    """
    Retrieve a project by its ID.
    """
    statement = select(Project).where(Project.id == project_id)
    result = db.exec(statement)
    project = result.one_or_none()
    if project:
        return ProjectRead.model_validate(project)
    return None


def update_project_in_db(
    db: Session, project_id: int, project_update: ProjectUpdate
) -> Project:
    """
    Update an existing project in the database.
    """
    # Fetch the existing project
    statement = select(Project).where(Project.id == project_id)
    result = db.exec(statement)
    project = result.one_or_none()

    if not project:
        return None

    # Update the project fields
    for key, value in project_update.model_dump().items():
        if value is not None:
            setattr(project, key, value)

    db.add(project)
    db.commit()
    db.refresh(project)  # Refresh to get the updated values
    return project


def delete_project_from_db(db: Session, project_id: int) -> bool:
    """
    Delete a project by its ID.
    """
    # Fetch the existing project
    statement = select(Project).where(Project.id == project_id)
    result = db.exec(statement)
    project = result.one_or_none()

    if not project:
        return False

    db.delete(project)
    db.commit()
    return True


def get_projects_by_area_id(
    db: Session, area_id: int, skip: int = 0, limit: int = 100
) -> List[Project]:
    """
    Retrieve all projects associated with a specific area ID.
    """
    statement = (
        select(Project).where(Project.area_id == area_id).offset(skip).limit(limit)
    )
    results = db.exec(statement)
    projects = results.all()
    return projects
