# CHECKPOINTS.md
## Phase Gate Criteria — Internal Knowledge Base Navigator

> You cannot start the next phase until the current gate is fully green. Each gate is a verifiable, binary pass/fail check — not a feeling of "mostly done."

---

## How to Use This Document

Before moving to any new phase:
1. Run every gate command listed for the current phase
2. All commands must exit with code 0 (or return the expected output)
3. Mark the gate `[✅ PASSED - Date]` before proceeding
4. If a gate is failing, fix it — do not skip it

---

## Gate 1 — Scaffolding Complete
**Must pass before:** Phase 2 (Ingestion)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G1.1 | Config module loads without error | `python -c "from app.core.config import get_settings; s = get_settings(); print(s.llm_model)"` |
| G1.2 | Schemas module imports cleanly | `python -c "from app.models.schemas import QueryResponse, QueryRequest; print('ok')"` |
| G1.3 | `.env.example` exists with all required keys | `cat .env.example` — must list all 8 keys from SPEC.md § 5 |
| G1.4 | `.env` exists (copied from example) and has real values | `python -c "from app.core.config import get_settings; assert get_settings().litellm_api_key"` |
| G1.5 | `data/sample_docs/` has exactly 8 `.md` files | `Get-ChildItem data/sample_docs/*.md \| Measure-Object \| Select-Object -ExpandProperty Count` → `8` |

**Gate 1 Status:** `[ ] Not started`

---

## Gate 2 — Ingestion Pipeline Ready
**Must pass before:** Phase 3a (Agents)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G2.1 | Ingestion script completes without error | `python scripts/ingest.py` → exit code 0 |
| G2.2 | ChromaDB collection has ≥ 30 chunks | `python -c "from app.ingestion.embedder import get_collection_count; print(get_collection_count())"` → `>= 30` |
| G2.3 | All 8 documents are indexed | `python -c "from app.ingestion.embedder import get_vector_store; s = get_vector_store(); r = s._collection.get(include=['metadatas']); srcs = {m['source'] for m in r['metadatas']}; print(len(srcs))"` → `8` |
| G2.4 | Embedder returns a vector store | `python -c "from app.ingestion.embedder import get_vector_store; print(type(get_vector_store()))"` → `<class 'langchain_chroma.vectorstores.Chroma'>` |

**Gate 2 Status:** `[ ] Not started`

---

## Gate 3a — Agents Individually Functional
**Must pass before:** Phase 3b (Pipeline Wiring)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G3a.1 | Query Understanding returns QueryContext | `python -c "from app.agents.query_understanding import run; r = run({'raw_query': 'What is the leave policy?', 'top_k': 5}); print(r.intent)"` → a valid intent string |
| G3a.2 | Search Agent returns chunks | `python -c "from app.agents.query_understanding import run as qu; from app.agents.search_agent import run as sa; ctx = qu({'raw_query': 'leave policy', 'top_k': 5}); r = sa(ctx); print(len(r.chunks))"` → `>= 1` |
| G3a.3 | Answer Generator returns answer | Manually verify `answer_generator.run()` with a populated `SearchResult` returns `has_answer=True` |
| G3a.4 | Source Linker returns deduped sources | Manually verify `source_linker.run()` returns a dict with `sources` list, one entry per unique source file |

**Gate 3a Status:** `[ ] Not started`

---

## Gate 3b — Pipeline Chain Functional
**Must pass before:** Phase 4 (FastAPI Backend)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G3b.1 | Full pipeline returns QueryResponse | `python -c "from app.core.pipeline import run_pipeline; r = run_pipeline('What is the annual leave policy?'); print(r.intent, r.has_answer)"` → `POLICY_LOOKUP True` |
| G3b.2 | Sources point to correct document | Verify `r.sources[0].source_file == 'annual-leave-policy.md'` |
| G3b.3 | Processing time logged | Uvicorn / REPL console shows `Pipeline completed in Xms` |
| G3b.4 | "No answer" path works | `run_pipeline("xyzzy plugh nonsense irrelevant")` → `has_answer=False` (or graceful fallback) |

**Gate 3b Status:** `[ ] Not started`

---

