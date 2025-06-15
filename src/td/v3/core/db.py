__all__ = ["engine", "create_db_and_tables", "get_session", "session_scope"]
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

from .settings import DATABASE_URL, ECHO_SQL


engine = create_engine(
    DATABASE_URL, echo=ECHO_SQL, connect_args={"check_same_thread": False}
)


def create_db_and_tables():
    """
    Creates the database and all tables defined by SQLModel models.
    This function should be called once at application startup or via a CLI command.
    """
    # Import models here specifically for table creation to ensure they are registered
    # with SQLModel.metadata before create_all is called.
    # This avoids circular dependencies if models also import db components.
    from ..models import Node  # noqa: F401 - Imported for side effect of table registration

    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency provider for FastAPI to get a database session.
    Ensures the session is closed after the request is finished.
    """
    with Session(engine) as session:
        yield session


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.
    Useful for CLI commands or background tasks.
    This context manager handles begin, commit, and rollback.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
