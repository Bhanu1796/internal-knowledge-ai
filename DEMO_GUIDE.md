# Demo Guide — Internal Knowledge Base Navigator
### AI-Forge 2026 · Capstone Project #7

---

## Before the Demo (Checklist)

Run through this 5 minutes before the session starts.

- [ ] Backend running: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app`
- [ ] Frontend running: `streamlit run frontend/app.py --server.port 8501`
- [ ] Browser open to `http://localhost:8501`
- [ ] Sidebar shows **"API Online"** (green dot)
- [ ] Sidebar shows **8 documents / 35 chunks**
- [ ] Swagger docs open in another tab: `http://localhost:8000/docs`
- [ ] Clear the conversation (click "Clear conversation" in sidebar) so the chat is empty
- [ ] Have a terminal visible showing uvicorn logs (mentors love to see live requests)

---

## Recommended Demo Flow (10–12 minutes)

### 1 · Opening (1 min) — Explain the problem

> "Companies store critical knowledge in scattered documents — policies, guides, procedures. Employees waste time searching. This project is a conversational AI that sits on top of those documents and gives direct, sourced answers in seconds."

Point to the sidebar:
- Show the document count (8 documents, 35 chunks ingested)
- Explain it is connected to a live FastAPI backend

---

### 2 · Live Query Demo (5–6 min) — Run these queries in order

Run each query and narrate what is happening on screen.

#### Query 1 — Basic policy lookup
```
What is the annual leave policy?
```
**Narrate:** "The system first classifies the intent — POLICY_LOOKUP — then rewrites the question for better search, retrieves the most relevant chunks from ChromaDB, and passes them to Gemini to synthesise a clean answer. Notice the source card at the bottom — you can click 'View Document' to read the original file."

**What to show:** The intent chip ("POLICY_LOOKUP"), the source card with relevance %, the "View Document" link.

---

#### Query 2 — Multi-step procedure
```
How do I request new software for my team?
```
**Narrate:** "This is a PROCEDURE_LOOKUP intent. The answer comes from the IT Software Request document. The pipeline found the right document out of 8, without any keyword matching — purely by semantic similarity."

**What to show:** Intent chip changes to PROCEDURE_LOOKUP, different source document.

---

#### Query 3 — Factual / numeric question
```
How many days of sick leave are employees entitled to?
```
**Narrate:** "Even specific factual questions get precise answers because the retrieval is grounded in the actual documents. There is no hallucination — if the document says 10 days, the answer says 10 days, and the source is linked."

---

#### Query 4 — Borderline / unknown (shows graceful degradation)
```
What is the company's policy on cryptocurrency investments?
```
**Narrate:** "The system is honest when it does not know. It will not hallucinate an answer. This is the `has_answer: false` branch in the pipeline — the answer generator is instructed to say so when the retrieved chunks do not contain relevant information."

---

#### Query 5 — Multi-document question (optional, if time allows)
```
What happens during the first week of onboarding and what security guidelines should a new employee follow?
```
**Narrate:** "This question spans two documents — the Onboarding Guide and Security Guidelines. The search agent retrieves chunks from both, and the answer generator synthesises them into a single coherent response."

---

### 3 · Architecture Walkthrough (2–3 min)

Switch to the terminal showing uvicorn logs. Point to a recent `POST /query` log line.

Explain the four pipeline stages:

| Stage | What it does | Technology |
|---|---|---|
| ① Query Understanding | Classifies intent, rewrites query | LLM (Gemini 2.5 Flash via LangChain) |
| ② Search Agent | Finds top-K relevant chunks | ChromaDB cosine similarity + text-embedding-3-large |
| ③ Answer Generator | Synthesises answer from chunks | LLM with grounding prompt |
| ④ Source Linker | Deduplicates, ranks, links sources | Pure Python post-processing |

> "Each stage is a LangChain Runnable, and they are chained with LCEL (LangChain Expression Language). This makes the pipeline easy to test — each stage is independently unit-tested with mocks."

---

### 4 · API & Tests (1–2 min)

Switch to `http://localhost:8000/docs`.

