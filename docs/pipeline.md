# Sequential RAG Pipeline

## Overview

The core of this application is a **4-stage Sequential Pipeline** implemented using LangChain LCEL (LangChain Expression Language). Each stage is a dedicated agent module. The output of every stage feeds directly into the next, forming a linear data-processing chain.

```
Raw Query
    │
    ▼  Stage 1
Query Understanding Agent  →  QueryContext
    │
    ▼  Stage 2
Search Agent               →  SearchResult
    │
    ▼  Stage 3
Answer Generator Agent     →  GeneratedAnswer
    │
    ▼  Stage 4
Source Linker Agent        →  List[SourceLink]
    │
    ▼
Final Response { answer, sources }
```

---

## Stage 1 — Query Understanding (`app/agents/query_understanding.py`)

### Purpose
Parse the raw employee question to determine **intent** and produce a **retrieval-optimised reformulation** of the query. This improves search recall by removing filler words, expanding acronyms, and making implicit context explicit.

### Input
```json
{ "raw_query": "what's the process to request new software?" }
```

### Processing
1. The raw query is sent to the LLM with a structured system prompt requesting:
   - **Intent classification** — e.g., `PROCESS_INQUIRY`, `POLICY_LOOKUP`, `CONTACT_LOOKUP`, `GENERAL_INFO`
   - **Reformulated query** — a clean, keyword-rich sentence for embedding-based search
   - **Key entities** — extracted nouns/topics (used for metadata filtering)

2. The LLM response is parsed into a `QueryContext` Pydantic model.

### Output — `QueryContext`
```python
class QueryContext(BaseModel):
    raw_query: str
    intent: str                   # e.g. "PROCESS_INQUIRY"
    reformulated_query: str       # e.g. "software request approval process IT department"
    key_entities: List[str]       # e.g. ["software", "IT", "request"]
```

### Example Transformation
| Field | Value |
|---|---|
| `raw_query` | `"what's the process to request new software?"` |
| `intent` | `PROCESS_INQUIRY` |
| `reformulated_query` | `"software request approval process IT department steps"` |
| `key_entities` | `["software", "IT request", "approval"]` |

---

## Stage 2 — Search Agent (`app/agents/search_agent.py`)

### Purpose
Perform **semantic similarity search** against the ChromaDB vector store using the reformulated query. Returns the most relevant document chunks with their metadata.

### Input
`QueryContext` (from Stage 1)

### Processing
1. The `reformulated_query` string is embedded using `OpenAIEmbeddings` pointed at the LiteLLM proxy (`text-embedding-3-large`)
2. ChromaDB performs cosine-similarity search against all stored chunk embeddings
3. The top `k` results (default: `5`, configurable via `SEARCH_TOP_K` in `.env`) are returned
4. Each result includes the chunk text, similarity score, and metadata

### Output — `SearchResult`
```python
class DocumentChunk(BaseModel):
    chunk_id: str
    content: str           # The actual text excerpt
    source: str            # File name, e.g. "it-software-policy.md"
    doc_url: str           # Simulated Confluence/SharePoint URL
    page: int              # Page or section number
    score: float           # Cosine similarity score (0.0 – 1.0)

class SearchResult(BaseModel):
    query_context: QueryContext
    chunks: List[DocumentChunk]
```

### Relevance Threshold
Chunks with a similarity score below `SEARCH_MIN_SCORE` (default: `0.30`) are filtered out to avoid including irrelevant context in the answer generation step.

---

## Stage 3 — Answer Generator (`app/agents/answer_generator.py`)

### Purpose
Use the LLM to synthesise a **concise, direct answer** from the retrieved document chunks. The LLM is instructed to only use information present in the retrieved context (no hallucination outside the knowledge base).

### Input
`SearchResult` (from Stage 2), which carries `QueryContext` and `chunks`

### Processing
1. Retrieved chunks are assembled into a context block:
   ```
   [Source: it-software-policy.md | Page 2]
   To request new software, employees must submit a ticket via the IT portal...

   [Source: onboarding-guide.md | Page 5]
   New software requests require manager approval before IT processing...
   ```
2. A prompt is constructed:
   - **System**: "You are a helpful internal knowledge base assistant. Answer using ONLY the provided context. If the context does not contain enough information, say so."
   - **Human**: Context block + original `raw_query`
