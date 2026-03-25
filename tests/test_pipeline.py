"""Tests for the RAG pipeline."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.pipeline import ingest, query, get_store_info


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with sample documents."""
    tmpdir = tempfile.mkdtemp()
    
    # Create sample files
    txt_file = Path(tmpdir) / "sample.txt"
    txt_file.write_text("This is a sample document about Python.\nPython is a programming language.")
    
    md_file = Path(tmpdir) / "readme.md"
    md_file.write_text("# README\n\nThis is a markdown document.\n\n## Section\n\nWith content about Python.")
    
    yield tmpdir
    
    # Cleanup
    if Path(tmpdir).exists():
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def temp_store_dir():
    """Create a temporary directory for the vector store."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    if Path(tmpdir).exists():
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_ingest_returns_dict(temp_docs_dir, temp_store_dir):
    """Test that ingest returns a dictionary."""
    result = ingest(temp_docs_dir, temp_store_dir)
    assert isinstance(result, dict)
    assert "status" in result


def test_ingest_nonexistent_directory(temp_store_dir):
    """Test ingest with nonexistent directory."""
    result = ingest("/nonexistent/directory", temp_store_dir)
    assert result["status"] == "error"


def test_ingest_empty_directory(temp_store_dir):
    """Test ingest with empty directory."""
    empty_dir = tempfile.mkdtemp()
    try:
        result = ingest(empty_dir, temp_store_dir)
        assert result["status"] == "error"
        assert result["documents_loaded"] == 0
    finally:
        shutil.rmtree(empty_dir, ignore_errors=True)


@patch("src.pipeline.add_documents")
def test_ingest_success(mock_add_docs, temp_docs_dir, temp_store_dir):
    """Test successful ingestion."""
    result = ingest(temp_docs_dir, temp_store_dir)
    assert result["status"] == "success"
    assert result["documents_loaded"] > 0
    assert result["chunks_created"] > 0
    assert mock_add_docs.called


def test_query_returns_dict(temp_store_dir):
    """Test that query returns a dictionary."""
    with patch("src.pipeline.retrieve_documents", return_value=[]):
        result = query("test question", temp_store_dir)
        assert isinstance(result, dict)
        assert "status" in result
        assert "answer" in result


def test_query_no_results(temp_store_dir):
    """Test query with no results."""
    with patch("src.pipeline.retrieve_documents", return_value=[]):
        result = query("test question", temp_store_dir)
        assert result["status"] == "error"
        assert result["retrieved_count"] == 0


def test_query_with_results(temp_store_dir):
    """Test query with results."""
    from langchain_core.documents import Document
    
    mock_docs = [
        Document(
            page_content="Python is a programming language.",
            metadata={"source": "test.txt", "chunk_index": 0, "file_type": "txt"}
        )
    ]
    
    with patch("src.pipeline.retrieve_documents", return_value=mock_docs):
        with patch("src.pipeline.generate_answer", return_value="Python is a programming language."):
            result = query("What is Python?", temp_store_dir)
            assert result["status"] == "success"
            assert "answer" in result
            assert len(result["sources"]) > 0


def test_query_extracts_sources(temp_store_dir):
    """Test that query properly extracts source information."""
    from langchain_core.documents import Document
    
    mock_docs = [
        Document(
            page_content="Content 1",
            metadata={"source": "file1.txt", "chunk_index": 0, "file_type": "txt"}
        ),
        Document(
            page_content="Content 2",
            metadata={"source": "file2.txt", "chunk_index": 1, "file_type": "md"}
        )
    ]
    
    with patch("src.pipeline.retrieve_documents", return_value=mock_docs):
        with patch("src.pipeline.generate_answer", return_value="Answer"):
            result = query("Question?", temp_store_dir)
            assert len(result["sources"]) == 2
            assert result["sources"][0]["filename"] == "file1.txt"
            assert result["sources"][1]["filename"] == "file2.txt"


def test_get_store_info_returns_dict(temp_store_dir):
    """Test that get_store_info returns a dictionary."""
    result = get_store_info(temp_store_dir)
    assert isinstance(result, dict)
    assert "status" in result
