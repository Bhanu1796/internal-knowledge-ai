# Document Ingestion

## Overview

The ingestion pipeline converts raw knowledge base files (Markdown, PDF, DOCX, TXT) into searchable vector embeddings stored in ChromaDB. It must be run once before the API can answer questions, and re-run whenever the knowledge base content changes.

---

## Running Ingestion

```bash
python scripts/ingest.py
```

Optional flags:

```bash
# Ingest from a custom directory
python scripts/ingest.py --docs-path /path/to/your/docs

# Wipe and rebuild the collection (default behaviour)
python scripts/ingest.py --reset

# Append new documents without clearing existing ones
python scripts/ingest.py --no-reset
```

---

## Ingestion Pipeline Steps

```
data/sample_docs/
  *.md / *.pdf / *.docx / *.txt
        │
        ▼  Step 1: Load
  DocumentLoader
  (LangChain loaders per file type)
        │
        ▼  Step 2: Chunk
  RecursiveCharacterTextSplitter
  chunk_size=800, overlap=100
        │
        ▼  Step 3: Enrich Metadata
  Attach: source, doc_url, title, chunk_id
        │
        ▼  Step 4: Embed
  OpenAIEmbeddings (text-embedding-3-small)
        │
        ▼  Step 5: Persist
  ChromaDB collection: "knowledge_base"
  Path: ./chroma_db/
```

---

## Step 1 — Document Loading (`app/ingestion/document_loader.py`)

Files are loaded from the configured `DOCS_PATH` directory. The loader automatically selects the correct LangChain loader based on file extension:

| Extension | Loader |
|---|---|
| `.md` | `UnstructuredMarkdownLoader` |
| `.pdf` | `PyPDFLoader` (page-aware) |
| `.docx` | `Docx2txtLoader` |
| `.txt` | `TextLoader` (UTF-8) |

Files with unsupported extensions are skipped with a warning.

---

## Step 2 — Chunking

Documents are split using `RecursiveCharacterTextSplitter` with the following hierarchy of separators:

```
["\n\n", "\n", ". ", " ", ""]
```

This ensures chunks respect paragraph and sentence boundaries wherever possible.

| Parameter | Default | Environment Variable |
|---|---|---|
| `chunk_size` | `800` tokens | `CHUNK_SIZE` |
| `chunk_overlap` | `100` tokens | `CHUNK_OVERLAP` |

---

## Step 3 — Metadata Enrichment

Each chunk is tagged with structured metadata before embedding. This metadata is stored alongside the vector in ChromaDB and returned with search results.

```python
{
    "source": "it-software-request.md",       # Original filename
    "title": "IT Software Request Policy",     # Derived from filename
    "doc_url": "https://confluence.internal/pages/it-software-request",  # Simulated URL
    "page": 2,                                 # Page index (PDF) or chunk sequence (others)
    "chunk_id": "it-software-request.md_2_0"  # filename_page_chunkIndex
}
```

### URL Generation
Since documents are local files simulating a Confluence/SharePoint export, URLs are generated deterministically from the filename:

```
it-software-request.md  →  https://confluence.internal/pages/it-software-request
annual-leave-policy.md  →  https://confluence.internal/pages/annual-leave-policy
```

The base URL (`https://confluence.internal/pages/`) is configurable via `DOC_BASE_URL` in `.env`.

---

## Step 4 — Embedding

Chunks are embedded in batches of 100 using the OpenAI `text-embedding-3-small` model.

- Embedding dimensions: **1536**
- Distance metric: **cosine similarity**
- Batching prevents rate-limit errors on large collections

---

## Step 5 — Persistence (ChromaDB)

Vectors and metadata are written to the ChromaDB persistent collection `knowledge_base` at the path defined by `CHROMA_DB_PATH` (default: `./chroma_db/`).

On `--reset` (default), the collection is deleted and recreated to ensure a clean state. On `--no-reset`, new documents are upserted by `chunk_id` (duplicates are overwritten, new chunks are appended).

---

## Sample Knowledge Base Documents

The `data/sample_docs/` directory ships with 8 sample documents that simulate a company's Confluence knowledge base:

| File | Title | Topics Covered |
|---|---|---|
| `annual-leave-policy.md` | Annual Leave Policy | Leave entitlement, accrual, approval process |
| `it-software-request.md` | IT Software Request Policy | Software request steps, approval chain, portal link |
| `onboarding-guide.md` | Employee Onboarding Guide | First week checklist, system access, key contacts |
| `expense-reimbursement.md` | Expense Reimbursement Policy | Eligible expenses, submission process, approval limits |
| `remote-work-policy.md` | Remote Work Policy | Eligibility, equipment, security requirements |
| `code-of-conduct.md` | Code of Conduct | Workplace behaviour, ethics, reporting misconduct |
| `performance-review-process.md` | Performance Review Process | Review cycle, self-assessment, rating criteria |
| `security-guidelines.md` | IT Security Guidelines | Password policy, phishing awareness, data handling |

---

## Adding Your Own Documents

1. Place files in `data/sample_docs/` (or a custom directory)
2. Supported formats: `.md`, `.pdf`, `.docx`, `.txt`
3. Run the ingestion script:
   ```bash
   python scripts/ingest.py
   ```
4. Restart or reload the FastAPI backend

---

## Verifying Ingestion

After ingestion, confirm the collection is populated:

```bash
curl http://localhost:8000/documents
```

Or check via the Python client:

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("knowledge_base")
print(f"Total chunks: {collection.count()}")
```

---

## Ingestion Logs

The script prints progress at each step:

```
[Ingest] Loading documents from data/sample_docs/ ...
[Ingest] Loaded 8 documents
[Ingest] Splitting into chunks (size=800, overlap=100) ...
[Ingest] Created 47 chunks
[Ingest] Resetting ChromaDB collection 'knowledge_base' ...
[Ingest] Embedding and storing chunks (batch_size=100) ...
[Ingest] Batch 1/1: 47 chunks embedded
[Ingest] Done. Collection 'knowledge_base' contains 47 documents.
[Ingest] Time elapsed: 8.4s
```

---

## Troubleshooting

### `openai.AuthenticationError`
Ensure `OPENAI_API_KEY` is set in `.env` and the key is valid.

### `FileNotFoundError: data/sample_docs/`
The docs directory must exist. Create it and add at least one file before running ingestion.

### Chunks are too large / too small
Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` in `.env`. Re-run ingestion after changes.

### PDF text is garbled or missing
Some scanned PDFs require OCR. Replace `PyPDFLoader` with `UnstructuredPDFLoader` (install `unstructured[pdf]`) for OCR-capable loading.
