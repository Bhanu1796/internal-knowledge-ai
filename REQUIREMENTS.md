# REQUIREMENTS.md
## Internal Knowledge Base Navigator — Project Contract

> **Programme:** AI-Forge 2026 — Capstone Project #7
> **Duration:** 2 weeks (Days 1–14)
> **Frozen:** This document is the contract. Any change to scope requires full downstream revision.

---

## 1. Problem Statement

Employees in growing organisations waste significant time hunting for information scattered across policy documents, onboarding guides, and procedure files. Search tools return raw files; employees must read entire documents to find a single answer. There is no conversational interface that understands the question, locates the relevant passage, and delivers a direct answer with a link back to the source. This project builds that interface — a conversational AI that sits on top of an internal document knowledge base and returns synthesised, sourced answers in seconds.

---

## 2. In-Scope Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Document Ingestion Pipeline** | Load, chunk, embed, and persist 8 company policy Markdown documents into ChromaDB using `text-embedding-3-large` |
| 2 | **Query Understanding Agent** | Classify employee intent (PROCESS_INQUIRY / POLICY_LOOKUP / CONTACT_LOOKUP / GENERAL_INFO / UNKNOWN) and reformulate the raw question for semantic retrieval |
| 3 | **Semantic Search Agent** | Retrieve the top-K most relevant document chunks from ChromaDB via cosine similarity |
| 4 | **Answer Generator Agent** | Synthesise a concise, grounded answer from retrieved context using Gemini 2.5 Flash via LiteLLM proxy |
| 5 | **Source Linker Agent** | Deduplicate, rank, and format source document metadata including direct document-view links |
| 6 | **Sequential RAG Pipeline** | Wire all 4 agents into a deterministic LCEL chain (`RunnableLambda` composition) |
| 7 | **FastAPI REST Backend** | Expose `POST /query`, `GET /health`, and `GET /documents` endpoints with full Pydantic validation |
| 8 | **In-browser Document Viewer** | Serve raw documents via `GET /documents/view/{filename}` with path-traversal protection |
| 9 | **Streamlit Chat UI** | Conversational interface with intent chip, source cards (title + URL + relevance %), clickable example query buttons, "How I found this" pipeline trace expander (reformulated query, key entities, response time), and session history |
| 10 | **Document Index Sidebar** | Sidebar panel listing all ingested documents with status indicator |
| 11 | **Unit + Integration Tests** | pytest suite covering all 4 pipeline agents and all 3 API endpoints; coverage report via `pytest-cov` |
| 12 | **Configuration via `.env`** | All secrets and runtime parameters controlled through `pydantic-settings`; no hardcoded credentials |

---

## 3. Out-of-Scope Features

| Feature | Reason excluded |
|---------|----------------|
| User authentication / login | Adds auth infrastructure; out of scope for a 2-week internal demo |
| Persistent multi-session history (database) | Requires a session store; Streamlit `session_state` is sufficient for demo |
| Document upload UI | File management UX is a separate product surface; ingestion CLI is sufficient |
| Real-time streaming responses (SSE / WebSocket) | FastAPI streaming adds complexity; single-shot JSON response meets demo needs |
| Docker / container deployment | Infrastructure concern; local development environment is the target runtime |
| Real Confluence / SharePoint integration | API integration and auth are weeks of work; simulated URLs serve the same demo purpose |
| Feedback / thumbs-up rating system | Requires a feedback store and analytics backend |
| Analytics dashboard (query volume, latency trends) | Observability is a Phase 2 concern |
| Multi-tenant / department-level access control | Security model design is beyond 2-week scope |
| PDF / DOCX ingestion | Markdown-only corpus keeps ingestion deterministic for demo; loaders exist but not demoed |
| Fine-tuning or custom embeddings | Pre-trained `text-embedding-3-large` meets accuracy requirements |
| CI/CD pipeline | Out of scope for a capstone demo environment |

---

## 4. Assumptions

