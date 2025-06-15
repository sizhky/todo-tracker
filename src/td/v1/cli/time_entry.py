from typer import Option, Argument
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..core.db import session_scope
from ..crud import get_task_by_id
from ..crud import (
    create_time_entry_in_db,
    get_time_entries_for_task_from_db,
    get_active_time_entry_for_task_from_db,
    update_time_entry_in_db,
    get_any_active_time_entry_from_db,  # Added import
    TimeEntryCreate,
    TimeEntryUpdate,
)
from .__pre_init__ import cli


@cli.command(name="trstart", help="Start a new time entry for a task.")
def start_time_entry(
    task_id: int = Argument(..., help="The ID of the task to start timing."),
    description: Optional[str] = Option(
        None, "--desc", "-d", help="Optional description for this time entry."
    ),
    time_stamp: Optional[datetime] = Option(
        None,
        "--time",
        "-t",
        help="Optional start time for the time entry. Defaults to now.",
    ),
):
    """
    Starts a new timer for the specified task.
    If there's an existing active timer for this task, it will be stopped first.
    """
    with session_scope() as session:
        task = get_task_by_id(session, task_id)
        if not task:
            print(f"Error: Task with ID {task_id} not found.")
            return

        active_entry = get_active_time_entry_for_task_from_db(session, task_id)
        start_time = time_stamp or datetime.now(timezone.utc)
        if active_entry:
            print(
                f"Info: Stopping active timer (ID: {active_entry.id}) for task '{task.title}'."
            )
            update_time_entry_in_db(
                session, active_entry.id, TimeEntryUpdate(end_time=start_time)
            )

        time_entry_create = TimeEntryCreate(
            task_id=task_id, description=description, start_time=start_time
        )
        db_time_entry = create_time_entry_in_db(session, time_entry_create)
        print(f"Timer started for task '{task.title}'. Entry ID: {db_time_entry.id}")


@cli.command(
    name="trstop",
    help="Stop the active time entry. If no task ID is given, stops any active timer.",
)
def stop_time_entry(
    task_id: Optional[int] = Argument(
        None, help="The ID of the task to stop timing. If None, stops any active timer."
    ),
    time_stamp: Optional[datetime] = Option(
        None,
        "--time",
        "-t",
        help="Optional end time for the time entry. Defaults to now.",
    ),
):
    """
    Stops the currently active timer.
    - If task_id is provided, stops the timer for that specific task.
    - If task_id is None, stops any currently active timer.
    """
    time_stamp = time_stamp or datetime.now(timezone.utc)
    with session_scope() as session:
        if task_id is None or not isinstance(task_id, int):
            # Stop any active timer
            active_entry = get_any_active_time_entry_from_db(session)
            if not active_entry:
                print("No active timer to stop.")
                return

            task = get_task_by_id(
                session, active_entry.task_id
            )  # Fetch task for its title
            update_data = TimeEntryUpdate(end_time=time_stamp)
            updated_entry = update_time_entry_in_db(
                session, active_entry.id, update_data
            )
            duration_seconds = (
                updated_entry.end_time - updated_entry.start_time
            ).total_seconds()
            duration_str = str(timedelta(seconds=int(duration_seconds)))
            print(
                f"Timer stopped for task '{task.title}' (ID: {task.id}). Entry ID: {updated_entry.id}. Duration: {duration_str}."
            )
        else:
            # Stop timer for a specific task
            task = get_task_by_id(session, task_id)
            if not task:
                print(f"Error: Task with ID {task_id} not found.")
                return

            active_entry = get_active_time_entry_for_task_from_db(session, task_id)
            if not active_entry:
                print(f"Warning: No active timer found for task '{task.title}'.")
                return

            update_data = TimeEntryUpdate(end_time=time_stamp)
            updated_entry = update_time_entry_in_db(
                session, active_entry.id, update_data
            )

            duration_seconds = (
                updated_entry.end_time - updated_entry.start_time
            ).total_seconds()
            duration_str = str(timedelta(seconds=int(duration_seconds)))
            print(
                f"Timer stopped for task '{task.title}'. Entry ID: {updated_entry.id}. Duration: {duration_str}."
            )


