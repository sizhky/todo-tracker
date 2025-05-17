from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timezone

from ..models import TimeEntry, TimeEntryCreate, TimeEntryUpdate

__all__ = [
    "create_time_entry_in_db",
    "get_time_entries_for_task_from_db",
    "get_time_entry_by_id_from_db",
    "update_time_entry_in_db",
    "delete_time_entry_from_db",
    "get_active_time_entry_for_task_from_db",
    "get_any_active_time_entry_from_db",
    "calculate_total_time_for_task",
    "TimeEntryCreate",
    "TimeEntryUpdate",
]

__all__ = [
    "create_time_entry_in_db",
    "get_time_entries_for_task_from_db",
    "get_time_entry_by_id_from_db",
    "update_time_entry_in_db",
    "delete_time_entry_from_db",
    "get_active_time_entry_for_task_from_db",
    "get_any_active_time_entry_from_db",
    "calculate_total_time_for_task",
    "TimeEntryCreate",
    "TimeEntryUpdate",
]


def create_time_entry_in_db(db: Session, time_entry: TimeEntryCreate) -> TimeEntry:
    """
    Create a new time entry in the database.
    """
    db_time_entry = TimeEntry.model_validate(time_entry)
    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def get_time_entries_for_task_from_db(
    db: Session, task_id: int, skip: int = 0, limit: int = 100
) -> List[TimeEntry]:
    """
    Retrieve all time entries for a specific task from the database.
    """
    statement = (
        select(TimeEntry).where(TimeEntry.task_id == task_id).offset(skip).limit(limit)
    )
    results = db.exec(statement)
    time_entries = results.all()
    return time_entries


def get_time_entry_by_id_from_db(
    db: Session, time_entry_id: int
) -> Optional[TimeEntry]:
    """
    Retrieve a time entry by its ID.
    """
    statement = select(TimeEntry).where(TimeEntry.id == time_entry_id)
    result = db.exec(statement)
    time_entry = result.one_or_none()
    return time_entry


def update_time_entry_in_db(
    db: Session, time_entry_id: int, time_entry_update: TimeEntryUpdate
) -> Optional[TimeEntry]:
    """
    Update an existing time entry in the database.
    """
    db_time_entry = get_time_entry_by_id_from_db(db, time_entry_id)
    if not db_time_entry:
        return None

    update_data = time_entry_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_time_entry, key, value)

    # Manually update updated_at
    db_time_entry.updated_at = datetime.now(timezone.utc)

    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def delete_time_entry_from_db(db: Session, time_entry_id: int) -> bool:
    """
    Delete a time entry from the database by its ID.
    Returns True if deleted, False otherwise.
    """
    db_time_entry = get_time_entry_by_id_from_db(db, time_entry_id)
    if db_time_entry:
        db.delete(db_time_entry)
        db.commit()
        return True
    return False


def get_active_time_entry_for_task_from_db(
    db: Session, task_id: int
) -> Optional[TimeEntry]:
    """
    Retrieve the active (not ended) time entry for a specific task.
    """
    statement = (
        select(TimeEntry)
        .where(TimeEntry.task_id == task_id)
        .where(TimeEntry.end_time.is_(None))  # Corrected comparison
    )
    result = db.exec(statement)
    time_entry = result.one_or_none()
    return time_entry


def get_any_active_time_entry_from_db(db: Session) -> Optional[TimeEntry]:
    """
    Retrieve any active (not ended) time entry across all tasks.
    Assumes only one timer can be active at a time.
    """
    statement = (
        select(TimeEntry).where(TimeEntry.end_time.is_(None))  # Corrected comparison
    )
    result = db.exec(statement)
    time_entry = result.one_or_none()  # Should be at most one
    return time_entry


def calculate_total_time_for_task(db: Session, task_id: int) -> float:
    """
    Calculate the total time spent on a task in seconds.
    Includes completed time entries and the duration of any active entry.
    """
    statement = select(TimeEntry).where(TimeEntry.task_id == task_id)
    entries = db.exec(statement).all()

    total_duration_seconds = 0.0
    for entry in entries:
        start_time = entry.start_time
        end_time = (
            entry.end_time or datetime.now(timezone.utc)
        )  # Use current UTC time if entry is active
        duration = end_time - start_time
        total_duration_seconds += duration.total_seconds()

    return round(total_duration_seconds, 2)