3. The LLM (`gpt-4o`) generates the answer
4. Response is parsed into `GeneratedAnswer`

### Output — `GeneratedAnswer`
```python
class GeneratedAnswer(BaseModel):
    search_result: SearchResult    # Passed through for Stage 4
    answer_text: str               # The LLM-synthesised answer
    has_answer: bool               # False if LLM indicated no relevant info found
```

### Fallback Behaviour
If `chunks` is empty (no relevant documents found), Stage 3 skips the LLM call and returns:
```json
{
  "answer_text": "I could not find relevant information in the knowledge base for your query.",
  "has_answer": false
}
```

---

## Stage 4 — Source Linker (`app/agents/source_linker.py`)

### Purpose
Collect the **unique source documents** referenced by the retrieved chunks and format them as structured links for display in the UI.

### Input
`GeneratedAnswer` (from Stage 3)

### Processing
1. Deduplicate chunks by `source` filename
2. For each unique source, build a `SourceLink` with the document title, URL, and page reference
3. Sort by descending similarity score so the most relevant source appears first

### Output — `dict` (passed to `run_pipeline`)

The Source Linker flattens the pipeline state into a plain dict consumed by `run_pipeline()`:

```python
{
    "answer_text": str,
    "has_answer": bool,
    "intent": str,
    "sources": List[SourceLink],
    "reformulated_query": str,   # carried forward from Stage 1
    "key_entities": List[str],   # carried forward from Stage 1
    "chunks_retrieved": int,     # total chunks returned by Stage 2
}
```

Deduplication rule: if multiple chunks share the same `source` filename, only the one with the highest score is kept. Sources are then sorted by score descending.

---

## Final Response Schema

After all 4 stages complete, `run_pipeline()` assembles a `QueryResponse`:

```python
class QueryResponse(BaseModel):
    question: str
    answer: str
    intent: str
    has_answer: bool
    sources: List[SourceLink]
    processing_time_ms: int
    reformulated_query: str = ""      # Stage 1 output — surfaced in UI pipeline trace
    key_entities: List[str] = []      # Stage 1 output — surfaced in UI pipeline trace
    chunks_retrieved: int = 0         # Stage 2 output — total chunks before deduplication
```

The three additional fields (`reformulated_query`, `key_entities`, `chunks_retrieved`) are displayed in the **"How I found this"** expander in the Streamlit UI, making the 4-stage pipeline reasoning visible to the user.

---

## LCEL Chain Definition (`app/core/pipeline.py`)

The four agents are composed into a single LangChain LCEL chain:

```python
pipeline = (
    RunnableLambda(query_understanding_agent.run)
    | RunnableLambda(search_agent.run)
    | RunnableLambda(answer_generator.run)
    | RunnableLambda(source_linker.run)
)
```

To invoke the pipeline:
```python
result = pipeline.invoke({"raw_query": "What is the annual leave policy?"})
```

---

## Configuration

All pipeline parameters are controlled via environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `LITELLM_PROXY_URL` | `http://litellm.amzur.com:4000` | LiteLLM proxy base URL |
| `LITELLM_API_KEY` | — | API key for the LiteLLM proxy |
| `LLM_MODEL` | `gemini/gemini-2.5-flash` | Chat model routed via proxy |
| `LITELLM_EMBEDDING_MODEL` | `text-embedding-3-large` | Embedding model routed via proxy |
| `SEARCH_TOP_K` | `5` | Number of chunks to retrieve |
| `SEARCH_MIN_SCORE` | `0.30` | Minimum similarity score threshold |
| `CHUNK_SIZE` | `800` | Token size per document chunk |
| `CHUNK_OVERLAP` | `100` | Token overlap between consecutive chunks |

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| OpenAI API timeout | Raises `PipelineError` with `stage="answer_generator"` |
| ChromaDB unavailable | Raises `PipelineError` with `stage="search"` at startup |
| Empty search results | Stage 3 returns graceful fallback, `has_answer=False` |
| LLM refuses to answer | `has_answer=False`, message forwarded to user |
| Malformed LLM output | Pydantic validation catches and re-prompts (max 2 retries) |
