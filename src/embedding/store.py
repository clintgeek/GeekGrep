"""Vector store initialization and management using ChromaDB."""

import os
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# Global store instance
_store = None


def get_embeddings():
    """Get or create the embeddings model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def get_store(persist_directory: str = "./data/chroma_db") -> Chroma:
    """
    Get or initialize the vector store.
    
    Args:
        persist_directory: Path where ChromaDB will persist data
        
    Returns:
        Chroma vector store instance
    """
    global _store
    
    if _store is None:
        os.makedirs(persist_directory, exist_ok=True)
        embeddings = get_embeddings()
        _store = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name="documents",
            collection_metadata={"hnsw:space": "cosine"}
        )
    
    return _store


def add_documents(chunks: List[Document], persist_directory: str = "./data/chroma_db") -> None:
    """
    Add document chunks to the vector store.
    
    Args:
        chunks: List of Document objects to add
        persist_directory: Path where ChromaDB will persist data
    """
    if not chunks:
        return
    
    store = get_store(persist_directory)
    store.add_documents(chunks)


def reset_store(persist_directory: str = "./data/chroma_db") -> None:
    """
    Reset the vector store (clear all documents).
    
    Args:
        persist_directory: Path where ChromaDB data is stored
    """
    global _store
    
    # Delete the directory
    import shutil
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    
    # Reset the global instance
    _store = None
