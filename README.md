# geekGrep

**Intelligent Document Query System** - A production-ready local RAG pipeline for semantic document search and AI-powered question answering.

## Quick Start

### 1. Setup

```bash
# Clone and enter directory
git clone <repo> geekGrep
cd geekGrep

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Ingest Documents

```bash
# Via CLI
python -m src.ui.cli ingest-docs ./documents

# Via Python
from src.pipeline import ingest
ingest("./documents")
```

### 3. Query Documents

```bash
# Via CLI
python -m src.ui.cli ask "What is Python?"

# Via Web UI
streamlit run src/ui/web.py

# Via Python
from src.pipeline import query
result = query("What is Python?")
print(result["answer"])
```

## Features

- 📄 **Multi-format Support**: PDF, Markdown, and text files
- 🔍 **Semantic Search**: Intelligent document retrieval using embeddings
- 🤖 **Flexible LLM Backend**: OpenAI (default) or local Ollama
- 💬 **Source Citation**: Every answer includes exact document references
- 🎯 **Metadata Filtering**: Filter by file type and modification date
- ⚡ **Async Processing**: Non-blocking document ingestion
- 🐳 **Docker Ready**: One-command deployment
- 🧪 **Fully Tested**: 44+ unit tests with 100% coverage of core modules

## Architecture

```
Documents → Loader → Splitter → Embeddings → Vector Store
                                                    ↓
                                            Similarity Search
                                                    ↓
Query → Embedding → Retrieval → Context → LLM → Answer + Citations
```

## Configuration

Set these environment variables in `.env`:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
GEEKGREP_LLM_BACKEND=openai          # or 'ollama'
GEEKGREP_MODEL=gpt-4o-mini           # or 'mistral' for ollama
GEEKGREP_DATA_DIR=./data
GEEKGREP_DOCUMENTS_DIR=./documents
```

## CLI Commands

```bash
# Ingest documents
python -m src.ui.cli ingest-docs <directory> [--persist-dir <path>] [--reset]

# Ask a question
python -m src.ui.cli ask "<question>" [--top-k 4] [--backend openai] [--model gpt-4o-mini]

# Show store info
python -m src.ui.cli info [--persist-dir <path>]
```

## Web Interface

```bash
streamlit run src/ui/web.py
```

Then open http://localhost:8501 in your browser.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_pipeline.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

## Project Structure

```
geekGrep/
├── src/
│   ├── ingestion/      # Document loading and chunking
│   ├── embedding/      # Vector store management
│   ├── retrieval/      # Document retrieval
│   ├── generation/     # LLM integration
│   ├── ui/             # CLI and web interfaces
│   └── pipeline.py     # Main RAG orchestration
├── tests/              # Unit tests (44+ tests)
├── DOCS/               # Documentation
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Orchestration | LangChain |
| Embeddings | HuggingFace (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| LLM | OpenAI API / Ollama |
| Web UI | Streamlit |
| CLI | Typer |
| Testing | Pytest |

## Performance

- **Ingestion**: ~100 documents/minute (depends on document size)
- **Query**: ~1-2 seconds with OpenAI, ~5-10 seconds with Ollama (CPU)
- **Storage**: ~1KB per chunk in vector store

## Troubleshooting

### "OPENAI_API_KEY not set"
Make sure you've created a `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add your key
```

### "No documents found"
Ensure your documents directory contains `.pdf`, `.md`, or `.txt` files.

### "Database error: readonly database"
This usually happens with temp directories. Use a persistent directory:
```bash
python -m src.ui.cli ingest-docs ./documents --persist-dir ./data/chroma_db
```

## License

MIT

## Contributing

Contributions welcome! Please ensure all tests pass before submitting PRs.

```bash
python -m pytest tests/ -v
```
