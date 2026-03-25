"""Tests for text splitter."""

import pytest
from langchain_core.documents import Document
from src.ingestion.splitter import split_documents


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    long_text = "This is a sample document. " * 100  # ~2700 characters
    doc = Document(
        page_content=long_text,
        metadata={
            "source": "test.txt",
            "file_type": "txt",
            "modified_date": "2025-03-24"
        }
    )
    return [doc]


def test_split_documents_returns_list(sample_documents):
    """Test that split_documents returns a list."""
    chunks = split_documents(sample_documents)
    assert isinstance(chunks, list)


def test_split_documents_creates_multiple_chunks(sample_documents):
    """Test that a long document is split into multiple chunks."""
    chunks = split_documents(sample_documents)
    assert len(chunks) > 1


def test_chunk_size_respected(sample_documents):
    """Test that chunk size is respected."""
    chunk_size = 1000
    chunks = split_documents(sample_documents, chunk_size=chunk_size)
    for chunk in chunks:
        assert len(chunk.page_content) <= chunk_size + 100  # Allow some tolerance


def test_metadata_preserved(sample_documents):
    """Test that metadata is preserved in chunks."""
    chunks = split_documents(sample_documents)
    for chunk in chunks:
        assert chunk.metadata["source"] == "test.txt"
        assert chunk.metadata["file_type"] == "txt"
        assert "chunk_index" in chunk.metadata
        assert "total_chunks" in chunk.metadata


def test_chunk_index_sequential(sample_documents):
    """Test that chunk indices are sequential."""
    chunks = split_documents(sample_documents)
    indices = [chunk.metadata["chunk_index"] for chunk in chunks]
    assert indices == list(range(len(chunks)))


def test_empty_documents_list():
    """Test handling of empty documents list."""
    chunks = split_documents([])
    assert chunks == []


def test_small_document_single_chunk():
    """Test that small documents produce a single chunk."""
    doc = Document(
        page_content="This is a small document.",
        metadata={"source": "small.txt"}
    )
    chunks = split_documents([doc])
    assert len(chunks) == 1
    assert chunks[0].page_content == "This is a small document."
