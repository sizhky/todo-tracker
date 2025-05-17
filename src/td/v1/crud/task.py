from sqlmodel import Session, select
from typing import List
from sqlalchemy.orm import joinedload

# Assuming your models are in ..models.task
# Adjust the import path if necessary
<<<<<<<< HEAD:src/td/v1/crud/task.py
from ..models import Task, TaskCreate, Project, TaskUpdate, TaskRead
========
from ...models.v1 import Task, TaskCreate, Project, TaskUpdate, TaskRead
>>>>>>>> 92d1087 (make crud and models as v1):src/td/v1/crud/v1/task.py
from .time_entry import calculate_total_time_for_task

__all__ = [
    "create_task_in_db",
    "get_all_tasks_from_db",
    "delete_task_from_db",
    "update_task_in_db",
    "get_task_by_id",
]


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


def get_all_tasks_from_db(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = False,
    as_hierarchy=False,
) -> List[TaskRead]:
    """
    Retrieve all tasks from the database with optional pagination.
    Includes total time spent on each task.
    """
    query_options = []
    if as_hierarchy:
        query_options.append(joinedload(Task.project).joinedload(Project.area))

    statement = select(Task).options(*query_options).offset(skip).limit(limit)

    if pending_only:
        statement = statement.where(Task.status == False)  # noqa

    db_tasks = db.exec(statement).all()

    tasks_with_time = []
    for db_task in db_tasks:
        total_time = calculate_total_time_for_task(db, db_task.id)
        task_read = TaskRead.model_validate(db_task)  # Convert Task to TaskRead
        task_read.total_time_seconds = total_time
        tasks_with_time.append(task_read)

    return tasks_with_time


def delete_task_from_db(db: Session, task_id: int) -> None:
    """
    Delete a task from the database by its ID.
    """
    statement = select(Task).where(Task.id == task_id)
    task = db.exec(statement).first()
    if task:
        db.delete(task)
        db.commit()
    else:
        print(f"Task with ID {task_id} not found.")


def update_task_in_db(db: Session, task_id: int, task_data: TaskUpdate) -> Task:
    """
    Update an existing task in the database.
    """
    statement = select(Task).where(Task.id == task_id)
    task = db.exec(statement).first()
    task_data = TaskUpdate.model_validate(task_data)
    if task:
        for key, value in task_data.model_dump().items():
            if value is None:
                continue
            setattr(task, key, value)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    else:
        print(f"Task with ID {task_id} not found.")
        return None


def get_task_by_id(db: Session, task_id: int) -> Task:
    """
    Retrieve a task from the database by its ID.
    """
    statement = select(Task).where(Task.id == task_id)
    task = db.exec(statement).first()
    if task:
        return task
    else:
        print(f"Task with ID {task_id} not found.")
        return None
