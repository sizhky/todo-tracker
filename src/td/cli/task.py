from ..core.db import session_scope
from ..crud.task import (
    create_task_in_db,
    get_all_tasks_from_db,
    delete_task_from_db,
    update_task_in_db,
    get_task_by_id,
)

from .__pre_init__ import cli
from .project import _list_projects, create_project


@cli.command(name="tc")
def create_task(
    title: str,
    description: str = "",
    status: int = 0,
    project: str = "default",
    project_id: int = None,
    area: str = None,
    area_id: int = None,
):
    """
    Create a new task in the database.

    Args:
        title: Title of the task. Multiple tasks can be created by providing comma-separated titles.
        description: Optional description for the task.
        status: Task status (0 = pending, 1 = done). Default is 0.
        project: Name of the project to associate with the task. If not found, it will be created.
        project_id: ID of the project to associate with the task. Takes precedence over project name.
        area: Name of the area to associate with the auto-created project (if needed).
        area_id: ID of the area to associate with the auto-created project (if needed).

    Returns:
        None. Prints confirmation message to console.
    """
    if project_id is None and project:
        # Check if the project exists
        project_id = _list_projects().project2id.get(project)
        if not project_id:
            project_id = create_project(
                name=project,
                description="Auto-created project",
                area=area,
                area_id=area_id,
            )
    elif project_id is None and project is None:
        raise ValueError("Either project or project_id must be provided.")

    if "," in title:
        return [
            create_task(
                title, description=description, status=status, project_id=project_id
            )
            for title in title.split(",")
        ]

    with session_scope() as session:
        task = {
            "title": title,
            "description": description,
            "status": status,
            "project_id": project_id,
        }
        created_task = create_task_in_db(session, task)
        print(f"Task created with ID: {created_task.id}")


@cli.command(name="tl")
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = True,
    as_hierarchy: bool = True,
):
    """
    List all tasks in the database with optional pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        pending_only: If True, only show tasks with status 0 (pending). Default is True.
        as_hierarchy: If True, group tasks by area and project. Default is True.

    Returns:
        JSON representation of tasks if called from MCP, dictionary of tasks if called from API,
        or prints the task information to console.
    """
    with session_scope() as session:
        tasks = get_all_tasks_from_db(
            session,
            skip=skip,
            limit=limit,
            pending_only=pending_only,
            as_hierarchy=as_hierarchy,
        )
        if not tasks:
            print("No tasks found.")
            return
        if as_hierarchy:
            from torch_snippets import pd

            _tasks = []
            for task in tasks:
                _tasks.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "status": task.status,
                        "project": task.project.name if task.project else None,
                        "area": (
                            task.project.area.name
                            if task.project and task.project.area
                            else None
                        ),
                        "task_time": task.total_time_seconds,
                    }
                )
            tasks = (
                pd.DataFrame(_tasks)[
                    ["title", "description", "project", "area", "id", "task_time"]
                ]
                .set_index(["area", "project"])
                .sort_index()
            )
            if hasattr(list_tasks, "from_mcp"):
                tasks = tasks.reset_index()
                return tasks.to_json(orient="records")
            elif hasattr(list_tasks, "from_api"):
                tasks = tasks.reset_index()
                return tasks.to_dict(orient="records")
            print(tasks)
            return
        print(f"{len(tasks)} Pending task{'' if len(tasks) == 1 else 's'} found")
        for task in tasks:
            print(f"ID: {task.id}, Title: {task.title}")


@cli.command(name="td")
def delete_task(
    task_id: str,
):
    """
    Delete a task from the database by its id.

    Args:
        task_id: ID of the task to delete. Multiple tasks can be deleted by providing comma-separated IDs.

    Returns:
        None. Prints confirmation message or error to console.
    """
    if isinstance(task_id, str) and "," in task_id:
        return [delete_task(id) for id in task_id.split(",")]

    try:
        task_id = int(task_id)
    except ValueError:
        raise ValueError(f"Invalid task ID: {task_id}. Task ID must be an integer.")

    with session_scope() as session:
        try:
            delete_task_from_db(session, task_id)
            print(f"Task with ID {task_id} deleted.")
        except Exception as e:
            print(f"Error deleting task with ID {task_id}: {e}")


@cli.command(name="tt")
def toggle_task(task_id: str):
    """
    Toggle the status of a task in the database by its id.

    Args:
        task_id: ID of the task to toggle. Multiple tasks can be toggled by providing comma-separated IDs.

    Returns:
        None. Prints confirmation message or error to console.
    """
    if isinstance(task_id, str) and "," in task_id:
        return [toggle_task(id) for id in task_id.split(",")]

    try:
        task_id = int(task_id)
    except ValueError:
        raise ValueError(f"Invalid task ID: {task_id}. Task ID must be an integer.")

    with session_scope() as session:
        try:
            task = get_task_by_id(session, task_id)
            task = update_task_in_db(
                session, task_id, {"status": 1 if task.status == 0 else 0}
            )
            print(
                f"Task with ID {task.id} toggled to {'done' if task.status == 1 else 'pending'}."
            )
        except Exception as e:
            print(f"Error toggling task with ID {task_id}: {e}")
