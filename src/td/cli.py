from typer import Typer

from .crud.task import (
    create_task_in_db,
    get_all_tasks_from_db,
    create_project_in_db,
    create_area_in_db,
)
from .core.db import session_scope, create_db_and_tables

cli = Typer()
create_db_and_tables()


@cli.command(name="ca")
def create_area(
    name: str,
    description: str = "",
):
    """
    Create a new area in the database.
    """
    with session_scope() as session:
        area = {
            "name": name,
            "description": description,
        }
        created_area = create_area_in_db(session, area)
        print(f"Area created with ID: {created_area.id}")


@cli.command(name="cp")
def create_project(
    name: str,
    description: str = "",
    area: str = None,
):
    """
    Create a new project in the database.
    """
    with session_scope() as session:
        project = {
            "name": name,
            "description": description,
            "area": area,
        }
        created_project = create_project_in_db(session, project)
        print(f"Project created with ID: {created_project.id}")


@cli.command(name="ct")
def create_task(
    title: str,
    description: str = "",
    status: str = "pending",
    project: str = None,
):
    """
    Create a new task in the database.
    """
    with session_scope() as session:
        task = {
            "title": title,
            "description": description,
            "status": status,
            "project": project,
        }
        created_task = create_task_in_db(session, task)
        print(f"Task created with ID: {created_task.id}")


@cli.command(name="lt")
def list_tasks(skip: int = 0, limit: int = 100):
    """
    List all tasks in the database with optional pagination.
    """
    with session_scope() as session:
        tasks = get_all_tasks_from_db(session, skip=skip, limit=limit)
        for task in tasks:
            print(f"ID: {task.id}, Title: {task.title}, Status: {task.status}")
