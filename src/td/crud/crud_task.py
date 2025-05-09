from sqlmodel import Session, select
from typing import List

# Assuming your models are in ..models.task
# Adjust the import path if necessary
from ..models.task import Task, TaskCreate


def create_task_db(db: Session, task_in: TaskCreate) -> Task:
    """
    Create a new task in the database.
    """
    # Create a Task model instance from the TaskCreate schema
    # SQLModel handles the conversion and validation.
    # The default_factory for created_at and updated_at in the Task model
    # will be used automatically upon instance creation.
    db_task = Task.model_validate(task_in)

    db.add(db_task)
    db.commit()
    db.refresh(db_task)  # Refresh to get the auto-generated ID and other DB defaults
    return db_task


def get_all_tasks_db(db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Retrieve all tasks from the database with optional pagination.
    """
    statement = select(Task).offset(skip).limit(limit)
    results = db.exec(statement)
    tasks = results.all()
    return tasks
