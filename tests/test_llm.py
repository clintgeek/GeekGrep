"""Tests for LLM module."""

import pytest
import os
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from src.generation.llm import get_llm, generate_answer


def test_get_llm_openai_requires_api_key():
    """Test that OpenAI backend requires API key."""
    with patch.dict(os.environ, {"GEEKGREP_LLM_BACKEND": "openai", "OPENAI_API_KEY": ""}):
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            get_llm()


def test_get_llm_invalid_backend():
    """Test that invalid backend raises error."""
    with patch.dict(os.environ, {"GEEKGREP_LLM_BACKEND": "invalid"}):
        with pytest.raises(ValueError, match="Unknown LLM backend"):
            get_llm()


@patch("langchain_openai.ChatOpenAI")
def test_get_llm_openai_success(mock_chat_openai):
    """Test successful OpenAI LLM initialization."""
    with patch.dict(os.environ, {
        "GEEKGREP_LLM_BACKEND": "openai",
        "OPENAI_API_KEY": "test-key",
        "GEEKGREP_MODEL": "gpt-4o-mini"
    }):
        llm = get_llm()
        mock_chat_openai.assert_called_once()


@patch("langchain_community.llms.Ollama")
def test_get_llm_ollama_success(mock_ollama):
    """Test successful Ollama LLM initialization."""
    with patch.dict(os.environ, {
        "GEEKGREP_LLM_BACKEND": "ollama",
        "GEEKGREP_MODEL": "mistral"
    }):
        llm = get_llm()
        mock_ollama.assert_called_once()


def test_generate_answer_with_context():
    """Test answer generation with context documents."""
    docs = [
        Document(
            page_content="Python is a programming language.",
            metadata={"source": "python.txt", "chunk_index": 0}
        )
    ]
    
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Python is a programming language used for various purposes."
    mock_llm.invoke.return_value = mock_response
    
    with patch("src.generation.llm.get_llm", return_value=mock_llm):
        answer = generate_answer("What is Python?", docs)
        assert "Python" in answer
        assert mock_llm.invoke.called


def test_generate_answer_empty_context():
    """Test answer generation with empty context."""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "I don't have enough information to answer that."
    mock_llm.invoke.return_value = mock_response
    
    with patch("src.generation.llm.get_llm", return_value=mock_llm):
        answer = generate_answer("What is Python?", [])
        assert mock_llm.invoke.called
        # Check that "No context available" was in the prompt
        call_args = mock_llm.invoke.call_args[0][0]
        assert "No context available" in call_args


def test_generate_answer_formats_sources():
    """Test that sources are properly formatted in the prompt."""
    docs = [
        Document(
            page_content="Content 1",
            metadata={"source": "file1.txt", "chunk_index": 0}
        ),
        Document(
            page_content="Content 2",
            metadata={"source": "file2.txt", "chunk_index": 1}
        )
    ]
    
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Answer"
    mock_llm.invoke.return_value = mock_response
    
    with patch("src.generation.llm.get_llm", return_value=mock_llm):
        generate_answer("Question?", docs)
        
        # Check that sources are in the prompt
        call_args = mock_llm.invoke.call_args[0][0]
        assert "file1.txt" in call_args
        assert "file2.txt" in call_args
        assert "Source 1:" in call_args
        assert "Source 2:" in call_args
