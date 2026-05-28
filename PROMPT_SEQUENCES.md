# PROMPT_SEQUENCES.md
## Copilot Agent Mode Prompt Patterns

> Specification-driven development: every file in this project was built by feeding these prompt sequences into GitHub Copilot Agent Mode. Run them in order. Each prompt builds on the artefacts produced by the previous one.

---

## Philosophy

This project uses **specification-driven development**: write the spec first, then prompt the AI to implement it. The workflow is:

```
SPEC.md → Prompt → Code → Verify against SPEC → Next prompt
```

Never start a prompt without first telling Copilot which spec section applies. This keeps the AI grounded and makes its output reviewable.

---

## Prompt Sequence 0 — Orientation (Run once at session start)

```
Read the following files in order and confirm you understand the project:
1. REQUIREMENTS.md — what is in scope and why
2. SPEC.md — all I/O contracts and schemas
3. DEPENDENCIES.md — what must be built before what
4. CHECKPOINTS.md — what "done" means at each phase

Do not write any code yet. Summarise in 5 bullet points what the project does
and what the critical path is.
```

---

## Prompt Sequence 1 — Scaffolding

### 1.1 — Config

```
Refer to SPEC.md § 5 (Configuration).

Create app/core/config.py using pydantic-settings. The Settings class must expose
exactly these fields (with the defaults from the spec):
  LITELLM_API_KEY, LITELLM_PROXY_URL, LLM_MODEL, EMBEDDING_MODEL,
  CHROMA_PATH, DOCS_PATH, TOP_K, COLLECTION_NAME

Use a @lru_cache singleton pattern so settings are loaded once.
Do not add any fields that are not in SPEC.md § 5.
```

### 1.2 — Schemas

```
Refer to SPEC.md § 2 (Data Model).

Create app/models/schemas.py with exactly the models defined in SPEC.md § 2.1
(pipeline-internal) and § 2.2 (API models). Use Pydantic v2 syntax.
Add no extra fields. Add no methods. Keep it flat.
```

---

## Prompt Sequence 2 — Ingestion Pipeline

### 2.1 — Document Loader

```
Refer to SPEC.md § 3 (Vector Store Schema) for chunk parameters.

Create app/ingestion/document_loader.py.
Requirements:
- Load all .md files from the directory given by settings.docs_path
- Use langchain RecursiveCharacterTextSplitter with chunk_size=500, chunk_overlap=50
- Each chunk must carry metadata: source (filename), title (derived from filename),
  doc_url (http://localhost:8000/documents/view/{filename}), page (chunk index), chunk_id ({source}_{page})
- Return a list of langchain Document objects
- Do not load non-.md files in the base implementation
```

### 2.2 — Embedder

```
Refer to SPEC.md § 3 and § 5 for collection name and embedding model.

Create app/ingestion/embedder.py.
Requirements:
- Use langchain-chroma ChromaDB with the collection name from settings
- Use langchain-openai OpenAIEmbeddings pointed at the LiteLLM proxy
- Expose these functions: get_vector_store(), get_collection_count(), embed_documents(docs)
- ChromaDB must persist to settings.chroma_path
- embed_documents must delete the existing collection before re-ingesting (idempotent re-run)
```

### 2.3 — Ingestion CLI

```
Create scripts/ingest.py.
Requirements:
- Call document_loader.load_documents() then embedder.embed_documents()
- Print a summary: how many documents loaded, how many chunks created, total time
- Exit with code 1 on any exception
- No argparse needed — all config comes from .env
```

---

## Prompt Sequence 3 — Pipeline Agents

### 3.1 — Query Understanding Agent

```
Refer to SPEC.md § 1.1 for the exact input/output contract and intent taxonomy.

Create app/agents/query_understanding.py.
Requirements:
- Input: dict with key "raw_query" (str)
- Output: QueryContext (from app.models.schemas)
- Use ChatPromptTemplate with system + human messages as specified in docs/prompt.md
- Temperature: 0
- Parse the LLM JSON response; on parse failure retry once with the retry prompt
- If second attempt also fails, default intent to "UNKNOWN" and reformulated_query to raw_query
- Expose a run(input: dict) -> QueryContext function
```

### 3.2 — Search Agent

```
Refer to SPEC.md § 1.2 for search parameters and scoring.

Create app/agents/search_agent.py.
Requirements:
- Input: QueryContext (from app.models.schemas)
- Output: SearchResult
- Use reformulated_query for the similarity search
- Convert ChromaDB L2 distance to similarity: score = 1 / (1 + distance)
- Respect top_k from the context if present, else use settings.top_k
- Expose a run(input: QueryContext) -> SearchResult function
```

### 3.3 — Answer Generator Agent

```
Refer to SPEC.md § 1.3 for the prompt contract and has_answer logic.

Create app/agents/answer_generator.py.
Requirements:
- Input: SearchResult
- Output: GeneratedAnswer
- Build context string from chunks (content only, separated by ----)
- Temperature: 0.3
- Detect the "I don't have enough information" sentinel and set has_answer=False
- Expose a run(input: SearchResult) -> GeneratedAnswer function
```

