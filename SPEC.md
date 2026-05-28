# SPEC.md
## Technical Specification — Internal Knowledge Base Navigator

> This is the single source of truth for agent contracts, I/O schemas, data model, and API contracts. Implementation must not deviate from this document.

---

## 1. Agent Specifications

### 1.1 Query Understanding Agent

**File:** `app/agents/query_understanding.py`
**Role:** Stage 1 of the pipeline. Parses the raw employee question and produces a structured context object for downstream retrieval.

**Input:**
```python
{"raw_query": str, "top_k": int | None}
```

**Output:**
```python
QueryContext(
    raw_query=str,          # original question, unchanged
    intent=str,             # one of 5 intent classes (see below)
    reformulated_query=str, # retrieval-optimised rewrite
    key_entities=list[str]  # up to 5 extracted topics
)
```

**Intent taxonomy:**

| Class | Trigger pattern |
|-------|----------------|
| `PROCESS_INQUIRY` | "How do I…", "Steps to…", "What is the process for…" |
| `POLICY_LOOKUP` | "What is the policy…", "Am I allowed to…", "What are the rules…" |
| `CONTACT_LOOKUP` | "Who do I contact…", "Who is responsible for…", "Who approves…" |
| `GENERAL_INFO` | "What is…", "Tell me about…", factual questions |
| `UNKNOWN` | Cannot be classified into any above category |

**Retry logic:** If the LLM returns invalid JSON, the agent retries once with an explicit retry prompt before raising.
**Temperature:** 0 (deterministic)

---

### 1.2 Search Agent

**File:** `app/agents/search_agent.py`
**Role:** Stage 2. Performs semantic similarity search against ChromaDB and returns the top-K matching chunks.

**Input:**
```python
QueryContext  # output of Stage 1
```

**Output:**
```python
SearchResult(
    query_context=QueryContext,
    chunks=list[DocumentChunk]  # ordered by relevance score descending
)
```

**Search parameters:**

| Parameter | Default | Override |
|-----------|---------|---------|
| `top_k` | 5 | `QueryRequest.top_k` (1–20) |
| Distance metric | cosine | Fixed — set at collection creation |
| Query text | `QueryContext.reformulated_query` | — |

**Chunk scoring:** ChromaDB returns L2 distances; these are converted to a [0, 1] similarity score: `score = 1 / (1 + distance)`.

---

### 1.3 Answer Generator Agent

**File:** `app/agents/answer_generator.py`
**Role:** Stage 3. Calls the LLM with the reformulated question and retrieved context to produce a grounded answer.

**Input:**
```python
SearchResult  # output of Stage 2
```

**Output:**
```python
GeneratedAnswer(
    search_result=SearchResult,  # passed through unchanged
    answer_text=str,             # synthesised answer
    has_answer=bool              # False if no relevant context found
)
```

**Prompt contract:**
- System prompt instructs the LLM to answer only from the provided context
- If context is insufficient, the LLM must return "I don't have enough information in the knowledge base to answer that question."
- `has_answer` is set to `False` when that sentinel phrase is detected

**Temperature:** 0.3 (slight variation for natural language fluency)

---

### 1.4 Source Linker Agent

**File:** `app/agents/source_linker.py`
**Role:** Stage 4 (final). Deduplicates document chunks by source file, ranks them, and formats source link objects.

**Input:**
```python
GeneratedAnswer  # output of Stage 3
```

**Output:**
```python
dict  # flattened — consumed directly by run_pipeline()
{
    "answer_text": str,
    "intent": str,
    "has_answer": bool,
    "sources": list[SourceLink]
}
```

**Deduplication rule:** If multiple chunks from the same `source` file are returned, keep the chunk with the highest score. One `SourceLink` per unique source file.
**Sort order:** Sources sorted by `score` descending.

---

## 2. Data Model

### 2.1 Pipeline-Internal Models (`app/models/schemas.py`)

```python
class QueryContext(BaseModel):
    raw_query: str
    intent: str = "UNKNOWN"
    reformulated_query: str
    key_entities: List[str]

class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    source: str        # filename, e.g. "annual-leave-policy.md"
    doc_url: str       # e.g. "http://localhost:8000/documents/view/annual-leave-policy.md"
    page: int          # 0-indexed chunk page number
    score: float       # [0, 1] similarity score

class SearchResult(BaseModel):
    query_context: QueryContext
    chunks: List[DocumentChunk]

class GeneratedAnswer(BaseModel):
    search_result: SearchResult
    answer_text: str
    has_answer: bool = True
```

### 2.2 API Models (`app/models/schemas.py`)

