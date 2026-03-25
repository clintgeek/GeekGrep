"""Retriever for finding relevant document chunks."""

from typing import List, Optional
from langchain_core.documents import Document
from src.embedding.store import get_store


def retrieve_documents(
    query: str,
    k: int = 4,
    persist_directory: str = "./data/chroma_db",
    file_type: Optional[str] = None,
    modified_after: Optional[str] = None
) -> List[Document]:
    """
    Retrieve the most relevant document chunks for a query.
    
    Args:
        query: The search query
        k: Number of results to return (default 4)
        persist_directory: Path to the vector store
        file_type: Optional filter by file type (pdf, md, txt)
        modified_after: Optional filter by modification date (ISO format)
        
    Returns:
        List of relevant Document objects
    """
    store = get_store(persist_directory)
    
    # Build where filter if needed
    where_filter = None
    if file_type or modified_after:
        where_filter = {}
        if file_type:
            where_filter["file_type"] = file_type
        if modified_after:
            where_filter["modified_date"] = {"$gte": modified_after}
    
    # Perform similarity search
    if where_filter:
        results = store.similarity_search(query, k=k, where=where_filter)
    else:
        results = store.similarity_search(query, k=k)
    
    return results


def format_retrieved_context(documents: List[Document]) -> str:
    """
    Format retrieved documents into a context string with citations.
    
    Args:
        documents: List of retrieved Document objects
        
    Returns:
        Formatted context string with source citations
    """
    if not documents:
        return "No relevant documents found."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        source = doc.metadata.get("source", "Unknown")
        chunk_index = doc.metadata.get("chunk_index", "?")
        content = doc.page_content
        
        context_parts.append(
            f"[Source {i}: {source}, chunk {chunk_index}]\n{content}"
        )
    
    return "\n\n".join(context_parts)
