# Setup Guide

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Python | 3.11+ |
| pip | 23+ |
| LiteLLM Proxy API Key | — |
| Git | 2.x |

---

## 1. Clone the Repository

```bash
git clone <repository-url>
cd internal-knowledge-ai
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi`, `uvicorn[standard]` — REST API
- `streamlit` — chat frontend
- `langchain`, `langchain-openai`, `langchain-community` — LLM pipeline
- `chromadb` — vector store
- `pypdf`, `python-docx`, `unstructured` — document loaders
- `pydantic`, `pydantic-settings` — data models and config
- `pytest`, `httpx` — testing

---

## 4. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set the required variables:

```dotenv
# Required
LITELLM_PROXY_URL=http://litellm.amzur.com:4000
LITELLM_API_KEY=your-litellm-api-key

# Optional — defaults shown
LLM_MODEL=gemini/gemini-2.5-flash
LITELLM_EMBEDDING_MODEL=text-embedding-3-large
SEARCH_TOP_K=5
SEARCH_MIN_SCORE=0.30
CHUNK_SIZE=800
CHUNK_OVERLAP=100
CHROMA_PERSIST_DIR=./chroma_db
DOCS_PATH=./data/sample_docs
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
```

> **Never commit `.env` to version control.** It is listed in `.gitignore`.

---

## 5. Ingest Documents into the Vector Store

This step loads all files from `data/sample_docs/`, chunks them, embeds them via the LiteLLM proxy, and persists the vectors in ChromaDB.

```bash
python scripts/ingest.py
```

Expected output:
```
[Ingest] Loading documents from data/sample_docs/ ...
[Ingest] Loaded 8 documents → 47 chunks
[Ingest] Embedding and storing chunks in ChromaDB ...
[Ingest] Done. ChromaDB collection 'knowledge_base' contains 47 documents.
```

To re-ingest after adding new documents, run the same command. The collection is cleared and rebuilt from scratch.

---

## 6. Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify it is running:
```bash
curl http://localhost:8000/health
# {"status": "ok", "vector_store_docs": 47}
```

Interactive API docs are available at: `http://localhost:8000/docs`

---

## 7. Start the Streamlit Frontend

Open a **second terminal** (with the virtual environment activated):

```bash
streamlit run frontend/app.py
```

The UI opens automatically at: `http://localhost:8501`

---

## 8. Run Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_pipeline.py::test_query_understanding_agent  PASSED
tests/test_pipeline.py::test_search_agent               PASSED
tests/test_pipeline.py::test_answer_generator           PASSED
tests/test_pipeline.py::test_source_linker              PASSED
tests/test_pipeline.py::test_full_pipeline              PASSED
tests/test_api.py::test_health_endpoint                 PASSED
tests/test_api.py::test_query_endpoint_valid            PASSED
tests/test_api.py::test_query_endpoint_no_results       PASSED
```

---

## Project Structure

```
internal-knowledge-ai/
│
├── app/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                   # App entry point, lifespan
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # API route handlers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # pydantic-settings config
│   │   └── pipeline.py           # LCEL sequential pipeline
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── query_understanding.py
│   │   ├── search_agent.py
│   │   ├── answer_generator.py
│   │   └── source_linker.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   └── embedder.py
│   └── models/
│       ├── __init__.py
│       └── schemas.py
│
├── frontend/
│   └── app.py                    # Streamlit chat UI
│
├── data/
│   └── sample_docs/              # Knowledge base source files
│       ├── annual-leave-policy.md
│       ├── it-software-request.md
│       ├── onboarding-guide.md
│       ├── expense-reimbursement.md
│       ├── remote-work-policy.md
│       ├── code-of-conduct.md
│       ├── performance-review-process.md
│       └── security-guidelines.md
│
├── scripts/
│   └── ingest.py                 # One-shot ingestion CLI
│
├── tests/
│   ├── test_pipeline.py
│   └── test_api.py
│
├── chroma_db/                    # ChromaDB persisted data (git-ignored)
├── docs/                         # Project documentation
│   ├── architecture.md
│   ├── pipeline.md
│   ├── setup.md
│   ├── api.md
│   └── ingestion.md
│
├── .env                          # Your local secrets (git-ignored)
├── .env.example                  # Template — safe to commit
├── .gitignore
└── requirements.txt
```

---

## Adding New Documents to the Knowledge Base

1. Drop your files (`.md`, `.pdf`, `.docx`, `.txt`) into `data/sample_docs/`
2. Re-run the ingestion script:
   ```bash
   python scripts/ingest.py
   ```
3. Restart the FastAPI backend (or it will reload automatically with `--reload`)

---

## Common Issues

### `LITELLM_API_KEY` not found
Ensure `.env` exists in the project root and contains a valid `LITELLM_API_KEY` and `LITELLM_PROXY_URL`. Confirm the virtual environment is activated before starting services.

### ChromaDB collection is empty
Run `python scripts/ingest.py` before starting the backend. The collection must be populated before queries can be answered.

### Port already in use
Change the port in `.env` (`APP_PORT=8001`) and pass it to uvicorn:
```bash
uvicorn app.main:app --reload --port 8001
```

### Streamlit cannot reach the backend
Ensure the FastAPI server is running on port 8000 before starting Streamlit. The backend URL is set in `frontend/app.py` via the `API_BASE_URL` constant.
