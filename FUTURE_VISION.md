# FUTURE_VISION.md
## Internal Knowledge Base Navigator — Full Product Vision

> This document captures the complete product thinking: what was built in 2 weeks (MVP), what was consciously left out, and where the product goes next. It exists to prove we thought before we coded.

---

## Vision Statement

Every employee in the organisation gets an always-on, conversational knowledge assistant that knows every policy, process, and procedure — and answers questions instantly, with citations, in the context of their role, department, and work history.

---

## Product Horizon Map

```
Now (2-week MVP)          Near (3–6 months)           Far (6–18 months)
─────────────────         ─────────────────────────   ──────────────────────────────
Sequential RAG            Streaming + feedback loop   Agentic multi-step reasoning
8 Markdown docs           50+ docs, PDF/DOCX/PPTX     Real Confluence / SharePoint sync
Single user, no auth      SSO + role-based filtering  Department-scoped collections
Streamlit chat UI         React SPA                   Slack / Teams bot integration
CLI ingestion             Upload UI + auto-re-index    Event-driven live ingestion
Local ChromaDB            Managed vector DB (Weaviate) Hybrid search (BM25 + vector)
Manual demo               Staging environment          Multi-region production
```

---

## In-Scope (Built in 2 Weeks)

These are the features that exist in the current codebase and will be demoed live.

1. **Document ingestion pipeline** — Markdown loader → recursive text splitter → `text-embedding-3-large` → ChromaDB persistent collection
2. **4-stage Sequential RAG pipeline** — Query Understanding → Semantic Search → Answer Generation → Source Linking, wired as a deterministic LCEL chain
3. **Intent classification** — 5-class intent taxonomy (PROCESS_INQUIRY, POLICY_LOOKUP, CONTACT_LOOKUP, GENERAL_INFO, UNKNOWN) surfaced in the UI
4. **FastAPI REST backend** — `POST /query`, `GET /health`, `GET /documents`, `GET /documents/view/{filename}` with Pydantic validation and path-traversal protection
5. **Streamlit chat UI** — Session history, intent chip, source cards (title, URL, relevance %), "View Document" in-browser viewer
6. **Unit + integration tests** — pytest suite covering all 4 agents and all 3 endpoints
7. **Config-driven secrets** — All credentials in `.env` via `pydantic-settings`; retry logic with `tenacity`

---

## Out-of-Scope (Deliberately Deferred)

These features were analysed and intentionally excluded from the 2-week build. Each has a rationale and a target horizon.

### Near-term Deferrals (3–6 months)

| Feature | Why deferred | Target horizon |
|---------|-------------|----------------|
| **Response streaming** (SSE / WebSocket) | Requires async pipeline rewrite; adds latency complexity | Month 2 |
| **User feedback / thumbs rating** | Needs a feedback store + analytics pipeline | Month 2 |
| **PDF and DOCX ingestion** | Loaders exist but parser edge cases (tables, images) need hardening | Month 2 |
| **Document upload UI** | File management UX is a separate surface; CLI is sufficient for demo | Month 3 |
| **Conversation memory across sessions** | Requires a session store (Redis/Postgres); Streamlit state is sufficient now | Month 3 |
| **Re-ranking with a cross-encoder** | Improves retrieval precision; adds latency and a second model call | Month 3 |
| **Query caching** | Reduces LLM cost for repeated questions; needs a cache key strategy | Month 3 |
| **Observability dashboard** (latency, cost, query volume) | Requires a metrics sink (Prometheus/Grafana or Langfuse) | Month 4 |
| **Docker / Compose deployment** | Infrastructure concern; local dev is target for MVP | Month 4 |
| **React SPA frontend** | Streamlit limits customisation; React enables richer UX | Month 5 |

### Long-term Deferrals (6–18 months)

| Feature | Why deferred | Target horizon |
|---------|-------------|----------------|
| **SSO / OAuth2 authentication** | Requires IdP integration design | Month 6 |
| **Role-based document filtering** | Needs a permissions model and per-user context injection | Month 7 |
| **Real Confluence / SharePoint connector** | Requires OAuth flows, pagination, delta-sync | Month 8 |
| **Agentic multi-step reasoning** (LangGraph) | ReAct loops and tool use need careful guardrails | Month 9 |
| **Slack / Microsoft Teams bot** | Messaging platform integration with webhook infra | Month 10 |
| **Live document sync** (event-driven re-ingestion) | Requires a document change-event bus | Month 12 |
| **Hybrid search** (BM25 + dense vector) | Improves recall on exact-match queries; needs search infra upgrade | Month 12 |
| **Multi-region production deployment** | Requires SRE, DR planning, data residency compliance | Month 18 |
| **Fine-tuned domain embeddings** | Custom embedding model for internal vocabulary | Month 18 |

---

## Stretch Goals (Could land in Week 2 if ahead of schedule)

These were considered and are small enough to attempt if capacity allows, but are not committed.

- [ ] Syntax highlighting in the document viewer
- [ ] "Copy answer" button in the chat UI
- [ ] Relevance score bar chart in source cards
- [ ] `top_k` slider in the Streamlit sidebar
- [ ] Dockerfile for one-command startup

---

## Architecture Evolution

### MVP (Now)
```
Streamlit → FastAPI → Sequential LCEL Pipeline → ChromaDB + LiteLLM
```

### Near (3–6 months)
```
React SPA → FastAPI (streaming) → Pipeline + Re-ranker → ChromaDB + Redis cache
                                                         ↑
                                              Feedback loop (Langfuse)
```

### Far (6–18 months)
```
Slack/Teams/Web → API Gateway → LangGraph Agentic Engine → Hybrid Search (BM25 + vector)
                                         ↓                        ↓
                               Confluence/SharePoint sync    Weaviate managed DB
                                         ↓
                                Permissions filter (RBAC)
```

---

## Why This Sequencing?

1. **Prove correctness before performance** — A working sequential pipeline with deterministic outputs is easier to debug than a streaming agentic loop.
2. **Ship a demo before adding infrastructure** — Auth, Docker, and CI/CD slow down early iteration. Add them once the product is validated.
3. **Data quality before model quality** — A better document corpus beats a better model. Expand the knowledge base before adding re-ranking or fine-tuning.
4. **Observability before optimisation** — You cannot improve what you cannot measure. Add Langfuse/Prometheus before tuning latency.