- Show the three endpoints: `/health`, `/query`, `/documents`
- Do a live try-it-out on `/health` — show the JSON response

Then briefly show the terminal:
```bash
python -m pytest tests/ -v
```
Point out: **15/15 tests passing** — unit tests for every pipeline stage, integration tests for every API endpoint, all external calls mocked.

---

## Anticipated Mentor Questions & Strong Answers

### Architecture & Design

**Q: Why did you choose ChromaDB over other vector stores like Pinecone or FAISS?**
> "ChromaDB runs locally with zero infrastructure — no API key, no cloud account, no cost. For a capstone prototype it's ideal. The interface is the same as Pinecone; swapping it out would require changing one file. FAISS is faster for very large corpora but has no built-in persistence or metadata filtering."

---

**Q: Why LangChain? Could you have done this without it?**
> "Yes — the pipeline is simple enough to write without LangChain. I used LCEL specifically because it gives a clean `chain = A | B | C` syntax and built-in tracing. The real value is that it made the stages independently testable as Runnables. In production you could replace it with plain Python functions."

---

**Q: What is the difference between semantic search and keyword search? Why use embeddings?**
> "Keyword search matches exact words. If the document says 'annual leave' but the user asks about 'vacation days', keyword search fails. Embeddings convert both into vectors in a high-dimensional semantic space — similar meanings land close together. The cosine distance between those vectors gives a relevance score regardless of the exact words used."

---

**Q: What does top_k mean? Why is it set to 5?**
> "`top_k` is how many chunks the search agent retrieves from ChromaDB — the top 5 most semantically similar chunks to the question. Those chunks become the context the LLM uses to generate the answer. 5 is the default: low enough to avoid noise, high enough to cover multi-part questions. You can change it live using the sidebar slider — lower (e.g. 3) is faster but may miss context; higher (e.g. 10) gives more material but risks including weakly related chunks."

---

**Q: How does the retrieval threshold work? What is 0.30?**
> "The search agent filters out chunks below a cosine similarity score of 0.30. Below that threshold the chunk is probably noise. The threshold was chosen empirically — too high and you miss relevant chunks, too low and you include irrelevant ones that confuse the answer generator."

---

**Q: What is LCEL (LangChain Expression Language)?**
> "LCEL is LangChain's pipe-operator syntax for chaining Runnables: `chain = prompt | llm | parser`. Each `|` passes the output of the left side as input to the right side. It also gives automatic streaming, async support, and a `.invoke()` / `.stream()` interface."

---

**Q: Why split documents into chunks? Why not pass the whole document to the LLM?**
> "Two reasons. First, LLMs have a context window limit — large documents exceed it. Second, retrieving the whole document for a narrow question includes a lot of irrelevant text that dilutes the answer. Chunks of ~500 tokens give the LLM just the relevant section."

---

**Q: What are those numbers next to each document in the sidebar?**
> "Those are the chunk counts per document — how many chunks that document was split into during ingestion. A longer document produces more chunks, a shorter one fewer. For example, a document showing '5' was split into 5 chunks of roughly 500 tokens each. All chunk counts add up to 35, which is the total shown at the top of the sidebar."

---

### Implementation Details

**Q: Will refreshing the page clear the conversation?**
> "Yes. The conversation history is stored in Streamlit's `st.session_state`, which lives only in the browser tab's session. A full page refresh (F5) resets it and the chat starts empty. To clear intentionally without refreshing, use the 'Clear conversation' button in the sidebar — it resets only the messages via `st.rerun()` without losing the API connection status or document list."

---

**Q: How does query understanding work?**
> "It sends the user's raw question to the LLM with a structured prompt asking it to (a) classify intent into one of five categories — POLICY_LOOKUP, PROCEDURE_LOOKUP, FACTUAL_QUERY, GENERAL_QUESTION, UNKNOWN — and (b) rewrite the question into a cleaner search query. The rewritten query is what gets embedded and searched."

---

