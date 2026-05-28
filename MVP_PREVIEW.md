# MVP_PREVIEW.md
## What This Looks Like After 2 Weeks

> A concrete, honest preview of the working product a reviewer will see on demo day. No speculation — every item here maps to code that exists or is committed to in [REQUIREMENTS.md](REQUIREMENTS.md).

---

## What You Will See

### Screen 1 — Streamlit Chat Interface (`http://localhost:8501`)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  ░░ KnowledgeAI sidebar ░░             │  KnowledgeAI chat window        │
│                                        │                                  │
│  ● API Online                          │  You: What is the annual leave   │
│                                        │       policy?                    │
│  Knowledge Base                        │                                  │
│  ─────────────                         │  ● Intent: POLICY_LOOKUP         │
│  📄 Annual Leave Policy    5 chunks    │                                  │
│  📄 Code of Conduct        4 chunks    │  Assistant:                      │
│  📄 Expense Reimbursement  5 chunks    │  Full-time employees receive 20  │
│  📄 IT Software Request    4 chunks    │  working days of paid annual     │
│  📄 Onboarding Guide       5 chunks    │  leave per year. Leave must be   │
│  📄 Performance Review     4 chunks    │  approved by your line manager   │
│  📄 Remote Work Policy     4 chunks    │  at least 2 weeks in advance.    │
│  📄 Security Guidelines    4 chunks    │  Unused leave (up to 5 days)     │
│                                        │  may carry over to the next year.│
│  8 documents / 35 chunks               │                                  │
│                                        │  Sources                         │
│  ─────────────                         │  ┌────────────────────────────┐  │
│  [Clear conversation]                  │  │ 📄 Annual Leave Policy     │  │
│                                        │  │ Relevance: 94%             │  │
│                                        │  │ [View Document]            │  │
│                                        │  └────────────────────────────┘  │
│                                        │                                  │
│                                        │  [Ask a follow-up question...]   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Screen 2 — Document Viewer (`http://localhost:8000/documents/view/annual-leave-policy.md`)

The raw policy document rendered in the browser as HTML. Clicking "View Document" in any source card opens this page directly — the employee can read the full original file without leaving the browser.

### Screen 3 — Swagger UI (`http://localhost:8000/docs`)

Interactive API documentation showing all 4 endpoints. Mentors can fire a `POST /query` directly to see the raw JSON response including `intent`, `answer`, `sources[]`, and `processing_time_ms`.

---

## What a Typical Demo Interaction Feels Like

**Employee types:** "How do I request new software for my team?"

**System does (invisible to user, visible in uvicorn logs):**
1. Query Understanding: classifies as `PROCESS_INQUIRY`, reformulates to *"software installation request procedure team IT department"*
2. Search: retrieves top-5 chunks from `it-software-request.md`
3. Answer Generator: synthesises a 3-step procedure from the retrieved context
4. Source Linker: returns 1 deduplicated source card

**User sees (in ~3–5 seconds):**
- Intent chip: "PROCESS_INQUIRY"
- Concise answer: "Submit a software request via the IT portal at helpdesk.company.com. Your manager must approve requests above £500. IT will install within 3 business days."
- Source card: "IT Software Request Policy — Relevance: 91% — [View Document]"

---

## What It Cannot Do Yet (Honest Limitations)

| Limitation | User Impact |
|-----------|-------------|
| No memory across page refreshes | Conversation resets on browser refresh |
| No streaming — answer appears all at once | 3–6 second wait before text appears |
| Only 8 documents in the knowledge base | Questions about topics not in the corpus return a "not found" answer |
| No authentication | Anyone with the URL can use the app |
| PDF / DOCX documents not ingested | Only Markdown files are indexed |
| Simulated document URLs | "View Document" links go to localhost, not a real Confluence/SharePoint |

---

## Demo Readiness Checklist

On Day 14, a reviewer sitting down cold should be able to:

- [ ] Clone the repo and run `pip install -r requirements.txt` without errors
- [ ] Copy `.env.example` to `.env`, fill in credentials, run `python scripts/ingest.py`
- [ ] Start the backend: `uvicorn app.main:app --reload`
- [ ] Start the frontend: `streamlit run frontend/app.py`
- [ ] Open `http://localhost:8501`, see "API Online", see 8 documents listed
- [ ] Ask "What is the annual leave policy?" and get a sourced answer in < 8 seconds
- [ ] Click "View Document" and see the raw policy file in the browser
- [ ] Open `http://localhost:8000/docs` and successfully call `POST /query` via Swagger
- [ ] Run `pytest tests/ -v` and see all tests pass

---

## Tech Stack Snapshot

| Layer | Technology | Version |
|-------|-----------|---------|
| LLM | Gemini 2.5 Flash (via LiteLLM proxy) | — |
| Embeddings | text-embedding-3-large (via LiteLLM proxy) | — |
| Vector store | ChromaDB (persistent, on-disk) | ≥ 1.0.9 |
| Pipeline | LangChain LCEL (RunnableLambda chain) | 0.3.25 |
| Backend | FastAPI + Uvicorn | 0.115 / 0.34 |
| Frontend | Streamlit | 1.45 |
| Config | pydantic-settings | 2.9 |
| Tests | pytest + pytest-asyncio | 8.3 / 0.26 |

---

## What "Done" Looks Like

The project is **done** when all five success criteria in [REQUIREMENTS.md § 5](REQUIREMENTS.md) are met and the demo checklist above is fully checked. Nothing more, nothing less.