```python
class QueryRequest(BaseModel):
    question: str           # 1–2000 characters
    top_k: Optional[int]    # 1–20, defaults to settings.top_k (5)

class SourceLink(BaseModel):
    title: str
    url: str
    source_file: str
    page: int
    score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    intent: str
    has_answer: bool
    sources: List[SourceLink]
    processing_time_ms: int
    reformulated_query: str = ""       # query after Stage 1 reformulation
    key_entities: List[str] = []       # extracted topics from Stage 1
    chunks_retrieved: int = 0          # total chunks returned by Stage 2

class DocumentInfo(BaseModel):
    title: str
    source_file: str
    url: str
    chunk_count: int

class DocumentListResponse(BaseModel):
    total_chunks: int
    total_documents: int
    documents: List[DocumentInfo]

class HealthResponse(BaseModel):
    status: str              # "ok" or "error"
    vector_store_docs: int
```

---

## 3. Vector Store Schema

**Collection name:** `knowledge_base`
**Embedding model:** `text-embedding-3-large` (3072 dimensions)
**Distance metric:** cosine

**Chunk metadata fields:**

| Field | Type | Description |
|-------|------|-------------|
| `source` | str | Filename of the originating document |
| `title` | str | Human-readable document title |
| `doc_url` | str | URL to view the document in browser |
| `page` | int | 0-indexed chunk sequence number within the document |
| `chunk_id` | str | `{source}_{page}` |

**Chunking parameters:**

| Parameter | Value |
|-----------|-------|
| `chunk_size` | 500 tokens |
| `chunk_overlap` | 50 tokens |
| Splitter | `RecursiveCharacterTextSplitter` |

---

## 4. API Contracts

**Base URL:** `http://localhost:8000`

### 4.1 `POST /query`

**Request:**
```json
{
  "question": "What is the annual leave policy?",
  "top_k": 5
}
```

**Response (200 OK):**
```json
{
  "question": "What is the annual leave policy?",
  "answer": "Full-time employees are entitled to 20 working days of paid annual leave per year...",
  "intent": "POLICY_LOOKUP",
  "has_answer": true,
  "sources": [
    {
      "title": "Annual Leave Policy",
      "url": "http://localhost:8000/documents/view/annual-leave-policy.md",
      "source_file": "annual-leave-policy.md",
      "page": 0,
      "score": 0.94
    }
  ],
  "processing_time_ms": 3241,
  "reformulated_query": "annual leave entitlement days employee policy",
  "key_entities": ["annual leave", "entitlement", "policy"],
  "chunks_retrieved": 5
}
```

**Response (500 Internal Server Error):**
```json
{"detail": "Pipeline error: <message>"}
```

---

### 4.2 `GET /health`

**Response (200 OK):**
```json
{
  "status": "ok",
  "vector_store_docs": 35
}
```

---

### 4.3 `GET /documents`

**Response (200 OK):**
```json
{
  "total_chunks": 35,
  "total_documents": 8,
  "documents": [
    {
      "title": "Annual Leave Policy",
      "source_file": "annual-leave-policy.md",
      "url": "http://localhost:8000/documents/view/annual-leave-policy.md",
      "chunk_count": 5
    }
  ]
}
```

---

### 4.4 `GET /documents/view/{filename}`

**Path parameter:** `filename` — e.g. `annual-leave-policy.md`
**Security:** Path traversal prevention — the resolved path must remain inside `settings.docs_path`.
**Response:** `200 OK` with `Content-Type: text/html` — rendered document content.
**Errors:** `400 Bad Request` for path traversal attempts; `404 Not Found` if file does not exist.

---

## 5. Configuration (`app/core/config.py`)

All settings loaded from `.env` via `pydantic-settings`:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LITELLM_API_KEY` | str | required | API key for the LiteLLM proxy |
| `LITELLM_PROXY_URL` | str | `http://litellm.amzur.com:4000` | Proxy base URL |
| `LLM_MODEL` | str | `gemini-2.5-flash` | Model name for answer generation |
| `EMBEDDING_MODEL` | str | `text-embedding-3-large` | Model name for embeddings |
| `CHROMA_PATH` | str | `./chroma_db` | Path to ChromaDB persistence directory |
| `DOCS_PATH` | str | `./data/sample_docs` | Path to raw document files |
| `TOP_K` | int | `5` | Default number of chunks to retrieve |
| `COLLECTION_NAME` | str | `knowledge_base` | ChromaDB collection name |

---

## 6. Pipeline Wiring (`app/core/pipeline.py`)

```python
pipeline = (
    RunnableLambda(query_understanding.run)   # dict → QueryContext
    | RunnableLambda(search_agent.run)        # QueryContext → SearchResult
    | RunnableLambda(answer_generator.run)    # SearchResult → GeneratedAnswer
    | RunnableLambda(source_linker.run)       # GeneratedAnswer → dict
)
```

**Invariant:** Each agent function receives the output of the previous step. No agent reaches back to an earlier stage's output directly — all needed data is carried forward by the model objects.