**Q: How are sources linked back to documents?**
> "Each chunk stored in ChromaDB has metadata — the source filename, chunk index, and original text. After the LLM generates an answer, the Source Linker stage takes the retrieved chunks, deduplicates by filename, sorts by relevance score, and builds URLs pointing to a `/documents/view/{filename}` endpoint on the FastAPI backend that serves the raw file as HTML."

---

**Q: What happens if the LLM hallucinates?**
> "The answer generator prompt explicitly instructs the model: 'Answer only from the provided context. If the context does not contain enough information, say so clearly.' The `has_answer` flag in the response indicates whether the LLM found sufficient grounding. This is not a perfect guard — it is a soft constraint — but it significantly reduces hallucination for factual document questions."

---

**Q: How are you handling API key security?**
> "API keys are stored in a `.env` file and loaded through pydantic-settings. The `.env` file is in `.gitignore` and never committed. The backend never exposes keys to the frontend — the Streamlit app talks to FastAPI, not to the LLM directly."

---

**Q: Why FastAPI and not Flask or Django?**
> "FastAPI gives automatic request/response validation through Pydantic models, auto-generated Swagger docs at `/docs`, and native async support which matters for LLM calls that may take several seconds. Flask requires more boilerplate for the same thing. Django is overkill for a single-responsibility API."

---

### Testing

**Q: How did you test LLM-dependent code? You can't mock a live LLM reliably.**
> "I mocked the LLM object and set `mock_llm.return_value` to a pre-built `AIMessage`. The key insight is that in a LangChain LCEL chain (`PROMPT | llm`), the chain calls `llm(messages)` directly — not `llm.invoke()` — so the mock must use `.return_value`, not `.invoke.return_value`. Tests run in milliseconds with no API calls."

---

**Q: What is the test coverage?**
> "15 tests total — 8 unit tests covering all four pipeline stages individually, and 7 integration tests covering all three API endpoints. External dependencies (LLM, ChromaDB, HTTP) are fully mocked. The test suite runs in under 5 seconds."

---

**Q: Would this work in production? What would you change?**
> "For production I would: (1) replace ChromaDB with a managed vector store (Pinecone or Weaviate) for scalability and high availability; (2) add authentication to the FastAPI endpoints; (3) add a reranking step (cross-encoder) after the initial retrieval to improve precision; (4) add observability — request logging, latency tracking, and LLM cost monitoring through LangSmith or similar; (5) containerise with Docker Compose so backend and frontend start with one command."

---

### Business / Impact

**Q: What is the real-world value of this project?**
> "HR and IT teams receive the same questions repeatedly — leave policy, expense rules, onboarding steps. This system lets employees self-serve in seconds instead of waiting for a human response. The source links mean employees can trust the answer and verify it. The same architecture scales to thousands of documents."

---

**Q: How would you add new documents?**
> "Drop a file into `data/sample_docs/` and run `python scripts/ingest.py`. The ingestion pipeline loads, chunks, embeds, and stores the new document in ChromaDB. No code changes needed. In production this would be a background job triggered by a document upload API."

---

**Q: What are the limitations?**
> "Three main ones. First, the knowledge is static — it only knows what was ingested; live document edits are not reflected until re-ingestion. Second, very long or complex multi-part questions may get incomplete answers if the relevant chunks are spread across many documents. Third, the LLM's language capability is bounded by the model — it cannot reason beyond what Gemini 2.5 Flash supports."

---

## Backup: API Demo via Swagger

If the UI has any issues, fall back to `http://localhost:8000/docs`:

1. Expand `POST /query` → click **Try it out**
2. Paste:
```json
{
  "question": "What is the remote work policy?",
  "top_k": 5
}
```
3. Click **Execute** — show the full JSON response including `intent`, `answer`, `sources`, and `processing_time_ms`

This proves the backend works independently of the frontend.

---

## One-liner Project Summary (for introductions)

> "Internal Knowledge Base Navigator — a four-stage RAG pipeline that takes a natural-language question, classifies its intent, retrieves relevant chunks from a ChromaDB vector store, synthesises an answer with Gemini 2.5 Flash, and returns it with clickable source links — served through a FastAPI backend and Streamlit chat UI."
