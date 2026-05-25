# Application Architecture

## Overview

The Internal Knowledge Base Navigator is a production-grade conversational AI built on a **Sequential RAG Pipeline**. Employees submit natural language questions and receive direct, concise answers with links to the source documents inside the company knowledge base.

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          User (Browser)                              │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  HTTP (REST / Streamlit)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                                │
│                    Streamlit Chat UI (Port 8501)                     │
│  • Query input field           • Streaming answer display            │
│  • Source-link cards           • Conversation history sidebar        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  REST API calls  (POST /query)
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        Backend Layer                                 │
│                    FastAPI Application (Port 8000)                   │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────────┐   │
│  │ POST /query │   │ GET /health │   │   GET /documents          │   │
│  └──────┬──────┘   └─────────────┘   └──────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Sequential RAG Pipeline (LangChain LCEL)        │    │
│  │                                                              │    │
│  │  Step 1: Query Understanding Agent                           │    │
│  │    └─► LLM extracts intent, reformulates query               │    │
│  │                    │                                         │    │
│  │  Step 2: Search Agent                                        │    │
│  │    └─► Semantic search in ChromaDB (top-k chunks)            │    │
│  │                    │                                         │    │
│  │  Step 3: Answer Generator Agent                              │    │
│  │    └─► LLM synthesises answer from retrieved context         │    │
│  │                    │                                         │    │
│  │  Step 4: Source Linker Agent                                 │    │
│  │    └─► Formats source metadata + document URLs               │    │
│  └──────────────────────────────────────────────────────────────┘    │
└───────────┬──────────────────────────────┬───────────────────────────┘
            │                              │
            ▼                              ▼
┌───────────────────────┐    ┌─────────────────────────────────────────┐
│   LLM Provider        │    │          Data Store Layer               │
│   LiteLLM Proxy       │    │  ┌──────────────────────────────────┐   │
│   litellm.amzur.com   │    │  │   ChromaDB (Vector Store)        │   │
│   • gemini-2.5-flash  │    │  │   • Persistent on disk           │   │
│   • text-embedding-   │    │  │   • Cosine similarity search     │   │
│     3-large           │    │  │   • Metadata filters             │   │
└───────────────────────┘    │  │   • Metadata filters             │   │
                             │  └──────────────────────────────────┘   │
                             │  ┌──────────────────────────────────┐   │
                             │  │   Document Store (File System)   │   │
                             │  │   data/sample_docs/              │   │
                             │  │   • Markdown / PDF / DOCX / TXT  │   │
                             │  └──────────────────────────────────┘   │
                             └─────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend — Streamlit (`frontend/app.py`)
- Provides the chat interface accessed at `http://localhost:8501`
- Maintains conversation history in `st.session_state`
- Calls the FastAPI backend via HTTP (`POST /query`)
- Renders source cards with document titles and simulated Confluence/SharePoint URLs

### Backend — FastAPI (`app/main.py`)
- Exposes a REST API at `http://localhost:8000`
- Loads the ChromaDB vector store at startup (lifespan event)
- Passes each query through the Sequential RAG Pipeline
- Returns a structured JSON response containing the answer and source list

### Sequential RAG Pipeline (`app/core/pipeline.py`)

| Step | Agent | Responsibility |
|------|-------|---------------|
| 1 | `QueryUnderstandingAgent` | Parses the raw question, extracts intent, reformulates for retrieval |
| 2 | `SearchAgent` | Runs semantic similarity search against ChromaDB, returns top-k chunks |
| 3 | `AnswerGeneratorAgent` | Calls the LLM with the question + retrieved context to generate an answer |
| 4 | `SourceLinkerAgent` | Collects unique source document metadata and formats links |

### Vector Store — ChromaDB (`chroma_db/`)
- Persisted on disk under `chroma_db/` (git-ignored)
- Collection name: `knowledge_base`
- Each document chunk is stored with metadata: `source`, `page`, `doc_url`, `chunk_id`
- Populated by running `python scripts/ingest.py`

### LLM Provider — LiteLLM Proxy
- Proxy URL: `http://litellm.amzur.com:4000` (configurable via `LITELLM_PROXY_URL` in `.env`)
- Chat model: `gemini/gemini-2.5-flash` (configurable via `LLM_MODEL`)
- Embedding model: `text-embedding-3-large` (configurable via `LITELLM_EMBEDDING_MODEL`)
- Both accessed through LangChain's `ChatOpenAI` and `OpenAIEmbeddings` wrappers pointed at the proxy base URL — no SDK change required

### Document Ingestion (`app/ingestion/`)
- `document_loader.py`: Loads files from `data/sample_docs/`, splits into chunks with overlap
- `embedder.py`: Embeds each chunk using OpenAI embeddings and upserts into ChromaDB
- `scripts/ingest.py`: CLI entrypoint — run once (or on new document upload)

---

## Inter-Agent Communication

```
User Query (str)
      │
      ▼
┌─────────────────────┐
│ QueryUnderstanding  │  Input : raw_query (str)
│ Agent               │  Output: QueryContext { intent, reformulated_query }
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Search Agent        │  Input : QueryContext
│                     │  Output: SearchResult { chunks: List[DocumentChunk] }
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Answer Generator    │  Input : QueryContext + SearchResult
│ Agent               │  Output: GeneratedAnswer { answer_text }
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Source Linker       │  Input : SearchResult
│ Agent               │  Output: List[SourceLink { title, url, page }]
└──────────┬──────────┘
           │
           ▼
   Final Response
   { answer, sources }
```

---

## Data Flow — Document Ingestion

```
data/sample_docs/          scripts/ingest.py
  *.md / *.pdf / *.docx  ──────────────────►  DocumentLoader
                                                    │
                                             Chunk (RecursiveCharacterTextSplitter)
                                                    │
                                             Embed  (OpenAIEmbeddings)
                                                    │
                                             Upsert (ChromaDB)
```

---

## Deployment Topology (Local Development)

```
localhost:8501  ──►  Streamlit  ──►  localhost:8000  ──►  FastAPI + Pipeline
                                                                │
                                                         OpenAI API (cloud)
                                                                │
                                                         ChromaDB (local disk)
```

---

## Technology Choices — Rationale

| Technology | Reason |
|---|---|
| **LangChain LCEL** | Explicit sequential chain mirrors the project's Sequential-Pipeline workflow requirement; composable, testable stages |
| **ChromaDB** | Persistent local vector store — no extra infrastructure, easy reset for demos |
| **FastAPI** | Production-grade async REST framework, auto-generates OpenAPI docs |
| **Streamlit** | Fastest path to a polished chat demo UI in pure Python |
| **LiteLLM Proxy** | Unified OpenAI-compatible proxy at `litellm.amzur.com` — routes to Gemini, enables model swapping without code changes |
| **Gemini 2.5 Flash** | Fast, cost-efficient model routed via LiteLLM proxy |
| **pydantic-settings** | Type-safe, validated environment configuration with `.env` support |
