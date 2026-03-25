# geekGrep: Step-by-Step Build Guide

> Each step is self-contained with clear inputs, outputs, and a "done when" checklist. Complete them in order. If you get stuck on a step for more than 30 minutes, flag it and move on.

---

## Step 1: Install Prerequisites

**Goal**: Get the required tools installed on your machine.

**Do this**:
1. Install Python 3.11+ — verify with `python --version`
2. Get an OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
3. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-key-here
   GEEKGREP_LLM_BACKEND=openai
   GEEKGREP_MODEL=gpt-4o-mini
   ```
4. **(Optional)** Install [Ollama](https://ollama.com/download) if you want local/offline fallback:
   - `ollama pull mistral`
   - To use it, set `GEEKGREP_LLM_BACKEND=ollama` in `.env`

**Done when**:
- [ ] `python --version` prints 3.11 or higher
- [ ] `.env` file exists with your `OPENAI_API_KEY`
- [ ] (Optional) `ollama list` shows `mistral`

---

## Step 2: Create Project Structure

**Goal**: Set up the folder layout and virtual environment.

**Do this**:
```bash
cd geekGrep
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

mkdir -p src/ingestion src/embedding src/retrieval src/generation src/ui
mkdir -p tests test_docs
touch src/__init__.py src/ingestion/__init__.py src/embedding/__init__.py
touch src/retrieval/__init__.py src/generation/__init__.py src/ui/__init__.py
```

Create `requirements.txt` with these exact contents:
```
langchain>=0.2.0
langchain-community>=0.2.0
langchain-openai>=0.1.0
langchain-huggingface>=0.0.3
chromadb>=0.5.0
openai>=1.30.0
sentence-transformers>=3.0.0
streamlit>=1.35.0
typer>=0.12.0
pypdf>=4.0.0
unstructured>=0.14.0
watchdog>=4.0.0
rich>=13.0.0
python-dotenv>=1.0.0
# Optional: for local LLM fallback
# ollama>=0.2.0
```

Then install: `pip install -r requirements.txt`

**Done when**:
- [ ] `pip list | grep langchain` shows the package
- [ ] `pip list | grep chromadb` shows the package
- [ ] Folder structure matches the layout above

---

## Step 3: Build the Document Loaders

**Goal**: Write code that reads `.pdf`, `.md`, and `.txt` files from a directory and returns their text content.

**File**: `src/ingestion/loaders.py`

**What it does**:
- Takes a directory path as input
- Finds all `.pdf`, `.md`, and `.txt` files in that directory (recursively)
- Uses `langchain_community.document_loaders` — `PyPDFLoader` for PDFs, `TextLoader` for `.txt`, `UnstructuredMarkdownLoader` for `.md`
- Returns a list of LangChain `Document` objects (each has `.page_content` and `.metadata`)
- The `.metadata` must include `source` (file path), `file_type`, and `modified_date`

**Test it**:
1. Drop 2-3 sample files (a PDF, a markdown file, a text file) into `test_docs/`
2. Write `tests/test_loaders.py` that calls your loader and asserts:
   - Correct number of documents returned
   - Each document has `page_content` that is not empty
   - Each document has `source` in metadata

**Done when**:
- [ ] `python -m pytest tests/test_loaders.py` passes
- [ ] All three file types load successfully

---

## Step 4: Build the Text Splitter

**Goal**: Break loaded documents into smaller chunks suitable for embedding.

**File**: `src/ingestion/splitter.py`

**What it does**:
- Takes a list of `Document` objects from Step 3
- Uses `langchain.text_splitter.RecursiveCharacterTextSplitter`
- Config: `chunk_size=1000`, `chunk_overlap=200`
- Preserves the original metadata on each chunk (source file, page number)
- Adds `chunk_index` to metadata so we can trace back to position in original doc

**Test it**:
Write `tests/test_splitter.py` that:
- Feeds in a known document with 3000+ characters
- Asserts output has multiple chunks
- Asserts each chunk is ≤ 1000 characters
- Asserts metadata carries through

**Done when**:
- [ ] `python -m pytest tests/test_splitter.py` passes
- [ ] A 3000-char document produces 3+ chunks with metadata intact

---

## Step 5: Set Up the Vector Store

**Goal**: Store document chunks as embeddings in ChromaDB.

**File**: `src/embedding/store.py`

**What it does**:
- Initializes a persistent ChromaDB collection at `./data/chroma_db`
- Uses `langchain_huggingface.HuggingFaceEmbeddings` with model `all-MiniLM-L6-v2`
- Provides two functions:
  - `add_documents(chunks)` — embeds and stores a list of chunks
  - `get_store()` — returns the initialized vector store for querying
- The first time you run embedding it will download the model (~80MB) — this is normal

**Test it**:
Write `tests/test_store.py` that:
- Creates a few fake `Document` objects with known content
- Calls `add_documents()`
- Queries the store with a related string
- Asserts the correct document comes back as most similar

**Done when**:
- [ ] `python -m pytest tests/test_store.py` passes
- [ ] `./data/chroma_db` directory exists with data files after running
- [ ] Similarity search returns relevant results

---

## Step 6: Build the Retriever

**Goal**: Given a user question, find the most relevant chunks from the vector store.

**File**: `src/retrieval/retriever.py`

**What it does**:
- Wraps the ChromaDB store from Step 5
- Takes a query string and returns the top `k` most similar chunks (default `k=4`)
- Each result includes the chunk text AND its metadata (source file, page, chunk index)
- Uses cosine similarity (ChromaDB default)

**Test it**:
Write `tests/test_retriever.py` that:
- Ingests a few test documents through Steps 3-5
- Queries with a question clearly related to one document
- Asserts that document appears in the top results

**Done when**:
- [ ] `python -m pytest tests/test_retriever.py` passes
- [ ] Asking a question about a specific doc returns that doc in results

---

## Step 7: Connect the LLM

**Goal**: Send a prompt to an LLM and get a response. Supports OpenAI (default) and Ollama (fallback).

**File**: `src/generation/llm.py`

**What it does**:
- Reads `GEEKGREP_LLM_BACKEND` from `.env` (values: `openai` or `ollama`, default: `openai`)
- Reads `GEEKGREP_MODEL` from `.env` (default: `gpt-4o-mini` for OpenAI, `mistral` for Ollama)
- If backend is `openai`: uses `langchain_openai.ChatOpenAI` with the `OPENAI_API_KEY` from `.env`
- If backend is `ollama`: uses `langchain_community.llms.Ollama` to connect to local server
- Provides a function `get_llm()` that returns the configured LLM instance
- Provides a function `generate_answer(question, context_chunks)` that:
  1. Formats the context chunks into a single context string with source citations
  2. Fills in the prompt template (see below)
  3. Sends to the LLM via `get_llm()`
  4. Returns the response text

**Prompt template**:
```
You are an expert technical assistant specializing in document analysis.
Using the provided context, answer the user's question accurately and concisely.

