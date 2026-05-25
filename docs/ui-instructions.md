# UI Instructions

## Overview

The frontend is a **Streamlit chat application** (`frontend/app.py`). This document describes the layout, components, interaction flows, and implementation guidelines for every UI element.

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  SIDEBAR (260px)            │  MAIN AREA                        │
│                             │                                   │
│  ┌─────────────────────┐    │  ┌─────────────────────────────┐  │
│  │  App Title          │    │  │  Page Header                │  │
│  │  + tagline          │    │  │  + subtitle                 │  │
│  └─────────────────────┘    │  └─────────────────────────────┘  │
│                             │                                   │
│  ┌─────────────────────┐    │  ┌─────────────────────────────┐  │
│  │  Knowledge Base     │    │  │  Chat Message Area          │  │
│  │  Documents          │    │  │  (scrollable history)       │  │
│  │  • Doc 1            │    │  │                             │  │
│  │  • Doc 2            │    │  │  [assistant] Welcome msg    │  │
│  │  • ...              │    │  │  [user]      First query    │  │
│  └─────────────────────┘    │  │  [assistant] Answer + srcs  │  │
│                             │  │  [user]      Second query   │  │
│  ┌─────────────────────┐    │  │  [assistant] ...            │  │
│  │  Settings           │    │  │                             │  │
│  │  Top-K slider       │    │  └─────────────────────────────┘  │
│  │  Clear chat btn     │    │                                   │
│  └─────────────────────┘    │  ┌─────────────────────────────┐  │
│                             │  │  Chat Input (sticky bottom) │  │
│  ┌─────────────────────┐    │  └─────────────────────────────┘  │
│  │  API Status badge   │    │                                   │
│  └─────────────────────┘    │                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sidebar

### App Title Block
- Title: **"KB Navigator"**
- Tagline: `"AI-powered internal knowledge base search"`
- Render using `st.sidebar.markdown` with custom CSS class `sidebar-title`

### Knowledge Base Documents Panel
- Section header: **"Knowledge Base"**
- Fetch document list from `GET /documents` on page load
- Render as a `st.sidebar.expander("📚 Indexed Documents", expanded=False)`
- Each document displayed as:
  ```
  • Annual Leave Policy   (6 chunks)
  • IT Software Request   (5 chunks)
  ```
- Show total at bottom: `Total: 47 chunks across 8 documents`
- On error fetching documents: show `st.sidebar.warning("Could not load document list")`

### Settings Panel
- Render as `st.sidebar.expander("⚙️ Settings", expanded=False)`
- **Top-K slider**: `st.sidebar.slider("Results to retrieve", min=1, max=20, value=5, step=1)`
  - Stored in `st.session_state["top_k"]`
- **Clear Chat button**: `st.sidebar.button("🗑️ Clear conversation")`
  - On click: clear `st.session_state["messages"]` and rerun

### API Status Badge
- Pinned to bottom of sidebar
- Poll `GET /health` on page load
- Display:
  - ✅ `API Connected` (green) — when health returns `status: ok`
  - ❌ `API Offline` (red) — on connection error
- Render using `st.sidebar.markdown` with inline CSS badge styling

---

## Main Area

### Page Header
```python
st.title("Internal Knowledge Base Navigator")
st.caption("Ask a question and I'll find the answer from your company's knowledge base.")
```

### Chat Message Area

All conversation messages are stored in `st.session_state["messages"]` as a list of dicts:

```python
[
    {"role": "assistant", "content": "...", "sources": [], "intent": None},
    {"role": "user",      "content": "...", "sources": None, "intent": None},
    {"role": "assistant", "content": "...", "sources": [...], "intent": "PROCESS_INQUIRY"},
]
```

Messages are rendered by iterating `st.session_state["messages"]` and calling `st.chat_message(role)`.

#### User Message
```python
with st.chat_message("user"):
    st.markdown(message["content"])
```

#### Assistant Message
```python
with st.chat_message("assistant", avatar="🔍"):
    st.markdown(message["content"])
    if message.get("sources"):
        render_source_cards(message["sources"])
    if message.get("intent") and message["intent"] != "UNKNOWN":
        st.caption(f"Intent: {message['intent']}")
```

#### Welcome Message
Displayed only when `st.session_state["messages"]` is empty:

