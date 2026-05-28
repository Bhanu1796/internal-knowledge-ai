# PLAN.md
## Two-Week Execution Plan — Internal Knowledge Base Navigator

> Milestones mapped exclusively to in-scope deliverables from [REQUIREMENTS.md](REQUIREMENTS.md). Days are working days (Mon–Fri, 2 weeks).

---

## Timeline Overview

```
Week 1                                    Week 2
─────────────────────────────────────     ─────────────────────────────────────
Day 1    Day 2    Day 3-4   Day 5-6       Day 7-8   Day 9-10  Day 11-12  Day 13-14
   │        │        │         │              │          │          │          │
Phase 1  Phase 2  Phase 3a  Phase 3b     Phase 4    Phase 5   Phase 6   Phase 7
Scaffold  Ingest   Agents   Pipeline      API       Frontend   Tests     Polish
```

---

## Phase 1 — Scaffolding (Day 1)

**Goal:** A runnable project skeleton. Nothing works end-to-end yet, but the structure is correct and `from app.core.config import get_settings` succeeds.

| Task | File(s) | Done? |
|------|---------|-------|
| 1.1 Create folder structure | All directories | ☐ |
| 1.2 Pin all dependencies | `requirements.txt` | ☐ |
| 1.3 Implement `pydantic-settings` config | `app/core/config.py` | ☐ |
| 1.4 Define all Pydantic schemas | `app/models/schemas.py` | ☐ |
| 1.5 Create `.env.example` | `.env.example` | ☐ |
| 1.6 Set up `.gitignore` | `.gitignore` | ☐ |
| 1.7 Write planning docs (this file + SPEC, etc.) | `*.md`, `docs/` | ☐ |

**Gate:** `python -c "from app.core.config import get_settings; print(get_settings())"` succeeds.

---

## Phase 2 — Document Ingestion Pipeline (Day 2)

**Goal:** Run `python scripts/ingest.py` and verify documents are persisted in ChromaDB.

| Task | File(s) | Done? |
|------|---------|-------|
| 2.1 Implement document loader (Markdown + recursive splitter) | `app/ingestion/document_loader.py` | ☐ |
| 2.2 Implement embedder + ChromaDB persistence | `app/ingestion/embedder.py` | ☐ |
| 2.3 Write ingestion CLI script | `scripts/ingest.py` | ☐ |
| 2.4 Create 8 sample policy documents | `data/sample_docs/*.md` | ☐ |
| 2.5 Verify: `GET /health` returns `vector_store_docs > 0` | Manual | ☐ |

**Gate:** `python scripts/ingest.py` completes without error; ChromaDB collection has ≥ 30 chunks.

---

## Phase 3a — Pipeline Agents (Days 3–4)

**Goal:** Each agent can be called in isolation and returns the correct Pydantic model.

| Task | File(s) | Done? |
|------|---------|-------|
| 3.1 Implement Query Understanding Agent | `app/agents/query_understanding.py` | ☐ |
| 3.2 Implement Search Agent | `app/agents/search_agent.py` | ☐ |
| 3.3 Implement Answer Generator Agent | `app/agents/answer_generator.py` | ☐ |
| 3.4 Implement Source Linker Agent | `app/agents/source_linker.py` | ☐ |

**Gate:** Each agent's `run()` function can be called with a valid input dict and returns the expected output model without raising.

---

## Phase 3b — Pipeline Wiring (Days 5–6)

**Goal:** A single `run_pipeline("What is the leave policy?")` call returns a `QueryResponse` with a real answer.

| Task | File(s) | Done? |
|------|---------|-------|
| 3.5 Wire all agents into LCEL chain | `app/core/pipeline.py` | ☐ |
| 3.6 End-to-end smoke test via Python REPL | Manual | ☐ |

**Gate:** Running `run_pipeline("What is the annual leave policy?")` returns `has_answer=True` and at least one source from `annual-leave-policy.md`.

---

## Phase 4 — FastAPI Backend (Days 7–8)

