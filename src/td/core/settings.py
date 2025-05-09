# src/td/core/settings.py
from pathlib import Path

# For SQLite, you can use a file-based database or an in-memory database.
# File-based:
DB_DIR = Path.home() / ".todo"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_DIR / 'td.db'}"

# In-memory (useful for testing, data is lost when app stops):
# DATABASE_URL = "sqlite:///:memory:"

# Set to True to see all SQL statements executed by SQLAlchemy (SQLModel's backend)
# Useful for debugging, but can be verbose.
ECHO_SQL = True  # Or False for less verbose output, especially in production
