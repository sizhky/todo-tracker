from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ...models.v2.node import TimeEntry, Node, NodeType
from ...models.v2.time_entry import TimeEntryCreate, TimeEntryUpdate, TimeEntryRead

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
    db_time_entry = TimeEntry(
        task_id=time_entry.task_id,
        start=time_entry.start,
        end=time_entry.end,
        note=time_entry.note,
    )

    # Calculate duration if both start and end are provided
    if time_entry.start and time_entry.end:
        duration = (time_entry.end - time_entry.start).total_seconds()
        db_time_entry.duration = duration

    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def get_time_entries_for_task_from_db(
    db: Session, task_id: UUID, skip: int = 0, limit: int = 100
) -> List[TimeEntry]:
    """
    Retrieve all time entries for a specific task from the database.
    """
    statement = (
        select(TimeEntry).where(TimeEntry.task_id == task_id).offset(skip).limit(limit)
    )
    results = db.exec(statement)
    time_entries = results.all()
    return list(time_entries)


def get_time_entry_by_id_from_db(
    db: Session, time_entry_id: UUID
) -> Optional[TimeEntry]:
    """
    Retrieve a time entry by its ID.
    """
    return db.get(TimeEntry, time_entry_id)


def update_time_entry_in_db(
    db: Session, time_entry_id: UUID, time_entry_update: TimeEntryUpdate
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

    # Calculate duration if end time is provided
    if db_time_entry.end and db_time_entry.start:
        db_time_entry.duration = (
            db_time_entry.end - db_time_entry.start
        ).total_seconds()

    # Update updated_at field
    db_time_entry.updated_at = datetime.now(timezone.utc)

    db.add(db_time_entry)
    db.commit()
    db.refresh(db_time_entry)
    return db_time_entry


def delete_time_entry_from_db(db: Session, time_entry_id: UUID) -> bool:
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
    db: Session, task_id: UUID
) -> Optional[TimeEntry]:
    """
    Retrieve the active (not ended) time entry for a specific task.
    """
    statement = (
        select(TimeEntry)
        .where(TimeEntry.task_id == task_id)
        .where(TimeEntry.end.is_(None))
    )
    result = db.exec(statement)
    time_entry = result.first()
    return time_entry


def get_any_active_time_entry_from_db(db: Session) -> Optional[TimeEntry]:
    """
    Retrieve any active (not ended) time entry across all tasks.
    Assumes only one timer can be active at a time.
    """
    statement = select(TimeEntry).where(TimeEntry.end.is_(None))
    result = db.exec(statement)
    time_entry = result.first()
    return time_entry


def calculate_total_time_for_task(db: Session, task_id: UUID) -> float:
    """
    Calculate the total time spent on a task in seconds.
    Includes completed time entries and the duration of any active entry.
    """
    statement = select(TimeEntry).where(TimeEntry.task_id == task_id)
    entries = db.exec(statement).all()

    total_duration_seconds = 0.0
    for entry in entries:
        if entry.duration is not None:
            total_duration_seconds += entry.duration
        else:
            start_time = entry.start
            end_time = entry.end or datetime.now(timezone.utc)
            duration = end_time - start_time
            total_duration_seconds += duration.total_seconds()

    return round(total_duration_seconds, 2)
