import pytest
from sqlmodel import SQLModel, Session, create_engine
from datetime import datetime, timedelta, timezone

from td.models import Task, TaskCreate
from td.models import TimeEntryCreate
from td.crud.task import create_task_in_db
from td.crud.time_entry import create_time_entry_in_db, calculate_total_time_for_task

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_calculate_total_time_active_entry(session: Session):
    task = create_task_in_db(session, TaskCreate(title="task"))
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    time_entry = TimeEntryCreate(task_id=task.id, start_time=start)
    create_time_entry_in_db(session, time_entry)
    total = calculate_total_time_for_task(session, task.id)
    assert total > 3590
    assert total <= 3605