### 3.4 — Source Linker Agent

```
Refer to SPEC.md § 1.4 for deduplication and sort rules.

Create app/agents/source_linker.py.
Requirements:
- Input: GeneratedAnswer
- Output: dict (as specified in SPEC.md § 1.4 Output)
- Deduplicate by source filename — keep the chunk with the highest score per file
- Sort sources by score descending
- Convert each unique chunk to a SourceLink Pydantic model
- Expose a run(input: GeneratedAnswer) -> dict function
```

---

## Prompt Sequence 4 — Pipeline Wiring

### 4.1 — LCEL Chain

```
Refer to SPEC.md § 6 (Pipeline Wiring).

Create app/core/pipeline.py.
Requirements:
- Wire the 4 agents into a sequential LCEL chain using RunnableLambda exactly
  as shown in SPEC.md § 6
- Expose run_pipeline(question: str, top_k: int | None = None) -> QueryResponse
- Measure wall-clock time and populate processing_time_ms
- Log pipeline completion time at INFO level
```

---

## Prompt Sequence 5 — FastAPI Backend

### 5.1 — Routes

```
Refer to SPEC.md § 4 (API Contracts).

Create app/api/routes.py with exactly these endpoints:
  POST /query       — calls run_pipeline; returns QueryResponse
  GET  /health      — returns HealthResponse
  GET  /documents   — returns DocumentListResponse (deduplicated by source)
  GET  /documents/view/{filename} — serves raw document as HTML

Security: the /documents/view/{filename} handler MUST prevent path traversal.
Resolve the target path and confirm it starts with the resolved docs_dir before opening.
Return HTTP 400 if path traversal is detected.
```

### 5.2 — App Entry Point

```
Create app/main.py.
Requirements:
- Create FastAPI app with title "Internal Knowledge Base Navigator"
- Add CORS middleware allowing all origins (demo environment)
- Use lifespan context manager to load the vector store at startup
- Include the router from app.api.routes
- Log startup confirmation including collection chunk count
```

---

## Prompt Sequence 6 — Streamlit Frontend

### 6.1 — Chat UI

```
Refer to docs/ui-instructions.md and docs/design-tokens.md for visual spec.

Create frontend/app.py.
Requirements:
- Use st.session_state to maintain conversation history across reruns
- Render each assistant message with: answer text, intent chip (colored by intent class),
  and source cards (title, score as %, "View Document" link)
- Sidebar: API health indicator (green/red dot), document list from GET /documents,
  "Clear conversation" button
- POST to http://localhost:8000/query with {"question": ..., "top_k": 5}
- Show a spinner while waiting for the API response
- Handle API errors gracefully — show an error message, do not crash
```

---

## Prompt Sequence 7 — Tests

### 7.1 — Pipeline Unit Tests

```
Refer to SPEC.md §§ 1.1–1.4 for expected inputs and outputs.

Create tests/test_pipeline.py.
Write pytest tests for:
  - query_understanding.run() returns a QueryContext with the correct intent for
    a sample query about annual leave
  - search_agent.run() returns a SearchResult with at least 1 chunk
  - answer_generator.run() returns a GeneratedAnswer with has_answer=True for a
    context-rich SearchResult
  - source_linker.run() returns deduplicated sources sorted by score
  - run_pipeline() end-to-end returns a QueryResponse with intent and sources

Use real LLM calls (no mocking) — these are smoke tests, not unit tests.
Mark tests that require the LLM with @pytest.mark.integration if isolation is needed.
```

### 7.2 — API Integration Tests

```
Refer to SPEC.md § 4 (API Contracts) for expected response shapes.

Create tests/test_api.py.
Write pytest tests for:
  - GET /health returns {"status": "ok"} and vector_store_docs > 0
  - POST /query with a valid question returns 200 with all required fields
  - POST /query with an empty question returns 422
  - GET /documents returns total_documents >= 1
Use httpx.AsyncClient with the FastAPI TestClient pattern (pytest-asyncio).
```

---

## Prompt Sequence 8 — Polish

### 8.1 — README

```
Rewrite README.md as the definitive repo entry point.
Include:
  1. One-paragraph description of what the project does
  2. Architecture diagram (ASCII)
  3. Tech stack table
  4. Quick Start: install → configure .env → ingest → run backend → run frontend
  5. API reference table (3 endpoints + descriptions)
  6. Current phase status (Phase X of 7)
  7. Links to: SPEC.md, PLAN.md, DEMO_GUIDE.md
Keep it under 150 lines. No marketing language.
```

---

## Prompt Anti-Patterns (Do Not Use)

| Anti-pattern | Why it fails |
|-------------|-------------|
| "Build the whole app" | Too large; Copilot hallucinates missing details |
| "Add authentication" | Not in scope; will trigger scope creep |
| "Make it better" | Vague; produces unrequested refactoring |
| Starting a prompt without citing SPEC.md | Copilot will invent contracts that differ from the spec |
| Asking for streaming before the pipeline is tested | Streaming requires async rewrite; wait for Phase 6 gate |
