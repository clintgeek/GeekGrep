"""LLM integration for answer generation."""

import os
from typing import List
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    """
    Get the configured LLM instance based on environment variables.
    
    Returns:
        LangChain LLM instance (ChatOpenAI or Ollama)
        
    Raises:
        ValueError: If LLM backend is not configured or invalid
    """
    backend = os.getenv("GEEKGREP_LLM_BACKEND", "openai").lower()
    
    if backend == "openai":
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it in .env or environment variables."
            )
        
        model = os.getenv("GEEKGREP_MODEL", "gpt-4o-mini")
        return ChatOpenAI(model=model, api_key=api_key, temperature=0.7)
    
    elif backend == "ollama":
        from langchain_community.llms import Ollama
        
        model = os.getenv("GEEKGREP_MODEL", "mistral")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return Ollama(model=model, base_url=base_url)
    
    else:
        raise ValueError(
            f"Unknown LLM backend: {backend}. Must be 'openai' or 'ollama'."
        )


def generate_answer(question: str, context_documents: List[Document]) -> str:
    """
    Generate an answer to a question using the configured LLM.
    
    Args:
        question: The user's question
        context_documents: List of relevant Document objects for context
        
    Returns:
        The generated answer with source citations
    """
    llm = get_llm()
    
    # Format context with citations
    context_parts = []
    for i, doc in enumerate(context_documents, 1):
        source = doc.metadata.get("source", "Unknown")
        chunk_index = doc.metadata.get("chunk_index", "?")
        content = doc.page_content
        context_parts.append(f"[Source {i}: {source}, chunk {chunk_index}]\n{content}")
    
    context = "\n\n".join(context_parts) if context_parts else "No context available."
    
    # Build the prompt
    prompt = f"""You are an expert technical assistant specializing in document analysis.
Using the provided context, answer the user's question accurately and concisely.

Rules:
- Only answer using information from the context below
- Cite your sources as [filename, chunk number]
- If the answer is not in the context, say "I don't have enough information to answer that."
- Be concise and clear

Context:
{context}

Question: {question}

Answer:"""
    
    # Generate response
    response = llm.invoke(prompt)
    
    # Extract text from response (handle both string and BaseMessage types)
    if hasattr(response, 'content'):
        return response.content
    return str(response)
