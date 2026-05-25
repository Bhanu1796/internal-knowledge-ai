import httpx
import streamlit as st

API_BASE_URL = "http://localhost:8000"

# --- Page Config --------------------------------------------------------------

st.set_page_config(
    page_title="KnowledgeAI",
    page_icon="zap",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ----------------------------------------------------------------------

def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }

        /* App background */
        .stApp { background: #F0F2FF; }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1E1B4B 0%, #2D2A6E 100%) !important;
            border-right: none !important;
        }
        [data-testid="stSidebar"] * { color: #E0E7FF !important; }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }
        [data-testid="stSidebar"] .stMarkdown p { color: #C7D2FE !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.12) !important; }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255,255,255,0.07) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 12px !important;
            margin-bottom: 8px;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            color: #E0E7FF !important;
            font-weight: 600;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: #E0E7FF !important;
            border-radius: 10px !important;
            font-weight: 500;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.18) !important;
        }

        /* Main content */
        .block-container {
            padding-top: 1.5rem !important;
            max-width: 900px !important;
        }

        /* Header banner */
        .kb-header {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 60%, #A855F7 100%);
            border-radius: 20px;
            padding: 28px 32px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 32px rgba(79,70,229,0.35);
        }
        .kb-header-left h1 {
            color: #FFFFFF;
            font-size: 1.6rem;
            font-weight: 700;
            margin: 0 0 4px 0;
        }
        .kb-header-left p {
            color: rgba(255,255,255,0.75);
            font-size: 0.88rem;
            margin: 0;
        }
        .kb-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            background: rgba(255,255,255,0.18);
            border: 1px solid rgba(255,255,255,0.25);
            border-radius: 9999px;
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
        }
        .kb-status-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #4ADE80;
            box-shadow: 0 0 6px #4ADE80;
            animation: pulse-dot 2s infinite;
        }
        .kb-status-dot-offline {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #F87171;
        }
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50%       { opacity: 0.5; }
        }

        /* Source cards */
        .sources-header {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #6B7280;
            margin: 16px 0 10px 0;
        }
        .source-card {
            background: #FFFFFF;
            border: 1px solid #E8EAFB;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            position: relative;
            overflow: hidden;
        }
        .source-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #4F46E5, #A855F7);
        }
        .source-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79,70,229,0.15);
        }
        .source-title {
            font-size: 13px;
            font-weight: 700;
            color: #1E1B4B;
            margin-bottom: 6px;
        }
        .source-meta {
            font-size: 11px;
            color: #9CA3AF;
            margin-bottom: 8px;
        }
        .relevance-bar-wrap {
            background: #F3F4F6;
            border-radius: 9999px;
            height: 4px;
            margin-bottom: 8px;
            overflow: hidden;
        }
        .relevance-bar-fill {
            height: 4px;
            border-radius: 9999px;
            background: linear-gradient(90deg, #4F46E5, #A855F7);
        }
        .source-link {
            font-size: 12px;
            font-weight: 600;
            color: #4F46E5;
            text-decoration: none;
        }
        .source-link:hover { color: #7C3AED; text-decoration: underline; }

        /* Intent chips */
        .intent-chip {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 10px;
        }
        .intent-POLICY_LOOKUP    { background: #EDE9FE; color: #6D28D9; border: 1px solid #DDD6FE; }
        .intent-PROCESS_INQUIRY  { background: #DBEAFE; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .intent-CONTACT_LOOKUP   { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .intent-GENERAL_INFO     { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .intent-UNKNOWN          { background: #F3F4F6; color: #6B7280; border: 1px solid #E5E7EB; }

        /* Chat input — strip all Streamlit default chrome */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] > div > div > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        /* Outer wrapper — the visible panel */
        [data-testid="stChatInput"] > div {
            background: #FFFFFF !important;
            border: 1.5px solid #C7D2FE !important;
            border-radius: 16px !important;
            padding: 4px 4px 4px 4px !important;
            box-shadow: 0 2px 16px rgba(79,70,229,0.10),
                        0 1px 4px rgba(0,0,0,0.04) !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
            display: flex !important;
            align-items: center !important;
        }
        [data-testid="stChatInput"] > div:focus-within {
            border-color: #6366F1 !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.12),
                        0 2px 16px rgba(79,70,229,0.14) !important;
        }
        /* Textarea itself */
        [data-testid="stChatInput"] textarea {
            border: none !important;
            border-radius: 12px !important;
            background: transparent !important;
            font-size: 0.94rem !important;
            color: #1E1B4B !important;
            padding: 12px 14px !important;
            box-shadow: none !important;
            outline: none !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #9CA3AF !important;
        }
        /* Send button */
        [data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #4F46E5, #7C3AED) !important;
            border: none !important;
            border-radius: 12px !important;
            min-width: 42px !important;
            height: 42px !important;
            box-shadow: 0 3px 10px rgba(79,70,229,0.35) !important;
            flex-shrink: 0 !important;
            transition: transform 0.15s, box-shadow 0.15s !important;
        }
        [data-testid="stChatInput"] button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 5px 16px rgba(79,70,229,0.45) !important;
        }
        [data-testid="stChatInput"] button svg {
            fill: #FFFFFF !important;
        }

        /* Sidebar logo */
        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 0 16px 0;
        }
        .sidebar-logo-icon {
            width: 38px; height: 38px;
            background: linear-gradient(135deg, #6366F1, #A855F7);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
        }
        .sidebar-logo-text {
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }
        .sidebar-logo-sub {
            font-size: 0.72rem !important;
            color: #A5B4FC !important;
            margin-top: 1px;
        }

        /* Sidebar stats strip */
        .stats-strip {
            display: flex;
            gap: 8px;
            padding: 10px 12px;
            background: rgba(255,255,255,0.07);
            border-radius: 10px;
            margin-bottom: 16px;
            justify-content: space-between;
        }
        .stat-item { text-align: center; }
        .stat-num  { font-size: 1.1rem; font-weight: 700; color: #FFFFFF !important; }
        .stat-lbl  { font-size: 0.65rem; color: #A5B4FC !important;
                     text-transform: uppercase; letter-spacing: 0.06em; }

        /* Doc item */
        .doc-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            margin-bottom: 4px;
            font-size: 12.5px;
        }
        .doc-item-dot {
            width: 6px; height: 6px;
            background: #818CF8;
            border-radius: 50%;
            flex-shrink: 0;
        }
        .doc-chunks {
            margin-left: auto;
            font-size: 10px;
            background: rgba(255,255,255,0.12);
            padding: 1px 6px;
            border-radius: 9999px;
            color: #A5B4FC !important;
        }

        /* Welcome card */
        .welcome-card {
            background: #FFFFFF;
            border: 1px solid #E8EAFB;
            border-radius: 20px;
            padding: 32px;
            text-align: center;
            box-shadow: 0 2px 16px rgba(0,0,0,0.05);
            margin-bottom: 16px;
        }
        .welcome-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #1E1B4B;
            margin-bottom: 8px;
        }
        .welcome-sub {
            color: #6B7280;
            font-size: 0.9rem;
            margin-bottom: 24px;
        }
        .example-pills {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }
        .example-pill {
            display: inline-block;
            padding: 8px 16px;
            background: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()

# --- Session State ------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "top_k" not in st.session_state:
    st.session_state.top_k = 5

# --- API Helpers --------------------------------------------------------------

@st.cache_data(ttl=30, show_spinner=False)
def fetch_health() -> dict:
    r = httpx.get(f"{API_BASE_URL}/health", timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=60, show_spinner=False)
def fetch_documents() -> dict:
    r = httpx.get(f"{API_BASE_URL}/documents", timeout=5)
    r.raise_for_status()
    return r.json()


def call_query_api(question: str, top_k: int) -> dict:
    r = httpx.post(
        f"{API_BASE_URL}/query",
        json={"question": question, "top_k": top_k},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


# --- Intent helpers -----------------------------------------------------------

INTENT_ICONS = {
    "POLICY_LOOKUP":   "Policy",
    "PROCESS_INQUIRY": "Process",
    "CONTACT_LOOKUP":  "Contact",
    "GENERAL_INFO":    "Info",
    "UNKNOWN":         "Unknown",
}


# --- Source Cards -------------------------------------------------------------

def render_source_cards(sources: list[dict]) -> None:
    if not sources:
        return
    st.markdown('<div class="sources-header">Sources</div>', unsafe_allow_html=True)
    cols = st.columns(min(len(sources), 3))
    for i, source in enumerate(sources):
        with cols[i % 3]:
            page = source["page"]
            page_label = f"Page {page} &nbsp;&middot;&nbsp; " if page > 0 else ""
            relevance = int(source["score"] * 100)
            view_url = f"{API_BASE_URL}/documents/view/{source['source_file']}"
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-title">{source['title']}</div>
                    <div class="source-meta">{page_label}Relevance: {relevance}%</div>
                    <div class="relevance-bar-wrap">
                        <div class="relevance-bar-fill" style="width:{relevance}%"></div>
                    </div>
                    <a href="{view_url}" target="_blank" rel="noopener noreferrer" class="source-link">
                        View Document &rarr;
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )


# --- Intent Chip --------------------------------------------------------------

def render_intent_chip(intent: str) -> None:
    if not intent or intent == "UNKNOWN":
        return
    label = INTENT_ICONS.get(intent, intent)
    st.markdown(
        f'<span class="intent-chip intent-{intent}">{label}</span>',
        unsafe_allow_html=True,
    )


# --- Sidebar ------------------------------------------------------------------

with st.sidebar:
    # Logo block
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-icon">&#9889;</div>
            <div>
                <div class="sidebar-logo-text">KnowledgeAI</div>
                <div class="sidebar-logo-sub">Internal Knowledge Navigator</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Stats strip
    try:
        doc_data = fetch_documents()
    except Exception:
        doc_data = {}
    total_docs   = doc_data.get("total_documents", 0)
    total_chunks = doc_data.get("total_chunks", 0)
    query_count  = len(st.session_state.messages) // 2

    st.markdown(
        f"""
        <div class="stats-strip">
            <div class="stat-item">
                <div class="stat-num">{total_docs}</div>
                <div class="stat-lbl">Docs</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{total_chunks}</div>
                <div class="stat-lbl">Chunks</div>
            </div>
            <div class="stat-item">
                <div class="stat-num">{query_count}</div>
                <div class="stat-lbl">Queries</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Document list
    with st.expander("Knowledge Base", expanded=True):
        if doc_data:
            for doc in doc_data.get("documents", []):
                st.markdown(
                    f"""<div class="doc-item">
                        <div class="doc-item-dot"></div>
                        {doc['title']}
                        <span class="doc-chunks">{doc['chunk_count']}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Could not load documents.")

    # Settings
    with st.expander("Settings", expanded=False):
        st.session_state.top_k = st.slider(
            "Top-K results",
            min_value=1,
            max_value=20,
            value=st.session_state.top_k,
            step=1,
        )
        if st.button("Clear conversation", use_container_width=True, key="clear_chat_btn"):
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # API status
    try:
        health = fetch_health()
    except Exception:
        health = {}
    if health.get("status") == "ok":
        st.markdown(
            f"""<div style="text-align:center">
                <span class="kb-status-pill">
                    <span class="kb-status-dot"></span>
                    API Live &nbsp;&middot;&nbsp; {health.get("vector_store_docs", 0)} docs
                </span>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div style="text-align:center">
                <span class="kb-status-pill">
                    <span class="kb-status-dot-offline"></span>
                    API Offline
                </span>
            </div>""",
            unsafe_allow_html=True,
        )


# --- Header Banner ------------------------------------------------------------

try:
    health_main = fetch_health()
except Exception:
    health_main = {}
if health_main.get("status") == "ok":
    status_html = (
        f'<span class="kb-status-pill">'
        f'<span class="kb-status-dot"></span>'
        f'{health_main.get("vector_store_docs", 0)} documents indexed'
        f'</span>'
    )
else:
    status_html = (
        '<span class="kb-status-pill">'
        '<span class="kb-status-dot-offline"></span>'
        'Offline'
        '</span>'
    )

st.markdown(
    f"""
    <div class="kb-header">
        <div class="kb-header-left">
            <h1>&#9889; KnowledgeAI Navigator</h1>
            <p>Ask anything about company policies, processes and guidelines</p>
        </div>
        <div>{status_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Chat History -------------------------------------------------------------

for msg in st.session_state.messages:
    avatar = "assistant" if msg["role"] == "assistant" else "user"
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            render_source_cards(msg["sources"])
        if msg["role"] == "assistant" and msg.get("intent"):
            render_intent_chip(msg["intent"])

# --- Welcome State ------------------------------------------------------------

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-card">
            <div class="welcome-title">Welcome to KnowledgeAI</div>
            <div class="welcome-sub">
                I have access to your company's internal documents.<br>
                Ask me anything &mdash; I'll find the answer and show you the source.
            </div>
            <div class="example-pills">
                <span class="example-pill">What is the annual leave policy?</span>
                <span class="example-pill">How do I request new software?</span>
                <span class="example-pill">What are the remote work requirements?</span>
                <span class="example-pill">How do I submit an expense claim?</span>
                <span class="example-pill">What are the security guidelines?</span>
                <span class="example-pill">How does the performance review work?</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Chat Input ---------------------------------------------------------------

if prompt := st.chat_input("Ask about company policies, processes or guidelines..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                data       = call_query_api(prompt, st.session_state.top_k)
                answer     = data["answer"]
                sources    = data.get("sources", [])
                intent     = data.get("intent", "UNKNOWN")
                has_answer = data.get("has_answer", True)

                if has_answer:
                    st.markdown(answer)
                else:
                    st.info(answer)

                render_source_cards(sources)
                render_intent_chip(intent)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "intent": intent,
                })

            except httpx.ConnectError:
                err = "Cannot connect to the API. Make sure the backend is running on port 8000."
                st.error(err)
                st.session_state.messages.append({
                    "role": "assistant", "content": err, "sources": [], "intent": None,
                })
            except Exception as e:
                err = f"An error occurred: {str(e)}"
                st.error(err)
                st.session_state.messages.append({
                    "role": "assistant", "content": err, "sources": [], "intent": None,
                })
