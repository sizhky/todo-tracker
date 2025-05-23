# src/td/core/settings.py
import os
from pathlib import Path

# For SQLite, you can use a file-based database or an in-memory database.
# File-based:
DB_DIR = Path.home() / ".todo/v3/"
DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_NAME = "default.db"  # Default database name
DB_PATH = DB_DIR / DEFAULT_DB_NAME
DB_PATH.touch(exist_ok=True)  # Create the database file if it doesn't exist
# Symlink name for the active database
ACTIVE_DB_LINK_FILENAME = os.environ.get("TDDB", "active.db").removesuffix(
    ".db"
)  # Symlink name for the active database
ACTIVE_DB_LINK_FILENAME = (
    f"{ACTIVE_DB_LINK_FILENAME}.db"  # Ensure it has a .db extension
)
# Symlink path for the active database
ACTIVE_DB_LINK_PATH = DB_DIR / ACTIVE_DB_LINK_FILENAME
# Symlink to the active database
if not ACTIVE_DB_LINK_PATH.exists():
    # Create a symlink to the default database if it doesn't exist
    try:
        ACTIVE_DB_LINK_PATH.symlink_to(DB_PATH)
    except FileExistsError:
        pass  # Symlink already exists, do nothing
    except OSError as e:
        print(f"Error creating symlink: {e}")

DATABASE_URL = f"sqlite:///{ACTIVE_DB_LINK_PATH}"

# In-memory (useful for testing, data is lost when app stops):
# DATABASE_URL = "sqlite:///:memory:"

# Set to True to see all SQL statements executed by SQLAlchemy (SQLModel's backend)
# Useful for debugging, but can be verbose.
ECHO_SQL = False  # Or False for less verbose output, especially in production