### Environment
- Python 3.11+ installed on the developer machine
- All dependencies installable via `pip install -r requirements.txt`
- Ports 8000 (FastAPI) and 8501 (Streamlit) are free on localhost

### Data
- The corpus is 8 Markdown company policy documents stored under `data/sample_docs/`
- Document volume fits entirely in memory during ingestion (< 1 MB total)
- ChromaDB persists on-disk under `chroma_db/`; the directory is git-ignored

### LLM / Embeddings
- The LiteLLM proxy at `http://litellm.amzur.com:4000` is reachable from the dev machine
- `gemini-2.5-flash` is available behind the proxy for answer generation
- `text-embedding-3-large` is available behind the proxy for embeddings
- API key is provided via `LITELLM_API_KEY` environment variable

### User
- Users are internal employees asking questions in natural English
- Average query length: 5–30 words
- Users do not require role-based document filtering

### Integration
- The Streamlit frontend and FastAPI backend run as two separate processes on the same machine
- The frontend calls the backend over `http://localhost:8000`

---

## 5. Success Criteria

| # | Criterion | Measurement |
|---|-----------|-------------|
| SC-1 | **Correct retrieval** | For each of the 8 demo queries in `DEMO_GUIDE.md`, at least one returned source chunk maps to the correct ground-truth document |
| SC-2 | **End-to-end latency** | `POST /query` responds in ≤ 8 seconds (p95) on the demo machine for typical single-sentence questions |
| SC-3 | **Test coverage** | All 7 pytest test functions pass with zero failures (`pytest tests/ -v` green) |
| SC-4 | **UI completeness** | The Streamlit chat UI renders: answer text, intent chip, at least one source card with a working "View Document" link, and a "How I found this" pipeline trace expander showing `reformulated_query` and `key_entities` |
| SC-5 | **No hardcoded secrets** | `grep -r "api_key\s*=" app/` returns zero matches; all secrets loaded from `.env` |

---

## 6. Deliverables List

> Elaborated in [DELIVERABLES.md](DELIVERABLES.md).

| # | Deliverable |
|---|-------------|
| D-1 | Working application (backend + frontend running locally) |
| D-2 | Ingested ChromaDB with 8 documents and verifiable chunk count |
| D-3 | Full pytest suite — all tests green |
| D-4 | Live demo walkthrough following `DEMO_GUIDE.md` |
| D-5 | `SPEC.md`, `PLAN.md`, `CHECKPOINTS.md`, `DEPENDENCIES.md`, `PROMPT_SEQUENCES.md` |
| D-6 | Updated `README.md` with quick-start instructions and current phase status |
| D-7 | `docs/architecture.mmd` — canonical Mermaid diagram |

---

## 7. Two-Week Capacity Reality Check

**Assumptions:** 1 developer, ~6 focused hours/day, 10 working days.

| Week | Days | Theme | Capacity (hrs) | Key Risks |
|------|------|-------|----------------|-----------|
| Week 1 | 1–5 | Core pipeline + backend | ~30 hrs | LiteLLM proxy availability; ChromaDB version compatibility |
| Week 2 | 6–10 | Frontend + tests + polish | ~30 hrs | Streamlit CSS quirks; LLM answer quality tuning |

**Fit assessment:**

| Phase | Est. Effort | Fits 2 weeks? |
|-------|------------|---------------|
| Scaffolding + config | 4 hrs | Yes |
| Ingestion pipeline | 6 hrs | Yes |
| 4 RAG agents + pipeline wiring | 12 hrs | Yes |
| FastAPI backend (3 endpoints) | 6 hrs | Yes |
| Streamlit UI + source cards + sidebar | 10 hrs | Yes (tight) |
| Tests (unit + integration) | 6 hrs | Yes |
| Docs + demo prep | 6 hrs | Yes |
| **Total** | **~50 hrs** | **Yes — with ~10 hrs buffer** |

**Verdict:** Scope is achievable in 2 weeks by a single focused developer. The tightest constraint is the Streamlit frontend polish (Day 8–10). If behind, cut CSS styling before cutting functionality.