Rules:
- Only answer using information from the context below
- Cite your sources as [filename, page/chunk]
- If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:
```

**Test it manually**:
```python
python -c "from src.generation.llm import generate_answer; print(generate_answer('What is Python?', [{'text': 'Python is a programming language.', 'source': 'test.md'}]))"
```

**Done when**:
- [ ] With `GEEKGREP_LLM_BACKEND=openai`: returns a coherent answer (fast, ~1-2s)
- [ ] With `GEEKGREP_LLM_BACKEND=ollama`: returns a coherent answer (slower, requires Ollama running)
- [ ] When context doesn't contain the answer, it says so

---

## Step 8: Wire Up the Full RAG Pipeline

**Goal**: Connect all the pieces into one function: question in → answer out.

**File**: `src/pipeline.py`

**What it does**:
- Imports from Steps 3-7
- Provides two main functions:
  - `ingest(directory_path)` — loads, splits, embeds all docs from a directory
  - `query(question, k=4)` — retrieves relevant chunks, passes to LLM, returns formatted answer with citations
- The `query` response should include:
  - The answer text
  - A list of sources used (filename + chunk location)

**Test it manually**:
1. Put some docs in `test_docs/`
2. Run `python -c "from src.pipeline import ingest; ingest('./test_docs')"`
3. Run `python -c "from src.pipeline import query; print(query('your question here'))"`

**Done when**:
- [ ] `ingest()` processes files without errors
- [ ] `query()` returns an answer with source citations
- [ ] End-to-end: ingest docs → ask question → get relevant answer

---

## Step 9: Build the CLI

**Goal**: Create a command-line interface so users don't have to write Python.

**File**: `src/ui/cli.py`

**What it does**:
- Uses `typer` to create two commands:
  - `geekgrep ingest <directory>` — runs the ingestion pipeline, shows progress with `rich`
  - `geekgrep query "<question>"` — runs the query pipeline, prints formatted answer
- Add `--backend` flag to switch between `openai` and `ollama`
- Add `--model` flag to override the default LLM model
- Add `--top-k` flag to control number of retrieved chunks
- Print source citations in a clean format beneath the answer

**Test it from terminal**:
```bash
python -m src.ui.cli ingest ./test_docs
python -m src.ui.cli query "What is in these documents?"
```

**Done when**:
- [ ] Both commands run without errors
- [ ] `ingest` shows progress feedback
- [ ] `query` prints a formatted answer with citations

---

## Step 10: Build the Web Interface

**Goal**: Create a simple Streamlit web UI.

**File**: `src/ui/web.py`

**What it does**:
- Sidebar with:
  - Directory path input for ingestion
  - "Ingest Documents" button
  - Backend toggle (OpenAI / Ollama)
  - Model selection dropdown (updates based on backend)
  - Top-k slider (1-10, default 4)
- Main area with:
  - Text input for questions
  - "Ask" button
  - Answer display area
  - Expandable "Sources" section showing which documents were used
- Show a spinner during ingestion and query processing
- Display error messages clearly if something fails (e.g., missing API key, Ollama not running)

**Run it**:
```bash
streamlit run src/ui/web.py
```

**Done when**:
- [ ] Web UI loads at `localhost:8501`
- [ ] Can ingest documents via the sidebar
- [ ] Can ask questions and get answers with citations
- [ ] Errors display clearly (try with a bad API key or Ollama stopped)

---

## Step 11: Add File Watching

**Goal**: Automatically re-ingest when files change in the watched directory.

**File**: `src/ingestion/watcher.py`

**What it does**:
- Uses the `watchdog` library to monitor a directory
- On file created/modified/deleted events for `.pdf`, `.md`, `.txt`:
  - Log the event
  - Re-run ingestion for that specific file (not the whole directory)
- For deletions, remove that file's chunks from the vector store
- Runs as a background thread so it doesn't block the CLI or web UI

**Test it**:
1. Start the watcher on `test_docs/`
2. Drop a new file in — verify it gets ingested (check logs)
3. Modify a file — verify chunks get updated
4. Delete a file — verify its chunks are removed

**Done when**:
- [ ] New files are automatically ingested
- [ ] Modified files trigger re-ingestion
- [ ] Deleted files have their chunks removed

---

## Step 12: Add Metadata Filtering

**Goal**: Let users filter queries by file type or modification date.

**Update**: `src/retrieval/retriever.py` and both UIs

**What it does**:
- Add optional filters to the query function:
  - `file_type` — only search `.pdf`, `.md`, or `.txt` files
  - `modified_after` — only search files modified after a given date
- Use ChromaDB's `where` clause to filter during retrieval
- Add corresponding flags to the CLI (`--file-type`, `--modified-after`)
- Add filter inputs to the Streamlit sidebar

**Done when**:
- [ ] `query("question", file_type="pdf")` only returns PDF sources
- [ ] `query("question", modified_after="2025-01-01")` filters by date
- [ ] Filters work in both CLI and web UI

---

## Step 13: Add Async Ingestion

**Goal**: Make document ingestion non-blocking so the UI stays responsive.

**Update**: `src/ingestion/loaders.py`, `src/pipeline.py`, `src/ui/web.py`

**What it does**:
- Wrap the ingestion pipeline with `asyncio`
- In Streamlit, show a progress bar that updates as each file is processed
- Add a status indicator: "Ingesting... 3/10 files complete"
- Handle errors per-file (don't let one bad PDF crash the whole batch)

**Done when**:
- [ ] Web UI remains responsive during ingestion
- [ ] Progress bar updates in real-time
- [ ] A corrupted file is skipped with an error message, not a crash

---

## Step 14: Dockerize

**Goal**: One-command deployment for the entire application.

**Files**: `Dockerfile`, `docker-compose.yml`

**What it does**:
- `Dockerfile`: Python 3.11 base, copies source, installs deps
- `docker-compose.yml` with services:
  - `geekgrep` — runs the Streamlit web UI
  - `ollama` (optional profile) — local LLM server for offline use
- Pass `OPENAI_API_KEY` via environment variable
- Mount a `./documents` volume so users can drop files in from the host
- Mount a `./data` volume so ChromaDB persists between restarts
- Expose Streamlit on port `8501`

**Test it**:
```bash
docker compose up --build
# Open http://localhost:8501
# Drop files into ./documents/
# Ask questions in the UI