## Gate 4 — FastAPI Backend Operational
**Must pass before:** Phase 5 (Streamlit Frontend)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G4.1 | App starts without error | `uvicorn app.main:app --port 8000` → no import errors in console |
| G4.2 | Health endpoint returns ok | `curl -s http://localhost:8000/health` → `{"status":"ok","vector_store_docs":35}` |
| G4.3 | Query endpoint returns 200 | `curl -s -X POST http://localhost:8000/query -H "Content-Type: application/json" -d "{\"question\":\"What is the leave policy?\"}"` → 200 with `answer` field |
| G4.4 | Documents endpoint lists 8 docs | `curl -s http://localhost:8000/documents` → `total_documents: 8` |
| G4.5 | Document viewer returns HTML | `curl -s http://localhost:8000/documents/view/annual-leave-policy.md` → starts with `<!DOCTYPE html>` or `<html` |
| G4.6 | Path traversal is blocked | `curl -s http://localhost:8000/documents/view/../../app/core/config.py` → `400 Bad Request` |
| G4.7 | Swagger UI loads | Open `http://localhost:8000/docs` in browser — interactive UI visible |

**Gate 4 Status:** `[ ] Not started`

---

## Gate 5 — Streamlit Frontend Working
**Must pass before:** Phase 6 (Tests)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G5.1 | Streamlit starts without error | `streamlit run frontend/app.py` → opens at `http://localhost:8501` |
| G5.2 | API health indicator shows green | Sidebar shows green dot and "API Online" |
| G5.3 | Document list populated | Sidebar shows 8 documents with chunk counts |
| G5.4 | Query returns answer + intent chip | Ask "What is the annual leave policy?" → intent chip shows `POLICY_LOOKUP`, answer text appears |
| G5.5 | Source card renders | At least one source card shows title, score %, and "View Document" link |
| G5.6 | "View Document" link works | Clicking "View Document" opens the document viewer in a new tab |
| G5.7 | Conversation history persists | Ask a second question — both exchanges visible in chat |
| G5.8 | "Clear conversation" works | Click button → conversation resets to empty |

**Gate 5 Status:** `[ ] Not started`

---

## Gate 6 — Tests All Green
**Must pass before:** Phase 7 (Polish & Demo Prep)

| # | Check | Command / Verification |
|---|-------|----------------------|
| G6.1 | All tests discovered | `pytest tests/ --collect-only` → ≥ 8 tests listed, 0 errors |
| G6.2 | All tests pass | `pytest tests/ -v --tb=short` → exit code 0, 0 failures, 0 errors |
| G6.3 | No hardcoded secrets | `grep -rn "api_key\s*=" app/ scripts/` → 0 matches (assignments in config.py are from env only) |

**Gate 6 Status:** `[ ] Not started`

---

## Gate 7 — Demo Ready (Final Gate)
**Must pass before:** Submission / Demo Day

| # | Check | Command / Verification |
|---|-------|----------------------|
| G7.1 | All 5 success criteria from REQUIREMENTS.md are met | Review each SC-1 through SC-5 manually |
| G7.2 | All 8 demo queries from DEMO_GUIDE.md return correct results | Run each query; verify source document matches ground truth |
| G7.3 | Cold-start works | Wipe terminals, clone fresh, follow README quick-start — app runs |
| G7.4 | End-to-end latency ≤ 8 seconds | Time 3 queries; all ≤ 8 seconds |
| G7.5 | DELIVERABLES.md checklist fully checked | Every item in DELIVERABLES.md is marked complete |

**Gate 7 Status:** `[ ] Not started`

---

## Gate Summary Dashboard

| Gate | Phase | Status |
|------|-------|--------|
| Gate 1 | Scaffolding | `[ ] Not started` |
| Gate 2 | Ingestion | `[ ] Not started` |
| Gate 3a | Agents | `[ ] Not started` |
| Gate 3b | Pipeline | `[ ] Not started` |
| Gate 4 | API | `[ ] Not started` |
| Gate 5 | Frontend | `[ ] Not started` |
| Gate 6 | Tests | `[ ] Not started` |
| Gate 7 | Demo Ready | `[ ] Not started` |
