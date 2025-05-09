from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager

from .settings import DATABASE_URL, ECHO_SQL
# Import your models here.
# This is a placeholder, adjust the import path if your models are elsewhere
# or if you have a central place where all models are imported (e.g., models.__init__.py)
# For now, assuming they are directly accessible for the create_db_and_tables function.
# We will need to import them specifically in create_db_and_tables or ensure they are
# part of SQLModel.metadata when it's called.

# The engine is the entry point to the database.
# `echo=True` will log all SQL statements. Set to False in production.
# `connect_args` is specific to SQLite to allow the connection to be shared across threads.
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
    from ..models import Task, Project, Area  # noqa: F401 - Imported for side effect of table registration

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


# Example of how you might ensure all models are loaded if not directly imported
# in create_db_and_tables. This is usually not needed if you import them as above.
# def _load_all_models():
#     from ..models import task # Assuming task.py contains all model definitions
# _load_all_models()
