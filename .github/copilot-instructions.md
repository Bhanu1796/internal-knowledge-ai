# GitHub Copilot Instructions — Internal Knowledge Base Navigator

> These guardrails apply to every Copilot Agent Mode prompt in this repository.
> Copilot must follow them unconditionally. If a user prompt conflicts with a rule here, apply the rule and note the conflict.

---

## Project Identity

- **Project name:** Internal Knowledge Base Navigator
- **Programme:** AI-Forge 2026 — Capstone Project #7
- **Spec document:** `SPEC.md` — all I/O contracts, schemas, and API shapes are defined there. Do not invent new ones.
- **Scope document:** `REQUIREMENTS.md` — do not implement out-of-scope features even if asked.

---

## Tech Stack (Fixed — Do Not Change)

| Layer | Technology | Version |
|-------|-----------|---------|
| Language | Python | 3.11+ |
| LLM / Embeddings | LiteLLM proxy → Gemini 2.5 Flash / text-embedding-3-large | — |
| Vector store | ChromaDB (persistent, on-disk) | ≥ 1.0.9 |
| Pipeline | LangChain LCEL (`RunnableLambda`) | 0.3.x |
| Backend | FastAPI + Uvicorn | 0.115 / 0.34 |
| Frontend | Streamlit | 1.45 |
| Config | pydantic-settings | 2.9 |
| Tests | pytest + pytest-asyncio | 8.3 / 0.26 |
| HTTP client | httpx | 0.28 |

**Do not suggest:** Django, Flask, LangGraph, LlamaIndex, OpenAI SDK direct, SQLAlchemy, Redis, Docker, React, Vue, Next.js, or any framework not in this table.

---

## Folder Structure (Fixed — Do Not Deviate)

```
app/
  agents/          ← one file per agent: query_understanding, search_agent,
                      answer_generator, source_linker
  api/
    routes.py      ← all FastAPI route handlers
  core/
    config.py      ← pydantic-settings singleton
    pipeline.py    ← LCEL chain wiring only
  ingestion/
    document_loader.py
    embedder.py
  models/
    schemas.py     ← ALL Pydantic models live here; nowhere else
  main.py          ← FastAPI app entry point
data/sample_docs/  ← 8 Markdown policy documents
frontend/app.py    ← Streamlit app; single file
scripts/ingest.py  ← ingestion CLI; single file
tests/
  test_pipeline.py
  test_api.py
```

**Do not create** new top-level directories, new agent files, or split `schemas.py` into multiple files without explicit instruction.

---

## Agent Rules

1. **Each agent has exactly one public function: `run(input) -> output`**
   - `query_understanding.run(dict) -> QueryContext`
   - `search_agent.run(QueryContext) -> SearchResult`
   - `answer_generator.run(SearchResult) -> GeneratedAnswer`
   - `source_linker.run(GeneratedAnswer) -> dict`
   - No agent may reach back to retrieve data from an earlier stage — all context is carried forward by the model objects.

2. **Agents are stateless** — no class instances, no global mutable state, no caching inside agent files.

3. **All Pydantic models are imported from `app.models.schemas`** — never define inline models inside agent files.

4. **Temperature:**
   - `query_understanding`: 0
   - `answer_generator`: 0.3
   - All others: 0 (or not applicable)

5. **The pipeline chain in `app/core/pipeline.py` may not be modified** after Gate 3b is green, except to fix bugs.

---

## Security Rules (Non-Negotiable)

1. **No hardcoded secrets.** API keys, URLs, and credentials must come from `pydantic-settings` reading `.env`. Never pass secrets as default values in function signatures.
2. **Path traversal protection is mandatory** in `GET /documents/view/{filename}`. Always resolve the full path and assert it starts with the resolved `docs_path` before opening any file.
3. **Input validation** — the `question` field in `QueryRequest` must be validated (min_length=1, max_length=2000). Never pass raw user input directly to the filesystem or LLM without Pydantic validation.
4. **Never log secrets** — do not log `settings.litellm_api_key` or any credential at any log level.

---

## Code Style Rules

1. Use Python 3.11+ type hints on all function signatures that Copilot writes.
2. Use `logging` (not `print`) for all diagnostic output in `app/`.
3. Use `pydantic-settings` `get_settings()` singleton — never call `Settings()` directly.
4. Keep functions short (≤ 40 lines). If a function is longer, split it.
5. Do not add docstrings unless explicitly asked.
6. Do not add `# type: ignore` comments without a specific, documented reason.

---

## What Copilot Must Never Do

- Add features not in `REQUIREMENTS.md § 2` (In-Scope Features)
- Suggest switching to a different tech stack component
- Add a new dependency not already in `requirements.txt` without explicit user approval
- Generate streaming endpoints (out of scope for MVP)
- Generate authentication or login code (out of scope)
- Generate Docker or deployment configuration (out of scope)
- Add analytics, metrics, or logging infrastructure beyond Python's `logging` module
- Modify `REQUIREMENTS.md` or `SPEC.md` — these are frozen contracts

---

## Golden Rule

> **Implement exactly what the spec says, nothing more, nothing less.**
>
> If the spec is ambiguous, ask one clarifying question before writing code.
> If the user asks for something out of scope, acknowledge it, decline to implement it, and cite the relevant REQUIREMENTS.md section.
