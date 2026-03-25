"""Text splitter for breaking documents into chunks."""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """
    Split documents into chunks while preserving metadata.
    
    Args:
        documents: List of Document objects to split
        chunk_size: Maximum size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of Document objects with chunks and preserved metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    split_docs = []
    
    for doc in documents:
        # Split the document
        chunks = splitter.split_text(doc.page_content)
        
        # Create new documents for each chunk, preserving metadata
        for chunk_index, chunk in enumerate(chunks):
            new_doc = Document(
                page_content=chunk,
                metadata={
                    **doc.metadata,
                    "chunk_index": chunk_index,
                    "total_chunks": len(chunks)
                }
            )
            split_docs.append(new_doc)
    
    return split_docs
