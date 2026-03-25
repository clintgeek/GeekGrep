"""File watcher for automatic document re-ingestion."""

import os
import logging
from pathlib import Path
from typing import Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent

from src.ingestion.loaders import load_documents
from src.ingestion.splitter import split_documents
from src.embedding.store import add_documents, get_store

logger = logging.getLogger(__name__)


class DocumentEventHandler(FileSystemEventHandler):
    """Handles file system events for document changes."""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.md', '.txt'}
    
    def __init__(
        self,
        persist_directory: str = "./data/chroma_db",
        on_change: Optional[Callable] = None
    ):
        """
        Initialize the event handler.
        
        Args:
            persist_directory: Path to the vector store
            on_change: Optional callback function when files change
        """
        self.persist_directory = persist_directory
        self.on_change = on_change
    
    def _is_supported_file(self, path: str) -> bool:
        """Check if file has a supported extension."""
        return Path(path).suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle file creation."""
        if event.is_directory:
            return
        
        if not self._is_supported_file(event.src_path):
            return
        
        logger.info(f"New file detected: {event.src_path}")
        self._ingest_file(event.src_path)
    
    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification."""
        if event.is_directory:
            return
        
        if not self._is_supported_file(event.src_path):
            return
        
        logger.info(f"File modified: {event.src_path}")
        self._ingest_file(event.src_path)
    
    def on_deleted(self, event: FileDeletedEvent) -> None:
        """Handle file deletion."""
        if event.is_directory:
            return
        
        if not self._is_supported_file(event.src_path):
            return
        
        logger.info(f"File deleted: {event.src_path}")
        self._remove_file_from_store(event.src_path)
    
    def _ingest_file(self, file_path: str) -> None:
        """Ingest a single file."""
        try:
            # Load the file
            from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
            from datetime import datetime
            
            file_path_obj = Path(file_path)
            suffix = file_path_obj.suffix.lower()
            
            if suffix == '.pdf':
                loader = PyPDFLoader(file_path)
            elif suffix == '.md':
                loader = UnstructuredMarkdownLoader(file_path)
            elif suffix == '.txt':
                loader = TextLoader(file_path)
            else:
                return
            
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata["source"] = str(file_path_obj)
                doc.metadata["file_type"] = suffix[1:]  # Remove the dot
                doc.metadata["modified_date"] = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat()
            
            # Split and add to store
            chunks = split_documents(documents)
            add_documents(chunks, self.persist_directory)
            
            logger.info(f"Successfully ingested {file_path}: {len(chunks)} chunks")
            
            if self.on_change:
                self.on_change("ingested", file_path, len(chunks))
        
        except Exception as e:
            logger.error(f"Error ingesting {file_path}: {e}")
            if self.on_change:
                self.on_change("error", file_path, str(e))
    
    def _remove_file_from_store(self, file_path: str) -> None:
        """Remove all chunks from a file from the vector store."""
        try:
            store = get_store(self.persist_directory)
            
            # Delete documents with this source
            store._collection.delete(
                where={"source": str(Path(file_path))}
            )
            
            logger.info(f"Removed {file_path} from vector store")
            
            if self.on_change:
                self.on_change("deleted", file_path, 0)
        
        except Exception as e:
            logger.error(f"Error removing {file_path} from store: {e}")
            if self.on_change:
                self.on_change("error", file_path, str(e))


class DocumentWatcher:
    """Watches a directory for document changes."""
    
    def __init__(
        self,
        directory: str,
        persist_directory: str = "./data/chroma_db",
        on_change: Optional[Callable] = None
    ):
        """
        Initialize the watcher.
        
        Args:
            directory: Directory to watch
            persist_directory: Path to the vector store
            on_change: Optional callback function
        """
        self.directory = directory
        self.persist_directory = persist_directory
        self.observer = Observer()
        self.event_handler = DocumentEventHandler(persist_directory, on_change)
    
    def start(self) -> None:
        """Start watching the directory."""
        self.observer.schedule(self.event_handler, self.directory, recursive=True)
        self.observer.start()
        logger.info(f"Started watching directory: {self.directory}")
    
    def stop(self) -> None:
        """Stop watching the directory."""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching directory")
