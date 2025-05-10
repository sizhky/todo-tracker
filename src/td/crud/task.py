from sqlmodel import Session, select
from typing import List
from sqlalchemy.orm import joinedload

# Assuming your models are in ..models.task
# Adjust the import path if necessary
from ..models import Task, TaskCreate, Project, TaskUpdate


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
) -> List[Task]:
    """
    Retrieve all tasks from the database with optional pagination.
    """
    if as_hierarchy:
        statement = (
            select(Task)
            .options(joinedload(Task.project).joinedload(Project.area))
            .offset(skip)
            .limit(limit)
        )
    else:
        statement = select(Task).offset(skip).limit(limit)
        if pending_only:
            statement = statement.where(Task.status == 0)
    results = db.exec(statement)
    tasks = results.all()
    return tasks


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
