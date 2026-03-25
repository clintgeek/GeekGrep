"""Tests for retriever."""

import pytest
from langchain_core.documents import Document
from src.retrieval.retriever import retrieve_documents, format_retrieved_context


@pytest.fixture
def sample_documents():
    """Create sample documents for retrieval testing."""
    return [
        Document(
            page_content="Python is a high-level programming language.",
            metadata={"source": "python.txt", "chunk_index": 0, "file_type": "txt"}
        ),
        Document(
            page_content="It is widely used for data science and machine learning.",
            metadata={"source": "python.txt", "chunk_index": 1, "file_type": "txt"}
        ),
        Document(
            page_content="JavaScript is used for web development.",
            metadata={"source": "javascript.txt", "chunk_index": 0, "file_type": "txt"}
        ),
    ]


def test_format_retrieved_context_empty():
    """Test formatting empty document list."""
    result = format_retrieved_context([])
    assert "No relevant documents found" in result


def test_format_retrieved_context_single_document(sample_documents):
    """Test formatting a single document."""
    result = format_retrieved_context([sample_documents[0]])
    assert "python.txt" in result
    assert "Python is a high-level" in result
    assert "Source 1:" in result


def test_format_retrieved_context_multiple_documents(sample_documents):
    """Test formatting multiple documents."""
    result = format_retrieved_context(sample_documents[:2])
    assert "python.txt" in result
    assert "Source 1:" in result
    assert "Source 2:" in result
    assert sample_documents[0].page_content in result
    assert sample_documents[1].page_content in result


def test_format_retrieved_context_includes_chunk_index(sample_documents):
    """Test that chunk indices are included in formatted context."""
    result = format_retrieved_context([sample_documents[0]])
    assert "chunk 0" in result


def test_format_retrieved_context_includes_source(sample_documents):
    """Test that source filenames are included in formatted context."""
    result = format_retrieved_context(sample_documents)
    assert "python.txt" in result
    assert "javascript.txt" in result
