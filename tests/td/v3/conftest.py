import pytest
from sqlmodel import SQLModel, Session, create_engine
from typing import Generator
import os

# Import models to make sure they're known to SQLModel
from td.v3.models import Node


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Create an in-memory SQLite database for testing.
    This fixture provides an isolated database session for each test.
    """
    # Use in-memory SQLite for tests
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create and yield a session
    with Session(engine) as session:
        yield session
