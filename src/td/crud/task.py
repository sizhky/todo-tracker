from sqlmodel import Session, select
from typing import List

# Assuming your models are in ..models.task
# Adjust the import path if necessary
from ..models import Task, TaskCreate, Area, AreaCreate, Project, ProjectCreate


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


def create_task_in_db(db: Session, task: TaskCreate) -> Task:
    """
    Create a new task in the database.
    """
    # Create a Task model instance from the TaskCreate schema
    # SQLModel handles the conversion and validation.
    # The default_factory for created_at and updated_at in the Task model
    # will be used automatically upon instance creation.
    db_task = Task.model_validate(task)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # Refresh to get the auto-generated ID and other DB defaults
    return db_task


def get_all_tasks_from_db(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Retrieve all tasks from the database with optional pagination.
    """
    statement = select(Task).offset(skip).limit(limit)
    results = db.exec(statement)
    tasks = results.all()
    return tasks