```python
with st.chat_message("assistant", avatar="🔍"):
    st.markdown(
        "Hello! I'm your Knowledge Base Navigator. "
        "Ask me anything about company policies, processes, or guidelines."
    )
    st.markdown("**Try asking:**")
    st.markdown("- *What is the annual leave policy?*")
    st.markdown("- *How do I request new software?*")
    st.markdown("- *What are the remote work requirements?*")
```

---

## Source Cards Component

Source cards are rendered below the assistant's answer when `sources` is non-empty.

### Layout
```
┌──────────────────────────────────────────────────────┐
│  📄 Sources                                          │
│                                                      │
│  ┌────────────────────────────────────┐              │
│  │ 📎 IT Software Request Policy      │              │
│  │    Page 2  •  Score: 0.89          │              │
│  │    🔗 View Document                │              │
│  └────────────────────────────────────┘              │
│  ┌────────────────────────────────────┐              │
│  │ 📎 Employee Onboarding Guide       │              │
│  │    Page 5  •  Score: 0.71          │              │
│  │    🔗 View Document                │              │
│  └────────────────────────────────────┘              │
└──────────────────────────────────────────────────────┘
```

### Implementation
```python
def render_source_cards(sources: list[dict]) -> None:
    st.markdown("**📄 Sources**")
    cols = st.columns(min(len(sources), 3))
    for i, source in enumerate(sources):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-title">📎 {source['title']}</div>
                    <div class="source-meta">
                        Page {source['page']} &nbsp;•&nbsp;
                        Score: {source['score']:.2f}
                    </div>
                    <a href="{source['url']}" target="_blank"
                       class="source-link">🔗 View Document</a>
                </div>
                """,
                unsafe_allow_html=True
            )
```

---

## Chat Input

```python
if prompt := st.chat_input("Ask a question about company policies or processes..."):
    handle_user_query(prompt)
```

- Placeholder text: `"Ask a question about company policies or processes..."`
- Rendered using `st.chat_input` which anchors to the bottom of the page automatically
- Disabled while a response is being generated (use `st.session_state["loading"]`)

---

## Loading State

While the API call is in progress:
1. Append the user message immediately to `st.session_state["messages"]` and rerender
2. Show a spinner inside the assistant chat bubble:
   ```python
   with st.chat_message("assistant", avatar="🔍"):
       with st.spinner("Searching knowledge base..."):
           response = call_api(prompt)
   ```
3. Replace the spinner with the answer + sources on completion

---

## Error States

| Scenario | UI Behaviour |
|---|---|
| API returns `has_answer: false` | Display the fallback message in a `st.info` box |
| API returns HTTP 5xx | `st.error("An error occurred. Please try again or contact support.")` |
| API is unreachable | `st.error("Cannot connect to the API. Ensure the backend is running on port 8000.")` |
| Empty query submitted | No action — `st.chat_input` prevents empty submission |

---

## Session State Keys

| Key | Type | Description |
|---|---|---|
| `messages` | `list[dict]` | Full conversation history |
| `top_k` | `int` | Current top-K retrieval setting (default: `5`) |
| `loading` | `bool` | True while an API call is in progress |
| `documents` | `list[dict]` | Cached document list from `GET /documents` |

Initialise all keys at the top of `app.py`:

```python
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "top_k" not in st.session_state:
    st.session_state["top_k"] = 5
if "loading" not in st.session_state:
    st.session_state["loading"] = False
```

---

## Page Configuration

```python
st.set_page_config(
    page_title="KB Navigator",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
```

---

## Custom CSS Injection

Inject once at the top of `app.py` using `st.markdown(..., unsafe_allow_html=True)`. CSS values reference the design tokens defined in `docs/design-tokens.md`.

```python
def inject_css() -> None:
    st.markdown("""
        <style>
        /* Source card styles */
        .source-card { ... }
        .source-title { ... }
        .source-meta { ... }
        .source-link { ... }

        /* Sidebar title */
        .sidebar-title { ... }

        /* API status badge */
        .badge-online { ... }
        .badge-offline { ... }
        </style>
    """, unsafe_allow_html=True)
```

Full CSS values are derived from `docs/design-tokens.md`.

---

## Accessibility Guidelines

- All interactive elements must have descriptive labels
- Source card links open in a new tab (`target="_blank"`) with `rel="noopener noreferrer"`
- Colour is never the sole indicator of status — pair badges with text labels ("Connected" / "Offline")
- Minimum text contrast ratio: 4.5:1 (WCAG AA)
