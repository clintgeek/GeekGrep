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

def test_retrieve_documents_with_filters(monkeypatch):
    """Test retrieve_documents handles file_type and modified_after filters correctly."""
    
    class MockStore:
        def __init__(self):
            self.last_query = None
            self.last_k = None
            self.last_where = None
            
        def similarity_search(self, query, k=4, where=None):
            self.last_query = query
            self.last_k = k
            self.last_where = where
            return []
            
    mock_store = MockStore()
    
    def mock_get_store(*args, **kwargs):
        return mock_store
        
    import src.retrieval.retriever as r
    monkeypatch.setattr(r, "get_store", mock_get_store)
    
    # Test without filters
    r.retrieve_documents("test query")
    assert mock_store.last_where is None
    
    # Test with file_type filter
    r.retrieve_documents("test query", file_type="pdf")
    assert mock_store.last_where == {"file_type": "pdf"}
    
    # Test with modified_after filter
    r.retrieve_documents("test query", modified_after="2023-01-01T00:00:00")
    assert mock_store.last_where == {"modified_date": {"$gte": "2023-01-01T00:00:00"}}
    
    # Test with both filters
    r.retrieve_documents("test query", file_type="md", modified_after="2023-01-01")
    assert mock_store.last_where == {"file_type": "md", "modified_date": {"$gte": "2023-01-01"}}
