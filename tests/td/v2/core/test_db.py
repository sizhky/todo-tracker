import pytest
import os
from sqlmodel import Session, SQLModel

from src.td.v2.core.db import create_db_and_tables, get_session
from src.td.v2.models.nodes import Node, NodeType


def test_create_db_and_tables(test_engine, monkeypatch):
    """Test that the create_db_and_tables function creates the tables correctly."""
    # Mock the engine to use our test engine
    monkeypatch.setattr("src.td.v2.core.db.engine", test_engine)

    # Call the function that creates tables
    create_db_and_tables()

    # Verify that tables exist by attempting to create and query data
    with Session(test_engine) as session:
        # Create a test node
        node = Node(title="Test DB Node", type=NodeType.sector)
        session.add(node)
        session.commit()

        # Query the node
        retrieved_node = (
            session.query(Node).filter(Node.title == "Test DB Node").first()
        )

        # Verify the node was created
        assert retrieved_node is not None
        assert retrieved_node.title == "Test DB Node"
        assert retrieved_node.type == NodeType.sector


def test_get_session_yields_session(test_engine, monkeypatch):
    """Test that get_session yields a session that can be used."""
    # Mock the engine to use our test engine
    monkeypatch.setattr("src.td.v2.core.db.engine", test_engine)

    # Create tables first
    SQLModel.metadata.create_all(test_engine)

    # Get a session using the generator function
    session_generator = get_session()
    session = next(session_generator)

    # Test that we can use the session
    try:
        # Create a test node
        node = Node(title="Session Test Node", type=NodeType.sector)
        session.add(node)
        session.commit()

        # Query the node
        retrieved_node = (
            session.query(Node).filter(Node.title == "Session Test Node").first()
        )

        # Verify the node was created
        assert retrieved_node is not None
        assert retrieved_node.title == "Session Test Node"
    finally:
        # Close the session by calling next on generator (will raise StopIteration)
        try:
            next(session_generator)
        except StopIteration:
            pass
