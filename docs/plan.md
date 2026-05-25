# Project Plan

## Project Details

| Field | Value |
|---|---|
| **Project** | Internal Knowledge Base Navigator |
| **Programme** | AI-Forge 2026 — Capstone Project #7 |
| **Duration** | 2 weeks (15 calendar days) |
| **Start Date** | Day 1 of assigned period |
| **Deliverable** | Production-grade conversational AI application |

---

## Objective

Build a conversational AI that helps employees find information within the company's internal knowledge base. The AI parses natural language questions, searches indexed documents, generates direct answers, and returns links to source documents — following a strict Sequential-Pipeline architecture.

---

## Phases & Task Breakdown

### Phase 1 — Project Scaffolding (Days 1–2)

| # | Task | File(s) | Status |
|---|---|---|---|
| 1.1 | Create full folder structure | All directories | ☐ |
| 1.2 | Write `requirements.txt` with pinned versions | `requirements.txt` | ☐ |
| 1.3 | Configure `pydantic-settings` config | `app/core/config.py` | ☐ |
| 1.4 | Define all Pydantic schemas | `app/models/schemas.py` | ☐ |
| 1.5 | Create `.env.example` | `.env.example` | ☐ |
| 1.6 | Set up `.gitignore` | `.gitignore` | ☐ |
| 1.7 | Write all documentation files | `docs/` | ☐ |

---

### Phase 2 — Document Ingestion Pipeline (Days 2–3)

| # | Task | File(s) | Status |
|---|---|---|---|
| 2.1 | Implement multi-format document loader | `app/ingestion/document_loader.py` | ☐ |
| 2.2 | Implement embedder + ChromaDB persistence | `app/ingestion/embedder.py` | ☐ |
| 2.3 | Write ingestion CLI script | `scripts/ingest.py` | ☐ |
| 2.4 | Create 8 sample knowledge base documents | `data/sample_docs/*.md` | ☐ |
| 2.5 | Verify ingestion produces correct chunk count | Manual test | ☐ |

---

### Phase 3 — Sequential RAG Pipeline (Days 3–6)

| # | Task | File(s) | Status |
|---|---|---|---|
| 3.1 | Implement Query Understanding Agent | `app/agents/query_understanding.py` | ☐ |
| 3.2 | Implement Search Agent | `app/agents/search_agent.py` | ☐ |
| 3.3 | Implement Answer Generator Agent | `app/agents/answer_generator.py` | ☐ |
| 3.4 | Implement Source Linker Agent | `app/agents/source_linker.py` | ☐ |
| 3.5 | Wire all agents into LCEL sequential chain | `app/core/pipeline.py` | ☐ |
| 3.6 | Smoke-test pipeline end-to-end in isolation | Python REPL / script | ☐ |

---

### Phase 4 — FastAPI Backend (Days 6–8)

| # | Task | File(s) | Status |
|---|---|---|---|
| 4.1 | Implement `POST /query` route | `app/api/routes.py` | ☐ |
| 4.2 | Implement `GET /health` route | `app/api/routes.py` | ☐ |
| 4.3 | Implement `GET /documents` route | `app/api/routes.py` | ☐ |
| 4.4 | Configure FastAPI app with CORS + lifespan | `app/main.py` | ☐ |
| 4.5 | Test all endpoints via Swagger UI | `http://localhost:8000/docs` | ☐ |

---

### Phase 5 — Streamlit Frontend (Days 8–10)

| # | Task | File(s) | Status |
|---|---|---|---|
| 5.1 | Build chat message UI with session history | `frontend/app.py` | ☐ |
| 5.2 | Add source-link card components | `frontend/app.py` | ☐ |
| 5.3 | Add sidebar: document index + config panel | `frontend/app.py` | ☐ |
| 5.4 | Apply design tokens + custom CSS | `frontend/app.py` | ☐ |
| 5.5 | Verify full end-to-end flow in browser | Manual test | ☐ |

---

### Phase 6 — Testing (Days 10–12)

| # | Task | File(s) | Status |
|---|---|---|---|
| 6.1 | Unit tests: Query Understanding Agent | `tests/test_pipeline.py` | ☐ |
| 6.2 | Unit tests: Search Agent | `tests/test_pipeline.py` | ☐ |
| 6.3 | Unit tests: Answer Generator Agent | `tests/test_pipeline.py` | ☐ |
| 6.4 | Unit tests: Source Linker Agent | `tests/test_pipeline.py` | ☐ |
| 6.5 | Unit tests: Full pipeline chain | `tests/test_pipeline.py` | ☐ |
| 6.6 | Integration tests: API endpoints | `tests/test_api.py` | ☐ |
| 6.7 | All tests pass (`pytest tests/ -v`) | — | ☐ |

---

### Phase 7 — Polish & Delivery (Days 12–15)

| # | Task | Status |
|---|---|---|
| 7.1 | Review all documentation files in `docs/` | ☐ |
| 7.2 | Final end-to-end demo rehearsal | ☐ |
| 7.3 | Prepare architecture diagram for walkthrough | ☐ |
| 7.4 | Code review: clean up comments, formatting | ☐ |
| 7.5 | Confirm all deliverables are ready | ☐ |

---

## Deliverables Checklist

| Deliverable | Description | Ready |
|---|---|---|
| **Application Walkthrough** | Live demo: submit query → get answer + sources, show multiple query types | ☐ |
| **Code Walkthrough** | Walk through `pipeline.py`, each agent, `main.py`, `frontend/app.py` | ☐ |
| **Framework, Tools & Techniques** | Explain LangChain LCEL, ChromaDB, RAG, OpenAI embeddings, FastAPI | ☐ |
| **Architecture Diagram** | `docs/architecture.md` — cover all components and data flows | ☐ |

---

## Dependencies & Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| OpenAI API rate limits during demo | Low | Cache a few example query responses; reduce `SEARCH_TOP_K` |
| ChromaDB local disk issues | Low | Keep `chroma_db/` backed up; add `--reset` flag to ingest script |
| LLM hallucination outside KB context | Medium | System prompt strictly instructs LLM to use only retrieved context |
| PDF parsing failures | Low | Fall back to `UnstructuredPDFLoader`; sample docs use Markdown |

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| LLM | Gemini 2.5 Flash via LiteLLM Proxy (`litellm.amzur.com`) |
| Embeddings | text-embedding-3-large via LiteLLM Proxy |
| Orchestration | LangChain LCEL |
| Vector Store | ChromaDB (persistent) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Config | pydantic-settings |
| Testing | pytest + httpx |