@cli.command(name="trl", help="List time entries for a task.")
def list_time_entries(
    task_id: int = Argument(..., help="The ID of the task to list time entries for."),
    limit: int = Option(
        100, "--limit", "-l", help="Maximum number of entries to display."
    ),
    skip: int = Option(
        0, "--skip", "-s", help="Number of entries to skip (for pagination)."
    ),
):
    """
    Lists all time entries associated with the specified task.
    """
    with session_scope() as session:
        task = get_task_by_id(session, task_id)
        if not task:
            print(f"Error: Task with ID {task_id} not found.")
            return

        time_entries = get_time_entries_for_task_from_db(
            session, task_id, skip=skip, limit=limit
        )
        if not time_entries:
            print(f"No time entries found for task '{task.title}'.")
            return

        print(f"Time Entries for Task: {task.title} (ID: {task.id})")
        print("---")
        for entry in time_entries:
            start_time_str = entry.start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = (
                entry.end_time.strftime("%Y-%m-%d %H:%M:%S")
                if entry.end_time
                else "Active"
            )
            duration_str = "-"
            if entry.end_time:
                duration_seconds = (entry.end_time - entry.start_time).total_seconds()
                duration_str = str(timedelta(seconds=int(duration_seconds)))

            print(f"  ID: {entry.id}")
            print(f"    Start Time: {start_time_str}")
            print(f"    End Time: {end_time_str}")
            print(f"    Duration: {duration_str}")
            print(f"    Description: {entry.description or 'N/A'}")
            print("  ---")


@cli.command(name="trt", help="Toggle the time tracker for a task.")
def task_track(
    task_id: int = Argument(..., help="The ID of the task to track."),
    time_stamp: Optional[datetime] = Option(
        None,
        "--time",
        "-t",
        help="Optional start time for the time entry. Defaults to now.",
    ),
):
    """
    Toggles the time tracker for a task.
    - If the specified task is already being tracked, it stops the timer.
    - If another task is being tracked, it stops that timer and starts timing the specified task.
    - If no task is being tracked, it starts timing the specified task.
    """
    time_stamp = time_stamp or datetime.now(timezone.utc)
    with session_scope() as session:
        task_to_track = get_task_by_id(session, task_id)
        if not task_to_track:
            print(f"Error: Task with ID {task_id} not found.")
            return

        # Check for any active timer
        any_active_entry = get_any_active_time_entry_from_db(session)

        if any_active_entry:
            active_task = get_task_by_id(
                session, any_active_entry.task_id
            )  # Get the task associated with the active entry
            # Stop the currently active timer
            update_data = TimeEntryUpdate(end_time=time_stamp)
            updated_entry = update_time_entry_in_db(
                session, any_active_entry.id, update_data
            )
            duration_seconds = (
                updated_entry.end_time - updated_entry.start_time
            ).total_seconds()
            duration_str = str(timedelta(seconds=int(duration_seconds)))
            print(
                f"Timer stopped for task '{active_task.title}' (ID: {active_task.id}). Entry ID: {updated_entry.id}. Duration: {duration_str}."
            )

            # If the active timer was for the specified task, we just stop it.
            if any_active_entry.task_id == task_id:
                return  # Timer stopped, nothing more to do

        # If we are here, it means either no timer was active, or a different timer was active and has been stopped.
        # Now, start a new timer for the specified task.
        time_entry_create = TimeEntryCreate(
            task_id=task_id,
            start_time=time_stamp,
            description=f"Tracking task {task_to_track.title}",
        )
        db_time_entry = create_time_entry_in_db(session, time_entry_create)
        print(
            f"Timer started for task '{task_to_track.title}' (ID: {task_to_track.id}). Entry ID: {db_time_entry.id}"
        )
