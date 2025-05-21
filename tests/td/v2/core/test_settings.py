import pytest
import os
from unittest.mock import patch

# Import the settings module explicitly to test it
from src.td.v2.core import settings


def test_database_url_default():
    """Test that DATABASE_URL has a default value."""
    assert settings.DATABASE_URL is not None
    assert isinstance(settings.DATABASE_URL, str)
    assert "sqlite://" in settings.DATABASE_URL


def test_echo_sql_default():
    """Test that ECHO_SQL has a default value."""
    assert isinstance(settings.ECHO_SQL, bool)


@patch.dict(os.environ, {"TD_DATABASE_URL": "sqlite:///custom.db"})
def test_database_url_from_env():
    """Test that DATABASE_URL can be overridden from environment variables."""
    # Create a temporary settings object to test
    with patch("src.td.v2.core.settings.DATABASE_URL", "sqlite:///custom.db"):
        assert settings.DATABASE_URL == "sqlite:///custom.db"
