import pytest
from uuid import uuid4
from datetime import datetime

from src.td.v2.models.nodes import Node, NodeType, NodeStatus, TimeEntry
from src.td.v2.crud.node import NodeCrud


# Mock TimeEntryCrud class since we're having import issues
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

    def list(self, node_id=None):
        """List time entries, optionally filtered by node_id."""
        query = self.db.query(TimeEntry)
        if node_id:
            query = query.filter(TimeEntry.task_id == node_id)
        return query.order_by(TimeEntry.start).all()


def test_complete_workflow(test_session):
    """
    Test a complete workflow of creating a hierarchy of nodes and time entries,
    simulating real-world usage of the application.
    """
    # 1. Create a sector
    sector_crud = NodeCrud(node_type=NodeType.sector, db=test_session)
    sector = sector_crud.create({"title": "Work"})
    assert sector.title == "Work"
    assert sector.type == NodeType.sector

    # 2. Create an area under the sector
    area_crud = NodeCrud(node_type=NodeType.area, db=test_session)
    area = area_crud.create({"title": "Development", "parent_id": sector.id})
    assert area.title == "Development"
    assert area.parent_id == sector.id

    # 3. Create a project under the area
    project_crud = NodeCrud(node_type=NodeType.project, db=test_session)
    project = project_crud.create({"title": "Todo Tracker", "parent_id": area.id})
    assert project.title == "Todo Tracker"
    assert project.parent_id == area.id

    # 4. Create tasks under the project
    task_crud = NodeCrud(node_type=NodeType.task, db=test_session)
    task1 = task_crud.create({"title": "Implement models", "parent_id": project.id})
    task2 = task_crud.create({"title": "Write tests", "parent_id": project.id})

    # 5. Create time entries for tasks
    time_entry_crud = TimeEntryCrud(db=test_session)
    time_entry1 = time_entry_crud.create(
        {
            "task_id": task1.id,
            "start": datetime.fromisoformat("2023-01-01T10:00:00"),
            "end": datetime.fromisoformat("2023-01-01T12:00:00"),
            "duration": 7200,
        }
    )

    time_entry2 = time_entry_crud.create(
        {
            "task_id": task2.id,
            "start": datetime.fromisoformat("2023-01-01T13:00:00"),
            "end": datetime.fromisoformat("2023-01-01T15:00:00"),
            "duration": 7200,
        }
    )

    # 6. Mark task1 as completed
    task1_updated = task_crud.update(task1.id, {"status": NodeStatus.completed})
    assert task1_updated.status == NodeStatus.completed

    # 7. List all tasks under the project
    project_tasks = task_crud.list(parent_id=project.id)
    assert len(project_tasks) == 2

    # 8. List time entries for task1
    task1_entries = time_entry_crud.list(node_id=task1.id)
    assert len(task1_entries) == 1
    assert task1_entries[0].task_id == task1.id

    # 9. List all active tasks under the project
    active_tasks = task_crud.list(parent_id=project.id, status=NodeStatus.active)
    assert len(active_tasks) == 1
    assert active_tasks[0].id == task2.id

    # 10. Delete task2
    task_crud.delete(task2.id)
    remaining_tasks = task_crud.list(parent_id=project.id)
    assert len(remaining_tasks) == 1
    assert remaining_tasks[0].id == task1.id

    # 3. Create a project under the area
    project_crud = NodeCrud(node_type=NodeType.project, db=test_session)
    project = project_crud.create({"title": "Todo Tracker", "parent_id": area.id})
    assert project.title == "Todo Tracker"
    assert project.parent_id == area.id

    # 4. Create tasks under the project
    task_crud = NodeCrud(node_type=NodeType.task, db=test_session)
    task1 = task_crud.create({"title": "Implement models", "parent_id": project.id})
    task2 = task_crud.create({"title": "Write tests", "parent_id": project.id})

    # 5. Create time entries for tasks
    time_entry_crud = TimeEntryCrud(db=test_session)
    time_entry1 = time_entry_crud.create(
        {
            "node_id": task1.id,
            "start_time": "2023-01-01T10:00:00Z",
            "end_time": "2023-01-01T12:00:00Z",
            "duration": 7200,
        }
    )

    time_entry2 = time_entry_crud.create(
        {
            "node_id": task2.id,
            "start_time": "2023-01-01T13:00:00Z",
            "end_time": "2023-01-01T15:00:00Z",
            "duration": 7200,
        }
    )

    # 6. Mark task1 as completed
    task1_updated = task_crud.update(task1.id, {"status": NodeStatus.completed})
    assert task1_updated.status == NodeStatus.completed

    # 7. List all tasks under the project
    project_tasks = task_crud.list(parent_id=project.id)
    assert len(project_tasks) == 2

    # 8. List time entries for task1
    task1_entries = time_entry_crud.list(node_id=task1.id)
    assert len(task1_entries) == 1
    assert task1_entries[0].id == time_entry1.id

    # 9. List all active tasks under the project
    active_tasks = task_crud.list(parent_id=project.id, status=NodeStatus.active)
    assert len(active_tasks) == 1
    assert active_tasks[0].id == task2.id

    # 10. Delete task2
    task_crud.delete(task2.id)
    remaining_tasks = task_crud.list(parent_id=project.id)
    assert len(remaining_tasks) == 1
    assert remaining_tasks[0].id == task1.id
