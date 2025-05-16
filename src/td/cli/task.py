from typing_extensions import Annotated
from starlette.responses import Response
from starlette import status as http_status
from typer import Option
from torch_snippets import write_json

from ..core.db import session_scope
from ..crud.task import (
    create_task_in_db,
    get_all_tasks_from_db,
    delete_task_from_db,
    update_task_in_db,
    get_task_by_id,
)
from ..crud.time_entry import (
    TimeEntryCreate,
    TimeEntryUpdate,
    create_time_entry_in_db,
    update_time_entry_in_db,
    get_active_time_entry_for_task_from_db,
)

from .__pre_init__ import cli
from .area import __list_areas
from .project import _list_projects, create_project, __list_projects


@cli.command(name="tc")
def create_task(
    title: str,
    project: Annotated[
        str | None,
        Option(
            "-p",
            help="Name of the project to associate with the task",
            autocompletion=__list_projects,
        ),
    ] = None,
    area: Annotated[
        str | None,
        Option(
            "-a",
            help="Name of the area to associate with the task",
            autocompletion=__list_areas,
        ),
    ] = None,
    description: Annotated[
        str,
        Option(
            "-d",
            help="Description of the task",
        ),
    ] = "",
    start_time: Annotated[
        str | None,
        Option(
            "-s",
            "--start",
            help="Start time for the task in ISO format (e.g., 2023-10-01T12:00:00)",
        ),
    ] = None,
    end_time: Annotated[
        str | None,
        Option(
            "-e",
            "--end",
            help="End time for the task in ISO format (e.g., 2023-10-01T12:00:00)",
        ),
    ] = None,
    status: int = 0,
    project_id: int = None,
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
    if end_time is not None and start_time is None:
        raise ValueError("start_time must be provided if end_time is specified.")
    default_area = "uncategorized"
    default_project = "inbox"
    if area and not project:
        project = area
    if project is None:
        project = default_project
        area = default_area
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
        assert start_time is None and end_time is None, (
            "start_time and end_time are not supported for multiple tasks."
        )
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
        if start_time is not None:
            time_entry = TimeEntryCreate(
                task_id=created_task.id,
                start_time=start_time,
                end_time=end_time,
            )
            create_time_entry_in_db(session, time_entry)
        if hasattr(create_task, "from_api"):
            # return 201 created
            return Response(
                write_json({"id": created_task.id}),
                status_code=http_status.HTTP_201_CREATED,
            )
        elif hasattr(create_task, "from_mcp"):
            return {"id": created_task.id}
        else:
            print(f"Task created with ID: {created_task.id}")
        return created_task.id


@cli.command(name="tl")
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    pending_only: bool = True,
    as_hierarchy: bool = True,
    as_string: bool = False,
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
        active_time_entry = get_active_time_entry_for_task_from_db(
            session, task_id=None
        )
        active_task_id = None
        if active_time_entry:
            active_task_id = active_time_entry.task_id
        if not tasks:
            print("No tasks found.")
            return
        if as_hierarchy:
            from torch_snippets import pd

            _tasks = []
            for task in tasks:
                title = task.title if task.id != active_task_id else f"*{task.title}"
                _tasks.append(
                    {
                        "id": task.id,
                        "title": title,
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
                    ["title", "id", "description", "project", "area", "task_time"]
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
            elif as_string:
                tasks = tasks.reset_index()
                return tasks
            print(tasks)
            return
        print(f"{len(tasks)} Pending task{'' if len(tasks) == 1 else 's'} found")
        for task in tasks:
            print(f"ID: {task.id}, Title: {task.title}")


@cli.command(name="tw")
def watch_tasks():
    import time
    import sys
    from datetime import datetime

    try:
        # Hide cursor for cleaner display
        print("\033[?25l", end="")

        # Get initial terminal size and task data
        tasks_data = list_tasks(as_string=True)
        lines_count = len(str(tasks_data).split("\n"))

        while True:
            # Move cursor to beginning
            print("\033[H", end="")

            # Get updated tasks
            tasks_data = list_tasks(as_string=True)

            # Display timestamp and tasks
            now = datetime.now().strftime("%H:%M:%S")
            print(f"Tasks as of {now} (Press Ctrl+C to exit)")
            print(tasks_data)

            # Clear any remaining lines from previous output
            current_lines = (
                len(str(tasks_data).split("\n")) + 2
            )  # +2 for timestamp and header
            if lines_count > current_lines:
                for _ in range(lines_count - current_lines):
                    print("\033[K")  # Clear line
                lines_count = current_lines
            else:
                lines_count = current_lines

            # Ensure output is displayed immediately
            sys.stdout.flush()

            # Wait before refresh
            time.sleep(1)
    except KeyboardInterrupt:
        # Show cursor again before exiting
        print("\033[?25h", end="")
        return
    finally:
        # Ensure cursor is visible even if there's an error
        print("\033[?25h", end="")


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
        If the task has an active time entry, it will be stopped.
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
            task_status = 0 if task.status else 1
            task = update_task_in_db(session, task_id, {"status": task_status})
            _time_entry = get_active_time_entry_for_task_from_db(session, task_id)
            if task.status == 1 and _time_entry:
                from datetime import datetime

                end_time = datetime.now()
                time_entry = TimeEntryUpdate(
                    task_id=task.id,
                    end_time=end_time,
                )
                update_time_entry_in_db(session, _time_entry.id, time_entry)
                print(
                    f"Timer stopped for task '{task.title}' (ID: {task.id}). Entry ID: {_time_entry.id}."
                )
            print(f"Task with ID {task.id} ({task.title}) toggled to {task_status}.")
        except Exception as e:
            print(f"Error toggling task with ID {task_id}: {e}")
