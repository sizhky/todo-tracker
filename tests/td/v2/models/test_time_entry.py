import pytest
from datetime import datetime, timezone
from uuid import UUID

from src.td.v2.models.nodes import TimeEntry


def test_time_entry_creation(test_session, sample_task):
    """Test that a TimeEntry can be created correctly."""
    # Create a time entry
    time_entry = TimeEntry(
        task_id=sample_task.id,
        start=datetime.fromisoformat("2023-01-01T10:00:00"),
        end=datetime.fromisoformat("2023-01-01T11:00:00"),
        duration=3600,  # 1 hour in seconds
    )
    test_session.add(time_entry)
    test_session.commit()
    test_session.refresh(time_entry)

    # Verify the time entry was created properly
    assert time_entry.id is not None
    assert isinstance(time_entry.id, UUID)
    assert time_entry.task_id == sample_task.id
    assert time_entry.start.isoformat() == "2023-01-01T10:00:00"
    assert time_entry.end.isoformat() == "2023-01-01T11:00:00"
    assert time_entry.duration == 3600

    # Retrieve the time entry from DB to ensure it was saved
    retrieved_entry = test_session.get(TimeEntry, time_entry.id)
    assert retrieved_entry is not None
    assert retrieved_entry.task_id == sample_task.id


def test_time_entry_update(test_session, sample_time_entry):
    """Test that a TimeEntry can be updated."""
    # Update the time entry
    sample_time_entry.end = datetime.fromisoformat("2023-01-01T12:00:00")
    sample_time_entry.duration = 7200  # 2 hours in seconds
    test_session.commit()
    test_session.refresh(sample_time_entry)

    # Verify the update worked
    assert sample_time_entry.end.isoformat() == "2023-01-01T12:00:00"
    assert sample_time_entry.duration == 7200


def test_time_entry_relation_to_node(test_session, sample_task):
    """Test the relationship between TimeEntry and Node."""
    # Create multiple time entries for the same task
    entries = []
    for i in range(3):
        entry = TimeEntry(
            task_id=sample_task.id,
            start=datetime.fromisoformat(f"2023-01-0{i + 1}T10:00:00"),
            end=datetime.fromisoformat(f"2023-01-0{i + 1}T11:00:00"),
            duration=3600,
        )
        test_session.add(entry)
        entries.append(entry)

    test_session.commit()

    # Query all time entries for the task
    task_entries = (
        test_session.query(TimeEntry).filter(TimeEntry.task_id == sample_task.id).all()
    )

    # Verify we have all the entries (not including the fixture entry which is missing because we're using a separate test session)
    assert len(task_entries) == 3

    # Check if all entries have the correct task_id
    for entry in task_entries:
        assert entry.task_id == sample_task.id
