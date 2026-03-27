import pytest

@pytest.fixture(autouse=True)
def reset_global_store():
    """Ensure the global vector store is reset before and after every test."""
    import src.embedding.store as s
    s._store = None
    yield
    s._store = None
