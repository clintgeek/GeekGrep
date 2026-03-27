"""Tests for document loaders."""

import pytest
import tempfile
from pathlib import Path
from src.ingestion.loaders import load_documents


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with sample documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample text file
        txt_file = Path(tmpdir) / "sample.txt"
        txt_file.write_text("This is a sample text document.\nIt has multiple lines.\nFor testing purposes.")
        
        # Create a sample markdown file
        md_file = Path(tmpdir) / "sample.md"
        md_file.write_text("# Sample Markdown\n\nThis is a markdown document.\n\n## Section\n\nWith content.")
        
        yield tmpdir


def test_load_documents_returns_list(temp_docs_dir):
    """Test that load_documents returns a list."""
    docs = load_documents(temp_docs_dir)
    assert isinstance(docs, list)


def test_load_documents_finds_files(temp_docs_dir):
    """Test that load_documents finds and loads files."""
    docs = load_documents(temp_docs_dir)
    assert len(docs) > 0


def test_documents_have_page_content(temp_docs_dir):
    """Test that each document has non-empty page_content."""
    docs = load_documents(temp_docs_dir)
    for doc in docs:
        assert hasattr(doc, 'page_content')
        assert len(doc.page_content) > 0


def test_documents_have_metadata(temp_docs_dir):
    """Test that each document has required metadata."""
    docs = load_documents(temp_docs_dir)
    for doc in docs:
        assert 'source' in doc.metadata
        assert 'file_type' in doc.metadata
        assert 'modified_date' in doc.metadata


def test_load_documents_nonexistent_dir():
    """Test that load_documents raises error for nonexistent directory."""
    with pytest.raises(ValueError):
        load_documents("/nonexistent/directory")

def test_load_documents_with_corrupt_files(temp_docs_dir, caplog):
    """Test that loaders handle corrupted files gracefully by logging and continuing."""
    import logging
    
    # Create corrupt files
    bad_pdf = Path(temp_docs_dir) / "corrupt.pdf"
    bad_pdf.write_text("Not a real PDF")
    
    # The actual PyPDFLoader might throw an error when loading a broken PDF.
    
    bad_md_path = Path(temp_docs_dir) / "missing_perms.txt"
    bad_md_path.write_text("Content")
    
    def buggy_loader(*args, **kwargs):
        raise RuntimeError("Mocked Loader Error")
    
    import src.ingestion.loaders as l
    
    # Monkeypatch PyPDFLoader, UnstructuredMarkdownLoader, TextLoader to simulate errors
    # Wait, the best way to simulate exception is to actually let PyPDF fail on invalid PDF
    
    with caplog.at_level(logging.ERROR):
        docs = load_documents(temp_docs_dir)
        
    # Valid docs should still be loaded
    assert len(docs) > 0
    # There should be an error logged for the corrupt PDF
    assert any("Error loading PDF" in record.message for record in caplog.records)
