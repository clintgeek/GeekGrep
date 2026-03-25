"""Document loaders for PDF, Markdown, and text files."""

import os
from pathlib import Path
from datetime import datetime
from typing import List

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document


def load_documents(directory_path: str) -> List[Document]:
    """
    Load all PDF, Markdown, and text files from a directory recursively.
    
    Args:
        directory_path: Path to the directory containing documents
        
    Returns:
        List of LangChain Document objects with metadata
    """
    documents = []
    directory = Path(directory_path)
    
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory_path}")
    
    # Find all supported file types
    pdf_files = list(directory.rglob("*.pdf"))
    md_files = list(directory.rglob("*.md"))
    txt_files = list(directory.rglob("*.txt"))
    
    # Load PDFs
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            for doc in docs:
                doc.metadata["file_type"] = "pdf"
                doc.metadata["source"] = str(pdf_file)
                doc.metadata["modified_date"] = datetime.fromtimestamp(
                    os.path.getmtime(pdf_file)
                ).isoformat()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading PDF {pdf_file}: {e}")
    
    # Load Markdown files
    for md_file in md_files:
        try:
            loader = UnstructuredMarkdownLoader(str(md_file))
            docs = loader.load()
            for doc in docs:
                doc.metadata["file_type"] = "md"
                doc.metadata["source"] = str(md_file)
                doc.metadata["modified_date"] = datetime.fromtimestamp(
                    os.path.getmtime(md_file)
                ).isoformat()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading Markdown {md_file}: {e}")
    
    # Load text files
    for txt_file in txt_files:
        try:
            loader = TextLoader(str(txt_file))
            docs = loader.load()
            for doc in docs:
                doc.metadata["file_type"] = "txt"
                doc.metadata["source"] = str(txt_file)
                doc.metadata["modified_date"] = datetime.fromtimestamp(
                    os.path.getmtime(txt_file)
                ).isoformat()
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading text file {txt_file}: {e}")
    
    return documents
