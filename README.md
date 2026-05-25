# Internal Knowledge Base Navigator

> **AI-Forge 2026 — Capstone Project #7**
>
> A conversational AI that queries an internal document knowledge base and returns synthesised answers with source links — built on a four-stage Sequential Pipeline.

---

## Architecture

```
User question
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│              Sequential Pipeline (LCEL)                 │
│                                                         │
│  ① Query Understanding   →  intent + reformulated query │
│  ② Search Agent          →  top-K chunks from ChromaDB  │
│  ③ Answer Generator      →  LLM-synthesised answer      │
│  ④ Source Linker         →  deduplicated source links   │
└─────────────────────────────────────────────────────────┘
      │
      ▼
FastAPI REST backend  ←→  Streamlit chat UI
```

**Stack**

| Layer | Technology |
|---|---|
| LLM / Embeddings | LiteLLM proxy → Gemini 2.5 Flash / text-embedding-3-large |
| Vector store | ChromaDB 1.5.x (persistent) |
| Pipeline | LangChain LCEL (`RunnableLambda` chain) |
| Backend API | FastAPI 0.115 + Uvicorn |
| Frontend | Streamlit 1.45 |
| Config | pydantic-settings + `.env` |
| Tests | pytest 8.3 + pytest-asyncio |

---

## Project Structure

```
internal-knowledge-ai/
├── app/
│   ├── agents/
│   │   ├── query_understanding.py   # Stage 1 — intent & reformulation
│   │   ├── search_agent.py          # Stage 2 — ChromaDB similarity search
│   │   ├── answer_generator.py      # Stage 3 — LLM answer synthesis
│   │   └── source_linker.py         # Stage 4 — deduplicate & rank sources
│   ├── api/
│   │   └── routes.py                # FastAPI route handlers
│   ├── core/
│   │   ├── config.py                # pydantic-settings singleton
│   │   └── pipeline.py              # LCEL chain wiring
│   ├── ingestion/
│   │   ├── document_loader.py       # Load & chunk documents
│   │   └── embedder.py              # Embed & store in ChromaDB
│   ├── models/
│   │   └── schemas.py               # All Pydantic models
│   └── main.py                      # FastAPI app entry point
├── data/
│   └── sample_docs/                 # 8 company policy documents
├── docs/                            # Architecture & API docs
├── frontend/
│   └── app.py                       # Streamlit chat UI
├── scripts/
│   └── ingest.py                    # Ingestion CLI
├── tests/
│   ├── test_pipeline.py             # Unit tests — all 4 pipeline stages
│   └── test_api.py                  # Integration tests — all 3 API endpoints
├── .env.example                     # Environment variable template
└── requirements.txt
```

---

## Quick Start

### Prerequisites

- Python 3.12
- Access to the LiteLLM proxy (see `.env.example`)

### 1 — Clone & install

```bash
git clone <repo-url>
cd internal-knowledge-ai
pip install -r requirements.txt
```

### 2 — Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your LITELLM_PROXY_URL and LITELLM_API_KEY
```

### 3 — Ingest documents

```bash
python scripts/ingest.py
# Expected output: "Ingestion complete. 35 chunks stored."
```

### 4 — Start the backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify: `GET http://localhost:8000/health`

### 5 — Start the frontend

```bash
streamlit run frontend/app.py --server.port 8501
```

Open: `http://localhost:8501`

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check + vector store doc count |
| `POST` | `/query` | Submit a question, receive an answer with sources |
| `GET` | `/documents` | List all indexed documents |

**POST `/query` — request body**

```json
{
  "question": "What is the annual leave policy?",
  "top_k": 5
}
```

**POST `/query` — response**

```json
{
  "question": "What is the annual leave policy?",
  "answer": "Employees are entitled to 20 days of annual leave per year...",
  "intent": "POLICY_LOOKUP",
  "has_answer": true,
  "sources": [
    {
      "title": "Annual Leave Policy",
      "url": "https://confluence.internal/pages/annual-leave-policy",
      "source_file": "annual-leave-policy.md",
      "page": 0,
      "score": 0.91
    }
  ],
  "processing_time_ms": 1843
}
```

Full API docs auto-generated at `http://localhost:8000/docs`.

---

## Running Tests

```bash
python -m pytest tests/ -v
```

15 tests — 8 pipeline unit tests + 7 API integration tests. All external calls (LLM, ChromaDB) are mocked.

---

## Sample Documents

Eight company policy documents are included in `data/sample_docs/`:

- Annual Leave Policy
- IT Software Request Process
- Employee Onboarding Guide
- Expense Reimbursement Policy
- Remote Work Policy
- Code of Conduct
- Performance Review Process
- Security Guidelines

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LITELLM_PROXY_URL` | LiteLLM proxy base URL | — |
| `LITELLM_API_KEY` | API key for the proxy | — |
| `LLM_MODEL` | Chat model name | `gemini/gemini-2.5-flash` |
| `LITELLM_EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-large` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_db` |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection | `knowledge_base` |
| `DOCS_PATH` | Path to documents | `./data/sample_docs` |
| `SEARCH_TOP_K` | Default results per query | `5` |
| `SEARCH_MIN_SCORE` | Minimum relevance score | `0.30` |
| `APP_PORT` | FastAPI port | `8000` |
| `API_BASE_URL` | Frontend → backend URL | `http://localhost:8000` |

---

## Further Reading

- [Architecture](docs/architecture.md)
- [Pipeline stages](docs/pipeline.md)
- [Ingestion](docs/ingestion.md)
- [API reference](docs/api.md)
- [Setup guide](docs/setup.md)
