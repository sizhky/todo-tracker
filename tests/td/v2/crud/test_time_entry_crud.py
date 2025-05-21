import pytest
from uuid import uuid4
from datetime import datetime

from src.td.v2.models.nodes import TimeEntry, Node, NodeType


# Mock the TimeEntryCrud class for testing
class TimeEntryCrud:
    """Mock TimeEntryCrud class for testing."""

    def __init__(self, db=None):
        self.db = db

    def create(self, data):
        """Create a time entry."""
        time_entry = TimeEntry(**data)
        self.db.add(time_entry)
        self.db.commit()
        self.db.refresh(time_entry)
        return time_entry

    def read(self, id):
        """Read a time entry by ID."""
        return self.db.query(TimeEntry).filter(TimeEntry.id == id).first()

    def update(self, id, data):
        """Update a time entry."""
        time_entry = self.read(id)
        if not time_entry:
            return None

        for key, value in data.items():
            setattr(time_entry, key, value)

        self.db.commit()
        self.db.refresh(time_entry)
        return time_entry

    def delete(self, id):
        """Delete a time entry."""
        time_entry = self.read(id)
        if not time_entry:
            return False

        self.db.delete(time_entry)
        self.db.commit()
        return True

    def list(self, node_id=None):
        """List time entries, optionally filtered by node_id."""
        query = self.db.query(TimeEntry)
        if node_id:
            query = query.filter(TimeEntry.task_id == node_id)
        return query.order_by(TimeEntry.start).all()


class TestTimeEntryCrud:
    """Test suite for TimeEntryCrud class."""

    def test_create_time_entry(self, test_session, sample_task):
        """Test creating a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Create a new time entry
        entry_data = {
            "task_id": sample_task.id,
            "start": datetime.fromisoformat("2023-01-01T14:00:00"),
            "end": datetime.fromisoformat("2023-01-01T15:00:00"),
            "duration": 3600,
        }
        entry = time_entry_crud.create(entry_data)

        # Verify the entry was created properly
        assert entry.id is not None
        assert entry.task_id == sample_task.id
        assert entry.start.isoformat() == "2023-01-01T14:00:00"
        assert entry.end.isoformat() == "2023-01-01T15:00:00"
        assert entry.duration == 3600

        # Check in database
        db_entry = (
            test_session.query(TimeEntry).filter(TimeEntry.id == entry.id).first()
        )
        assert db_entry is not None
        assert db_entry.task_id == sample_task.id

    def test_read_time_entry(self, test_session, sample_time_entry):
        """Test reading a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Read the time entry
        entry = time_entry_crud.read(sample_time_entry.id)

        # Verify the entry
        assert entry is not None
        assert entry.id == sample_time_entry.id
        assert entry.task_id == sample_time_entry.task_id
        assert entry.start == sample_time_entry.start

    def test_read_nonexistent_time_entry(self, test_session):
        """Test reading a time entry that doesn't exist."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Attempt to read a non-existent entry
        non_existent_id = uuid4()
        entry = time_entry_crud.read(non_existent_id)

        # Verify no entry was returned
        assert entry is None

    def test_update_time_entry(self, test_session, sample_time_entry):
        """Test updating a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Update the time entry
        update_data = {
            "end": datetime.fromisoformat("2023-01-01T12:30:00"),
            "duration": 9000,  # 2.5 hours in seconds
        }
        updated_entry = time_entry_crud.update(sample_time_entry.id, update_data)

        # Verify the update
        assert updated_entry is not None
        assert updated_entry.id == sample_time_entry.id
        assert updated_entry.end.isoformat() == "2023-01-01T12:30:00"
        assert updated_entry.duration == 9000

        # Check in database
        db_entry = (
            test_session.query(TimeEntry)
            .filter(TimeEntry.id == sample_time_entry.id)
            .first()
        )
        assert db_entry.end.isoformat() == "2023-01-01T12:30:00"
        assert db_entry.duration == 9000

    def test_delete_time_entry(self, test_session, sample_time_entry):
        """Test deleting a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Delete the time entry
        time_entry_crud.delete(sample_time_entry.id)

        # Verify the entry was deleted
        db_entry = (
            test_session.query(TimeEntry)
            .filter(TimeEntry.id == sample_time_entry.id)
            .first()
        )
        assert db_entry is None

    def test_list_time_entries(self, test_session, sample_task):
        """Test listing time entries for a node."""
        # Create multiple time entries for the task
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

        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # List all time entries for the task
        task_entries = time_entry_crud.list(node_id=sample_task.id)

        # Verify we got all entries for the task
        assert len(task_entries) == 3

        # Check if entries are sorted by start_time
        for i in range(len(task_entries) - 1):
            assert task_entries[i].start <= task_entries[i + 1].start

    def test_read_time_entry(self, test_session, sample_time_entry):
        """Test reading a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Read the time entry
        entry = time_entry_crud.read(sample_time_entry.id)

        # Verify the entry
        assert entry is not None
        assert entry.id == sample_time_entry.id
        assert entry.node_id == sample_time_entry.node_id
        assert entry.start_time == sample_time_entry.start_time

    def test_read_nonexistent_time_entry(self, test_session):
        """Test reading a time entry that doesn't exist."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Attempt to read a non-existent entry
        non_existent_id = uuid4()
        entry = time_entry_crud.read(non_existent_id)

        # Verify no entry was returned
        assert entry is None

    def test_update_time_entry(self, test_session, sample_time_entry):
        """Test updating a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Update the time entry
        update_data = {
            "end_time": "2023-01-01T12:30:00Z",
            "duration": 9000,  # 2.5 hours in seconds
        }
        updated_entry = time_entry_crud.update(sample_time_entry.id, update_data)

        # Verify the update
        assert updated_entry is not None
        assert updated_entry.id == sample_time_entry.id
        assert updated_entry.end_time == "2023-01-01T12:30:00Z"
        assert updated_entry.duration == 9000

        # Check in database
        db_entry = (
            test_session.query(TimeEntry)
            .filter(TimeEntry.id == sample_time_entry.id)
            .first()
        )
        assert db_entry.end_time == "2023-01-01T12:30:00Z"
        assert db_entry.duration == 9000

    def test_delete_time_entry(self, test_session, sample_time_entry):
        """Test deleting a time entry."""
        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # Delete the time entry
        time_entry_crud.delete(sample_time_entry.id)

        # Verify the entry was deleted
        db_entry = (
            test_session.query(TimeEntry)
            .filter(TimeEntry.id == sample_time_entry.id)
            .first()
        )
        assert db_entry is None

    def test_list_time_entries(self, test_session, sample_task):
        """Test listing time entries for a node."""
        # Create multiple time entries for the task
        entries = []
        for i in range(3):
            entry = TimeEntry(
                node_id=sample_task.id,
                start_time=f"2023-01-0{i + 1}T10:00:00Z",
                end_time=f"2023-01-0{i + 1}T11:00:00Z",
                duration=3600,
            )
            test_session.add(entry)
            entries.append(entry)

        test_session.commit()

        # Initialize TimeEntryCrud
        time_entry_crud = TimeEntryCrud(db=test_session)

        # List all time entries for the task
        task_entries = time_entry_crud.list(node_id=sample_task.id)

        # Verify we got all entries for the task
        assert len(task_entries) == 3

        # Check if entries are sorted by start_time
        for i in range(len(task_entries) - 1):
            assert task_entries[i].start_time <= task_entries[i + 1].start_time
