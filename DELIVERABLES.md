# DELIVERABLES.md
## Final Demo Checklist — Internal Knowledge Base Navigator

> This document elaborates the deliverables list from [REQUIREMENTS.md § 6](REQUIREMENTS.md) into a concrete, reviewable checklist. Every item here must be checked before the demo begins.

---

## D-1 — Working Application

The application must run locally from a clean checkout with no prior state.

| # | Item | Status |
|---|------|--------|
| D1.1 | `pip install -r requirements.txt` completes without errors | `[ ]` |
| D1.2 | `.env` configured with working LiteLLM credentials | `[ ]` |
| D1.3 | FastAPI backend starts: `uvicorn app.main:app --reload` | `[ ]` |
| D1.4 | Streamlit frontend starts: `streamlit run frontend/app.py` | `[ ]` |
| D1.5 | Both services run simultaneously without port conflict | `[ ]` |
| D1.6 | No import errors, no runtime exceptions at startup | `[ ]` |

---

## D-2 — Ingested Knowledge Base

ChromaDB is populated and the vector store is verifiably correct.

| # | Item | Status |
|---|------|--------|
| D2.1 | `python scripts/ingest.py` runs without error | `[ ]` |
| D2.2 | `GET /health` returns `vector_store_docs >= 30` | `[ ]` |
| D2.3 | `GET /documents` returns exactly 8 documents | `[ ]` |
| D2.4 | All 8 source documents present in `data/sample_docs/` | `[ ]` |
| D2.5 | Collection name is `knowledge_base` (as per SPEC.md § 3) | `[ ]` |

**Expected documents:**

| Document | Source file |
|----------|------------|
| Annual Leave Policy | `annual-leave-policy.md` |
| Code of Conduct | `code-of-conduct.md` |
| Expense Reimbursement | `expense-reimbursement.md` |
| IT Software Request | `it-software-request.md` |
| Onboarding Guide | `onboarding-guide.md` |
| Performance Review Process | `performance-review-process.md` |
| Remote Work Policy | `remote-work-policy.md` |
| Security Guidelines | `security-guidelines.md` |

---

## D-3 — Test Suite Green

| # | Item | Status |
|---|------|--------|
| D3.1 | `pytest tests/ --collect-only` discovers ≥ 8 tests | `[ ]` |
| D3.2 | `pytest tests/ -v` exits with code 0 | `[ ]` |
| D3.3 | Zero test failures | `[ ]` |
| D3.4 | Zero test errors | `[ ]` |
| D3.5 | Pipeline unit tests cover all 4 agents | `[ ]` |
| D3.6 | API integration tests cover `POST /query`, `GET /health`, `GET /documents` | `[ ]` |

---

## D-4 — Live Demo

Demonstrable end-to-end user journey following `DEMO_GUIDE.md`.

| # | Query | Expected intent | Expected source | Status |
|---|-------|----------------|----------------|--------|
| D4.1 | "What is the annual leave policy?" | POLICY_LOOKUP | annual-leave-policy.md | `[ ]` |
| D4.2 | "How do I request new software for my team?" | PROCESS_INQUIRY | it-software-request.md | `[ ]` |
| D4.3 | "What expenses can I claim when working remotely?" | POLICY_LOOKUP | remote-work-policy.md | `[ ]` |
| D4.4 | "Who do I contact about onboarding a new hire?" | CONTACT_LOOKUP | onboarding-guide.md | `[ ]` |
| D4.5 | Source card "View Document" link opens the correct document | N/A | Any | `[ ]` |
| D4.6 | API call visible in Swagger UI (`POST /query`) | N/A | N/A | `[ ]` |
| D4.7 | Uvicorn logs visible during demo showing live requests | N/A | N/A | `[ ]` |

---

## D-5 — Planning and Specification Documents

| # | Document | Location | Status |
|---|----------|----------|--------|
| D5.1 | REQUIREMENTS.md | `/REQUIREMENTS.md` | `[ ]` |
| D5.2 | SPEC.md | `/SPEC.md` | `[ ]` |
| D5.3 | PLAN.md | `/PLAN.md` | `[ ]` |
| D5.4 | CHECKPOINTS.md | `/CHECKPOINTS.md` | `[ ]` |
| D5.5 | DEPENDENCIES.md | `/DEPENDENCIES.md` | `[ ]` |
| D5.6 | PROMPT_SEQUENCES.md | `/PROMPT_SEQUENCES.md` | `[ ]` |
| D5.7 | FUTURE_VISION.md | `/FUTURE_VISION.md` | `[ ]` |
| D5.8 | MVP_PREVIEW.md | `/MVP_PREVIEW.md` | `[ ]` |
| D5.9 | DELIVERABLES.md (this file) | `/DELIVERABLES.md` | `[ ]` |

---

## D-6 — README and Entry Point

| # | Item | Status |
|---|------|--------|
| D6.1 | README.md describes the project in plain language | `[ ]` |
| D6.2 | Quick Start section works from a cold checkout | `[ ]` |
| D6.3 | Current phase status is accurate | `[ ]` |
| D6.4 | Links to SPEC.md, PLAN.md, DEMO_GUIDE.md all resolve | `[ ]` |

---

## D-7 — Architecture Diagram

| # | Item | Status |
|---|------|--------|
| D7.1 | `docs/architecture.mmd` exists | `[ ]` |
| D7.2 | Diagram renders correctly in a Mermaid viewer | `[ ]` |
| D7.3 | Diagram matches actual implemented architecture (all 4 agents, FastAPI, Streamlit, ChromaDB, LiteLLM) | `[ ]` |

---

## D-8 — Code Quality and Security

| # | Item | Status |
|---|------|--------|
| D8.1 | No hardcoded API keys or secrets in source code | `[ ]` |
| D8.2 | Path traversal protection present in `/documents/view/{filename}` | `[ ]` |
| D8.3 | All secrets in `.env`, loaded via `pydantic-settings` | `[ ]` |
| D8.4 | `.env` is listed in `.gitignore` | `[ ]` |
| D8.5 | `chroma_db/` is listed in `.gitignore` | `[ ]` |
| D8.6 | `__pycache__/` is listed in `.gitignore` | `[ ]` |

---

## Final Sign-Off

The project is **demo-ready** when every item above is checked.

| Reviewer | Sign-off | Date |
|----------|---------|------|
| Developer | | |
| Mentor | | |
