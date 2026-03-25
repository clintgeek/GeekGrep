"""Full RAG pipeline - orchestrates ingestion and querying."""

from typing import List, Optional, Dict, Any
from langchain_core.documents import Document

from src.ingestion.loaders import load_documents
from src.ingestion.splitter import split_documents
from src.embedding.store import add_documents, reset_store, get_store
from src.retrieval.retriever import retrieve_documents, format_retrieved_context
from src.generation.llm import generate_answer


def ingest(
    directory_path: str,
    persist_directory: str = "./data/chroma_db",
    reset: bool = False
) -> Dict[str, Any]:
    """
    Ingest documents from a directory into the vector store.
    
    Args:
        directory_path: Path to directory containing documents
        persist_directory: Path where vector store will be saved
        reset: If True, clear existing vector store before ingesting
        
    Returns:
        Dictionary with ingestion statistics
    """
    try:
        if reset:
            reset_store(persist_directory)
        
        # Load documents
        documents = load_documents(directory_path)
        if not documents:
            return {
                "status": "error",
                "message": "No documents found in directory",
                "documents_loaded": 0,
                "chunks_created": 0
            }
        
        # Split documents
        chunks = split_documents(documents)
        
        # Add to vector store
        add_documents(chunks, persist_directory)
        
        return {
            "status": "success",
            "documents_loaded": len(documents),
            "chunks_created": len(chunks),
            "message": f"Successfully ingested {len(documents)} documents into {len(chunks)} chunks"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "documents_loaded": 0,
            "chunks_created": 0
        }


def query(
    question: str,
    persist_directory: str = "./data/chroma_db",
    k: int = 4,
    file_type: Optional[str] = None,
    modified_after: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query the vector store and generate an answer.
    
    Args:
        question: The user's question
        persist_directory: Path to the vector store
        k: Number of chunks to retrieve
        file_type: Optional filter by file type (pdf, md, txt)
        modified_after: Optional filter by modification date (ISO format)
        
    Returns:
        Dictionary with answer and metadata
    """
    # Retrieve relevant documents
    retrieved_docs = retrieve_documents(
        question,
        k=k,
        persist_directory=persist_directory,
        file_type=file_type,
        modified_after=modified_after
    )
    
    if not retrieved_docs:
        return {
            "status": "error",
            "answer": "No relevant documents found for your query.",
            "sources": [],
            "retrieved_count": 0
        }
    
    # Generate answer
    answer = generate_answer(question, retrieved_docs)
    
    # Extract sources
    sources = []
    for doc in retrieved_docs:
        source_info = {
            "filename": doc.metadata.get("source", "Unknown"),
            "chunk_index": doc.metadata.get("chunk_index", "?"),
            "file_type": doc.metadata.get("file_type", "unknown")
        }
        if source_info not in sources:
            sources.append(source_info)
    
    return {
        "status": "success",
        "answer": answer,
        "sources": sources,
        "retrieved_count": len(retrieved_docs),
        "question": question
    }


def get_store_info(persist_directory: str = "./data/chroma_db") -> Dict[str, Any]:
    """
    Get information about the current vector store.
    
    Args:
        persist_directory: Path to the vector store
        
    Returns:
        Dictionary with store information
    """
    try:
        store = get_store(persist_directory)
        count = store._collection.count()
        return {
            "status": "success",
            "document_count": count,
            "persist_directory": persist_directory
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
