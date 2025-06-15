from td.v3.models import NodeCreate as NC, NodeType


def test_node_create_basic_types():
    """Test basic NodeCreate type inference based on title and path."""
    # Test with only title (sector)
    assert NC(title="a").type == NodeType.sector

    # Test with title and path (area)
    assert NC(title="a", path="b").type == NodeType.area

    # Test with title and longer path (project)
    assert NC(title="a", path="b/c").type == NodeType.project


def test_node_create_validation_errors():
    """Test validation errors in NodeCreate."""
    # Test slash in title
    try:
        NC(title="a/b", path="b/c")
        assert False, "Expected error for slash in title"
    except AssertionError:
        raise
    except Exception:
        pass

    # Test missing title and path
    try:
        NC(path="")
        assert False, "Expected error for missing title and path"
    except AssertionError:
        raise
    except Exception:
        pass


def test_node_create_equivalence_cases():
    """Test equivalence cases for NodeCreate."""
    # Test path inference
    assert NC(path="a").type == NodeType.sector

    # Test equivalence between different ways of specifying the same node
    assert NC(path="a/b") == NC(title="b", path="a")
    assert NC(path="a/b/c") == NC(title="c", path="a/b")
    assert NC(path="a/b/c") == NC(title="c", path="/a/b/")
    assert NC(path="a/b/c") == NC(title="c", path="/a/b")
    assert NC(path="a/b/c") == NC(title="c", path="a/b/")

    assert NC(path="a/b/c").title == NC(title="c", path="/a/b").title
    assert NC(path="a/b/c").type == NC(title="c", path="/a/b").type
    assert NC(path="a/b/c").path == NC(title="c", path="/a/b").path

    assert NC(path="a/b/c").title == NC(title="c", path="a/b/").title
    assert NC(path="a/b/c").type == NC(title="c", path="a/b/").type
    assert NC(path="a/b/c").path == NC(title="c", path="a/b/").path
