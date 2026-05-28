# API Reference

Base URL: `http://localhost:8000`

Interactive Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### `GET /health`

Returns the current health status of the API and the number of documents indexed in the vector store.

**Request**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response — 200 OK**
```json
{
  "status": "ok",
  "vector_store_docs": 47
}
```

**Response fields**

| Field | Type | Description |
|---|---|---|
| `status` | `string` | Always `"ok"` when the service is healthy |
| `vector_store_docs` | `integer` | Number of chunks currently indexed in ChromaDB |

---

### `POST /query`

Submit a natural language question and receive a direct answer with source document links.

**Request**
```http
POST /query HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

**Request Body**
```json
{
  "question": "What is the process to request new software?",
  "top_k": 5
}
```

**Request fields**

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `question` | `string` | Yes | — | The natural language question from the employee |
| `top_k` | `integer` | No | `5` | Override the number of document chunks to retrieve (1–20) |

**Response — 200 OK**
```json
{
  "question": "What is the process to request new software?",
  "answer": "To request new software, employees must submit a ticket through the IT Portal at it-portal.internal.com. The request requires manager approval and is typically processed within 3–5 business days. Licences for standard software (e.g., Microsoft Office, Zoom) are pre-approved; non-standard software requires an additional security review.",
  "intent": "PROCESS_INQUIRY",
  "has_answer": true,
  "sources": [
    {
      "title": "IT Software Request Policy",
      "url": "http://localhost:8000/documents/view/it-software-request.md",
      "source_file": "it-software-request.md",
      "page": 2,
      "score": 0.89
    },
    {
      "title": "Employee Onboarding Guide",
      "url": "http://localhost:8000/documents/view/onboarding-guide.md",
      "source_file": "onboarding-guide.md",
      "page": 5,
      "score": 0.71
    }
  ],
  "processing_time_ms": 1243,
  "reformulated_query": "software installation request approval process IT department",
  "key_entities": ["software", "IT request", "approval", "portal"],
  "chunks_retrieved": 5
}
```

**Response fields**

| Field | Type | Description |
|---|---|---|
| `question` | `string` | The original question as submitted |
| `answer` | `string` | LLM-synthesised answer derived from retrieved documents |
| `intent` | `string` | Classified intent: `PROCESS_INQUIRY`, `POLICY_LOOKUP`, `CONTACT_LOOKUP`, `GENERAL_INFO`, `UNKNOWN` |
| `has_answer` | `boolean` | `false` if no relevant documents were found or LLM could not form an answer |
| `sources` | `array[SourceLink]` | Ordered list of source documents used, most relevant first |
| `processing_time_ms` | `integer` | End-to-end pipeline latency in milliseconds |
| `reformulated_query` | `string` | The query after Stage 1 reformulation — keyword-rich rewrite used for vector search |
| `key_entities` | `array[string]` | Key topics and nouns extracted by Stage 1 (up to 5 items) |
| `chunks_retrieved` | `integer` | Total number of document chunks returned by Stage 2 before deduplication |

**SourceLink object**

| Field | Type | Description |
|---|---|---|
| `title` | `string` | Human-readable document title |
| `url` | `string` | Simulated Confluence/SharePoint URL |
| `source_file` | `string` | Original filename in `data/sample_docs/` |
| `page` | `integer` | Page or section number within the document |
| `score` | `float` | Best cosine similarity score (0.0–1.0) from this document |

**Response — 200 OK (no answer found)**
```json
{
  "question": "What is the wifi password at the Tokyo office?",
  "answer": "I could not find relevant information in the knowledge base for your query. Please contact your IT helpdesk directly.",
  "intent": "GENERAL_INFO",
  "has_answer": false,
  "sources": [],
  "processing_time_ms": 312
}
```

**Response — 422 Unprocessable Entity**

Returned when the request body fails validation.

```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Response — 500 Internal Server Error**
```json
{
  "detail": "Pipeline error at stage 'search': ChromaDB collection not found. Run scripts/ingest.py first."
}
```

---

### `GET /documents`

List all source documents currently indexed in the vector store (deduplicated by source file).

**Request**
```http
GET /documents HTTP/1.1
Host: localhost:8000
```

**Response — 200 OK**
```json
{
  "total_chunks": 47,
  "total_documents": 8,
  "documents": [
    {
      "title": "Annual Leave Policy",
      "source_file": "annual-leave-policy.md",
      "url": "https://confluence.internal/pages/annual-leave-policy",
      "chunk_count": 6
    },
    {
      "title": "IT Software Request Policy",
      "source_file": "it-software-request.md",
      "url": "https://confluence.internal/pages/it-software-request",
      "chunk_count": 5
    }
  ]
}
```

**Response fields**

| Field | Type | Description |
|---|---|---|
| `total_chunks` | `integer` | Total number of embedded chunks in ChromaDB |
| `total_documents` | `integer` | Number of unique source documents |
| `documents` | `array[DocumentInfo]` | List of indexed documents |

**DocumentInfo object**

| Field | Type | Description |
|---|---|---|
| `title` | `string` | Human-readable document title |
| `source_file` | `string` | Filename in `data/sample_docs/` |
| `url` | `string` | Simulated Confluence/SharePoint URL |
| `chunk_count` | `integer` | Number of chunks indexed for this document |

---

## Intent Classifications

The `intent` field in the query response uses the following values:

| Intent | Description | Example Query |
|---|---|---|
| `PROCESS_INQUIRY` | How to complete a task or follow a process | "How do I request annual leave?" |
| `POLICY_LOOKUP` | What the rules or policies say | "What is the remote work policy?" |
| `CONTACT_LOOKUP` | Who to contact for something | "Who is the HR contact for payroll?" |
| `GENERAL_INFO` | General factual questions | "When is the next performance review cycle?" |
| `UNKNOWN` | Intent could not be determined | — |

---

## Example — cURL

```bash
# Health check
curl http://localhost:8000/health

# Submit a query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the annual leave entitlement for new employees?"}'

# List indexed documents
curl http://localhost:8000/documents
```

## Example — Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

response = requests.post(
    f"{BASE_URL}/query",
    json={"question": "What is the annual leave entitlement for new employees?"}
)
data = response.json()

print(data["answer"])
for source in data["sources"]:
    print(f"  - {source['title']}: {source['url']}")
```
