"""Tests for vector store."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from langchain_core.documents import Document
from src.embedding.store import get_store, add_documents, reset_store, get_embeddings, _store


@pytest.fixture
def temp_store_dir():
    """Create a temporary directory for the vector store."""
    tmpdir = tempfile.mkdtemp()
    # Ensure proper permissions
    os.chmod(tmpdir, 0o755)
    yield tmpdir
    # Cleanup
    if Path(tmpdir).exists():
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_chunks():
    """Create sample document chunks."""
    return [
        Document(
            page_content="Python is a programming language.",
            metadata={"source": "python.txt", "chunk_index": 0}
        ),
        Document(
            page_content="It is widely used for data science and machine learning.",
            metadata={"source": "python.txt", "chunk_index": 1}
        ),
        Document(
            page_content="JavaScript is used for web development.",
            metadata={"source": "javascript.txt", "chunk_index": 0}
        ),
    ]


def test_get_embeddings():
    """Test that embeddings can be initialized."""
    embeddings = get_embeddings()
    assert embeddings is not None


def test_get_store_creates_instance(temp_store_dir):
    """Test that get_store creates a store instance."""
    store = get_store(temp_store_dir)
    assert store is not None


def test_add_documents_handles_empty_list(temp_store_dir):
    """Test handling of empty documents list."""
    # Should not raise an error
    add_documents([], temp_store_dir)
    assert True


def test_store_initialization(temp_store_dir):
    """Test that store can be initialized."""
    store = get_store(temp_store_dir)
    assert store is not None
    assert hasattr(store, 'similarity_search')
