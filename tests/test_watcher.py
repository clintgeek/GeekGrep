"""Tests for file watcher."""

import pytest
import tempfile
from pathlib import Path
from src.ingestion.watcher import DocumentEventHandler, DocumentWatcher


@pytest.fixture
def temp_watch_dir():
    """Create a temporary directory for watching."""
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    # Cleanup
    import shutil
    if Path(tmpdir).exists():
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_event_handler_supports_pdf():
    """Test that PDF files are recognized."""
    handler = DocumentEventHandler()
    assert handler._is_supported_file("test.pdf")


def test_event_handler_supports_markdown():
    """Test that Markdown files are recognized."""
    handler = DocumentEventHandler()
    assert handler._is_supported_file("test.md")


def test_event_handler_supports_text():
    """Test that text files are recognized."""
    handler = DocumentEventHandler()
    assert handler._is_supported_file("test.txt")


def test_event_handler_ignores_other_files():
    """Test that other file types are ignored."""
    handler = DocumentEventHandler()
    assert not handler._is_supported_file("test.doc")
    assert not handler._is_supported_file("test.py")
    assert not handler._is_supported_file("test.json")


def test_event_handler_case_insensitive():
    """Test that file extension check is case-insensitive."""
    handler = DocumentEventHandler()
    assert handler._is_supported_file("test.PDF")
    assert handler._is_supported_file("test.MD")
    assert handler._is_supported_file("test.TXT")


def test_document_watcher_initialization(temp_watch_dir):
    """Test that DocumentWatcher initializes correctly."""
    watcher = DocumentWatcher(temp_watch_dir)
    assert watcher.directory == temp_watch_dir
    assert watcher.observer is not None


def test_document_watcher_with_callback(temp_watch_dir):
    """Test that DocumentWatcher accepts a callback."""
    callback_called = []
    
    def on_change(event_type, file_path, count):
        callback_called.append((event_type, file_path, count))
    
    watcher = DocumentWatcher(temp_watch_dir, on_change=on_change)
    assert watcher.event_handler.on_change is not None