# For local-only mode with Ollama:
# docker compose --profile local up --build
```

**Done when**:
- [ ] `docker compose up` starts the app (OpenAI mode)
- [ ] Web UI is accessible at `localhost:8501`
- [ ] Can ingest and query documents through the containerized app
- [ ] Data persists after `docker compose down` and back `up`

---

## Step 15: Final Polish

**Goal**: Clean up for portfolio presentation.

**Do this**:
1. Write a `README.md` with:
   - Project description and screenshot
   - Quick start instructions (3 commands or fewer)
   - Architecture diagram (copy from THE_PLAN.md)
   - Usage examples for both CLI and web
2. Add a `.env.example` with all configurable environment variables:
   ```
   OPENAI_API_KEY=sk-your-key-here
   GEEKGREP_LLM_BACKEND=openai    # or 'ollama'
   GEEKGREP_MODEL=gpt-4o-mini     # or 'mistral' for ollama
   ```
3. Run all tests: `python -m pytest tests/ -v`
4. Remove any hardcoded paths or debug print statements
5. Add docstrings to all public functions
6. Create a short demo GIF or screenshot for the README

**Done when**:
- [ ] All tests pass
- [ ] README is complete with setup instructions
- [ ] No hardcoded paths or secrets in the code
- [ ] A stranger could clone the repo and get it running in under 5 minutes