**Goal:** All API endpoints respond correctly. Swagger UI is usable.

| Task | File(s) | Done? |
|------|---------|-------|
| 4.1 Implement `POST /query` | `app/api/routes.py` | ☐ |
| 4.2 Implement `GET /health` | `app/api/routes.py` | ☐ |
| 4.3 Implement `GET /documents` | `app/api/routes.py` | ☐ |
| 4.4 Implement `GET /documents/view/{filename}` | `app/api/routes.py` | ☐ |
| 4.5 Configure FastAPI app with CORS + lifespan | `app/main.py` | ☐ |
| 4.6 Test all endpoints via Swagger UI | `http://localhost:8000/docs` | ☐ |

**Gate:** `curl -X POST http://localhost:8000/query -d '{"question":"test"}'` returns a 200 JSON response.

---

## Phase 5 — Streamlit Frontend (Days 9–10)

**Goal:** A working chat UI that a non-technical reviewer can use without instructions.

| Task | File(s) | Done? |
|------|---------|-------|
| 5.1 Chat message UI with session history | `frontend/app.py` | ☐ |
| 5.2 Intent chip display | `frontend/app.py` | ☐ |
| 5.3 Source card components (title, URL, score, "View Document") | `frontend/app.py` | ☐ |
| 5.4 Sidebar: document index + API health indicator | `frontend/app.py` | ☐ |
| 5.5 Apply design tokens + custom CSS | `frontend/app.py` | ☐ |
| 5.6 Verify full end-to-end flow in browser | Manual | ☐ |

**Gate:** Opening `http://localhost:8501`, asking "What is the leave policy?", and seeing an answer with a source card — all within 8 seconds.

---

## Phase 6 — Tests (Days 11–12)

**Goal:** `pytest tests/ -v` produces zero failures.

| Task | File(s) | Done? |
|------|---------|-------|
| 6.1 Unit test: Query Understanding Agent | `tests/test_pipeline.py` | ☐ |
| 6.2 Unit test: Search Agent | `tests/test_pipeline.py` | ☐ |
| 6.3 Unit test: Answer Generator Agent | `tests/test_pipeline.py` | ☐ |
| 6.4 Unit test: Source Linker Agent | `tests/test_pipeline.py` | ☐ |
| 6.5 Unit test: Full pipeline chain | `tests/test_pipeline.py` | ☐ |
| 6.6 Integration test: `POST /query` | `tests/test_api.py` | ☐ |
| 6.7 Integration test: `GET /health` | `tests/test_api.py` | ☐ |
| 6.8 Integration test: `GET /documents` | `tests/test_api.py` | ☐ |

**Gate:** `pytest tests/ -v --tb=short` exits with code 0.

---

## Phase 7 — Polish & Demo Preparation (Days 13–14)

**Goal:** A reviewer who clones the repo cold can run the app and demo it without assistance.

| Task | File(s) | Done? |
|------|---------|-------|
| 7.1 Final README with quick-start + current phase status | `README.md` | ☐ |
| 7.2 Verify `DEMO_GUIDE.md` queries all produce correct results | Manual | ☐ |
| 7.3 Confirm all 5 success criteria from REQUIREMENTS.md | Manual | ☐ |
| 7.4 Confirm no hardcoded secrets in the codebase | `grep` check | ☐ |
| 7.5 Dry-run the full demo end-to-end | Manual | ☐ |

**Gate:** All checkpoints in [CHECKPOINTS.md](CHECKPOINTS.md) are green.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LiteLLM proxy unavailable | Medium | High | Cache a sample response for demo fallback; test proxy on Day 1 |
| ChromaDB version breaking change | Low | Medium | Pin version in `requirements.txt`; test ingestion on Day 2 |
| Streamlit CSS regression on upgrade | Low | Low | Pin `streamlit==1.45.1` |
| LLM answer quality poor for some queries | Medium | Medium | Tune prompt on Days 5–6; add "no answer" fallback |
| Phase 5 (frontend) runs over time | Medium | Low | Cut CSS polish before cutting functionality |
