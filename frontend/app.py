import httpx
import streamlit as st

API_BASE_URL = "http://localhost:8000"

# --- Page Config --------------------------------------------------------------

st.set_page_config(
    page_title="KnowledgeAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# --- CSS ----------------------------------------------------------------------

def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }

        /* ── App background with aurora glow ─────────────────────────────── */
        .stApp {
            background-color: #070712;
            background-image:
                radial-gradient(ellipse 90% 55% at 50% -5%,  rgba(109,40,217,0.22) 0%, transparent 65%),
                radial-gradient(ellipse 45% 35% at 90% 90%,  rgba(6,182,212,0.07)  0%, transparent 55%),
                radial-gradient(ellipse 30% 25% at 10% 80%,  rgba(139,92,246,0.06) 0%, transparent 50%);
        }

        /* ── Scrollbar ───────────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 3px; height: 3px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.35); border-radius: 2px; }

        /* ── Remove sidebar collapse toggle completely ───────────────────── */
        [data-testid="stSidebarHeader"] {
            display: none !important;
        }

        /* ── Remove sidebar scrollbar ────────────────────────────────────── */
        [data-testid="stSidebar"] [data-testid="stSidebarContent"],
        [data-testid="stSidebar"] > div,
        [data-testid="stSidebar"] {
            overflow: hidden !important;
            overflow-y: hidden !important;
        }

        /* ── Sidebar ─────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: #0D0D1C !important;
            border-right: 1px solid rgba(255,255,255,0.05) !important;
        }
        [data-testid="stSidebar"] * { color: #94A3B8 !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.05) !important; }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: rgba(255,255,255,0.025) !important;
            border: 1px solid rgba(255,255,255,0.06) !important;
            border-radius: 10px !important;
            margin-bottom: 6px !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            color: #64748B !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.09em !important;
        }
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(139,92,246,0.08) !important;
            border: 1px solid rgba(139,92,246,0.18) !important;
            color: #A78BFA !important;
            border-radius: 8px !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            transition: all 0.18s ease !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(139,92,246,0.18) !important;
            border-color: rgba(139,92,246,0.4) !important;
        }
        /* Slider */
        [data-testid="stSlider"] > div > div > div > div {
            background: linear-gradient(90deg,#7C3AED,#4F46E5) !important;
        }
        [data-testid="stSlider"] [role="slider"] {
            background: #8B5CF6 !important;
            border: 2px solid #0D0D1C !important;
            box-shadow: 0 0 0 3px rgba(139,92,246,0.3) !important;
        }

        /* ── Main content area ───────────────────────────────────────────── */
        .block-container {
            padding-top: 1.5rem !important;
            max-width: 860px !important;
        }

        /* ── Page header strip ───────────────────────────────────────────── */
        .page-hdr {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 0 18px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .page-hdr-left { display: flex; align-items: center; gap: 10px; }
        .page-hdr-icon {
            width: 36px; height: 36px;
            background: linear-gradient(135deg, #7C3AED 0%, #4F46E5 100%);
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 17px;
            box-shadow: 0 4px 16px rgba(124,58,237,0.4);
            flex-shrink: 0;
        }
        .page-hdr-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #F1F5F9;
            letter-spacing: -0.02em;
        }
        .page-hdr-sub {
            font-size: 11px;
            color: #475569;
            margin-top: 1px;
            font-weight: 400;
        }

        /* ── Status pill ─────────────────────────────────────────────────── */
        .kb-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 13px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 20px;
            color: #64748B;
            font-size: 11.5px;
            font-weight: 500;
        }
        .kb-status-dot {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #34D399;
            box-shadow: 0 0 7px rgba(52,211,153,0.7);
            animation: pulse-dot 2.5s infinite;
        }
        .kb-status-dot-offline {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #F87171;
        }
        @keyframes pulse-dot {
            0%,100% { opacity:1; transform:scale(1); }
            50%      { opacity:0.55; transform:scale(0.8); }
        }

        /* ── Chat messages ───────────────────────────────────────────────── */
        [data-testid="stChatMessage"] {
            background: transparent !important;
            border: none !important;
            padding: 4px 0 !important;
        }

        /* ── Text visibility ─────────────────────────────────────────────── */
        /* User message — brightest, high contrast */
        [data-testid="stChatMessage"][data-testid*="user"] p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
            color: #F1F5F9 !important;
        }
        /* Assistant answer body — clear mid-bright */
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) p,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) li,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ol li,
        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) ul li {
            color: #CBD5E1 !important;
            line-height: 1.75 !important;
        }
        /* Bold within answers — pop with near-white */
        [data-testid="stChatMessage"] strong {
            color: #E2E8F0 !important;
        }
        /* Headings inside answers */
        [data-testid="stChatMessage"] h1,
        [data-testid="stChatMessage"] h2,
        [data-testid="stChatMessage"] h3 {
            color: #F1F5F9 !important;
        }
        /* Inline code */
        [data-testid="stChatMessage"] code {
            color: #C4B5FD !important;
            background: rgba(139,92,246,0.1) !important;
            padding: 1px 5px !important;
            border-radius: 4px !important;
        }

        /* ── Source cards ────────────────────────────────────────────────── */
        .sources-label {
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #334155;
            margin: 18px 0 8px;
        }
        .source-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.07);
            border-left: 3px solid #7C3AED;
            border-radius: 10px;
            padding: 11px 16px;
            margin-bottom: 7px;
            transition: background 0.18s, border-color 0.18s;
        }
        .source-card:hover {
            background: rgba(124,58,237,0.06);
            border-color: rgba(124,58,237,0.22);
        }
        .source-info { min-width: 0; }
        .source-title {
            font-size: 13px;
            font-weight: 600;
            color: #E2E8F0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .source-meta { font-size: 11px; color: #475569; margin-top: 2px; }
        .source-right {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-shrink: 0;
            margin-left: 12px;
        }
        .score-badge {
            font-size: 12px;
            font-weight: 700;
            color: #A78BFA;
            background: rgba(139,92,246,0.12);
            border: 1px solid rgba(139,92,246,0.22);
            padding: 2px 8px;
            border-radius: 6px;
        }
        .source-link {
            font-size: 11px;
            font-weight: 600;
            color: #7C3AED;
            text-decoration: none;
            padding: 5px 11px;
            border: 1px solid rgba(124,58,237,0.28);
            border-radius: 7px;
            white-space: nowrap;
            transition: all 0.15s;
        }
        .source-link:hover {
            background: rgba(124,58,237,0.14);
            color: #C4B5FD;
            border-color: rgba(124,58,237,0.5);
            text-decoration: none;
        }

        /* ── Intent chips ────────────────────────────────────────────────── */
        .intent-chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 10px;
        }
        .intent-POLICY_LOOKUP   { background:rgba(139,92,246,0.14); color:#A78BFA; border:1px solid rgba(139,92,246,0.28); }
        .intent-PROCESS_INQUIRY { background:rgba(6,182,212,0.11);  color:#67E8F9; border:1px solid rgba(6,182,212,0.24); }
        .intent-CONTACT_LOOKUP  { background:rgba(52,211,153,0.11); color:#6EE7B7; border:1px solid rgba(52,211,153,0.24); }
        .intent-GENERAL_INFO    { background:rgba(251,191,36,0.11); color:#FCD34D; border:1px solid rgba(251,191,36,0.24); }
        .intent-UNKNOWN         { background:rgba(100,116,139,0.11);color:#94A3B8; border:1px solid rgba(100,116,139,0.22); }

        /* ── Sidebar logo ────────────────────────────────────────────────── */
        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 14px 0 18px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 14px;
        }
        .sidebar-logo-mark {
            width: 30px; height: 30px;
            background: linear-gradient(135deg, #7C3AED, #4F46E5);
            border-radius: 8px;
            display: flex; align-items: center; justify-content: center;
            font-size: 15px;
            flex-shrink: 0;
            box-shadow: 0 3px 10px rgba(124,58,237,0.4);
        }
        .sidebar-logo-text { font-size:0.9rem !important; font-weight:700 !important; color:#F1F5F9 !important; }
        .sidebar-logo-sub  { font-size:0.67rem !important; color:#475569 !important; letter-spacing:0.02em; }

        /* ── Stats cards ─────────────────────────────────────────────────── */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-bottom: 14px;
        }
        .stat-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 10px 12px;
            text-align: center;
        }
        .stat-num { font-size: 1.15rem; font-weight: 700; color: #F1F5F9 !important; line-height: 1; }
        .stat-lbl { font-size: 0.6rem; color: #475569 !important; text-transform: uppercase;
                    letter-spacing: 0.1em; margin-top: 4px; }

        /* ── Doc items in sidebar ────────────────────────────────────────── */
        .doc-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 7px;
            font-size: 12.5px;
            color: #64748B !important;
            cursor: default;
            transition: background 0.15s;
        }
        .doc-item:hover { background: rgba(255,255,255,0.03); }
        .doc-dot {
            width: 5px; height: 5px;
            background: #6D28D9;
            border-radius: 50%;
            flex-shrink: 0;
            opacity: 0.8;
        }

        /* ── Welcome state ───────────────────────────────────────────────── */
        .welcome-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 52px 0 28px;
        }
        .welcome-glow {
            width: 72px; height: 72px;
            background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(79,70,229,0.18));
            border: 1px solid rgba(124,58,237,0.28);
            border-radius: 22px;
            display: flex; align-items: center; justify-content: center;
            font-size: 30px;
            margin-bottom: 22px;
            box-shadow: 0 0 50px rgba(124,58,237,0.14), 0 0 0 1px rgba(124,58,237,0.08) inset;
        }
        .welcome-title {
            font-size: 1.55rem;
            font-weight: 800;
            color: #F1F5F9;
            letter-spacing: -0.03em;
            margin-bottom: 10px;
            text-align: center;
        }
        .welcome-sub {
            font-size: 0.88rem;
            color: #475569;
            text-align: center;
            line-height: 1.65;
            max-width: 400px;
            margin-bottom: 34px;
        }
        .welcome-hint {
            font-size: 10px;
            color: #334155;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
            margin-bottom: 14px;
            width: 100%;
            text-align: center;
        }

        /* ── Example pill buttons (main area) ────────────────────────────── */
        div[data-testid="column"] .stButton > button {
            background: rgba(255,255,255,0.025) !important;
            border: 1px solid rgba(255,255,255,0.07) !important;
            color: #64748B !important;
            border-radius: 9px !important;
            font-size: 12.5px !important;
            font-weight: 400 !important;
            text-align: left !important;
            padding: 9px 14px !important;
            transition: all 0.18s ease !important;
            line-height: 1.4 !important;
        }
        div[data-testid="column"] .stButton > button:hover {
            background: rgba(109,40,217,0.09) !important;
            border-color: rgba(109,40,217,0.25) !important;
            color: #C4B5FD !important;
        }

        /* ── Chat input ──────────────────────────────────────────────────── */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] > div > div > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }
        [data-testid="stChatInput"] > div {
            background: rgba(255,255,255,0.035) !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            border-radius: 14px !important;
            padding: 4px !important;
            transition: border-color 0.2s, box-shadow 0.2s !important;
        }
        [data-testid="stChatInput"] > div:focus-within {
            border-color: rgba(124,58,237,0.45) !important;
            box-shadow: 0 0 0 3px rgba(124,58,237,0.07) !important;
            background: rgba(255,255,255,0.05) !important;
        }
        [data-testid="stChatInput"] textarea {
            border: 1px solid rgba(255,255,255,0.09) !important;
            background: transparent !important;
            font-size: 0.92rem !important;
            color: #122032 !important;
            padding: 12px 14px !important;
            box-shadow: none !important;
        }
        [data-testid="stChatInput"] textarea::placeholder { color: #334155 !important; }
        [data-testid="stChatInput"] button {
            background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
            border: none !important;
            border-radius: 10px !important;
            min-width: 38px !important;
            height: 38px !important;
            box-shadow: 0 2px 12px rgba(124,58,237,0.45) !important;
            transition: filter 0.15s, transform 0.15s !important;
        }
        [data-testid="stChatInput"] button:hover {
            filter: brightness(1.12) !important;
            transform: scale(1.04) !important;
        }
        [data-testid="stChatInput"] button svg { fill: #FFFFFF !important; }

        /* ── Spinner text ────────────────────────────────────────────────── */
        [data-testid="stSpinner"] p { color: #64748B !important; font-size: 13px !important; }
        /* ── Custom: .st-emotion-cache-16tyu1 color override ─────────────── */
        .st-emotion-cache-16tyu1 {
            color: #727378 !important;
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
if "prefill_query" not in st.session_state:
    st.session_state.prefill_query = ""

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

INTENT_LABELS = {
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
    st.markdown('<div class="sources-label">Sources</div>', unsafe_allow_html=True)
    for source in sources:
        relevance = int(source["score"] * 100)
        view_url  = f"{API_BASE_URL}/documents/view/{source['source_file']}"
        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-info">
                    <div class="source-title">{source['title']}</div>
                    <div class="source-meta">{source['source_file']}</div>
                </div>
                <div class="source-right">
                    <span class="score-badge">{relevance}%</span>
                    <a href="{view_url}" target="_blank" rel="noopener noreferrer"
                       class="source-link">View &rarr;</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- Pipeline Trace -----------------------------------------------------------

def render_pipeline_trace(
    reformulated: str,
    key_entities: list[str],
    chunks_n: int,
    elapsed_ms: int,
) -> None:
    if not reformulated:
        return
    with st.expander("How I found this", expanded=False):
        pills = "".join(
            f'<span style="display:inline-block;margin:2px 3px;padding:2px 9px;'
            f'background:rgba(109,40,217,0.12);color:#A78BFA;'
            f'border:1px solid rgba(109,40,217,0.25);border-radius:5px;'
            f'font-size:11px;font-weight:600;">{e}</span>'
            for e in key_entities
        ) if key_entities else ""

        st.markdown(
            f"""
            <div style="font-size:12px;line-height:1.75;color:#475569;">
                <div style="margin-bottom:10px;">
                    <span style="font-size:10px;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.09em;color:#334155;">Reformulated query</span><br>
                    <div style="margin-top:5px;background:rgba(0,0,0,0.35);
                        border:1px solid rgba(255,255,255,0.05);border-radius:7px;
                        padding:8px 12px;font-style:italic;color:#A78BFA;font-size:12.5px;">
                        {reformulated}
                    </div>
                </div>
                {"<div style='margin-bottom:10px;'><span style='font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.09em;color:#334155;'>Key entities</span><br><div style='margin-top:5px;'>" + pills + "</div></div>" if pills else ""}
                <div style="display:flex;align-items:center;gap:6px;
                    font-size:11px;color:#334155;margin-top:6px;">
                    <span style="font-size:13px;">⚡</span>
                    <b style="color:#64748B;">{elapsed_ms} ms</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- Intent Chip --------------------------------------------------------------

def render_intent_chip(intent: str) -> None:
    if not intent or intent == "UNKNOWN":
        return
    label = INTENT_LABELS.get(intent, intent)
    st.markdown(
        f'<span class="intent-chip intent-{intent}">{label}</span>',
        unsafe_allow_html=True,
    )


# --- Sidebar ------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">
            <div class="sidebar-logo-mark">⚡</div>
            <div>
                <div class="sidebar-logo-text">KnowledgeAI</div>
                <div class="sidebar-logo-sub">Internal Knowledge Navigator</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        doc_data = fetch_documents()
    except Exception:
        doc_data = {}
    total_docs  = doc_data.get("total_documents", 0)
    query_count = len(st.session_state.messages) // 2

    st.markdown(
        f"""
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-num">{total_docs}</div>
                <div class="stat-lbl">Docs</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">{query_count}</div>
                <div class="stat-lbl">Queries</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Knowledge Base", expanded=True):
        if doc_data:
            for doc in doc_data.get("documents", []):
                st.markdown(
                    f"""<div class="doc-item">
                        <div class="doc-dot"></div>
                        {doc['title']}
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("Could not load documents.")

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

    try:
        health = fetch_health()
    except Exception:
        health = {}
    if health.get("status") == "ok":
        st.markdown(
            f"""<div style="text-align:center;">
                <span class="kb-status-pill">
                    <span class="kb-status-dot"></span>
                    API Live &nbsp;&middot;&nbsp; {total_docs} docs
                </span>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<div style="text-align:center;">
                <span class="kb-status-pill">
                    <span class="kb-status-dot-offline"></span>
                    API Offline
                </span>
            </div>""",
            unsafe_allow_html=True,
        )


# --- Page Header Strip --------------------------------------------------------

try:
    health_main = fetch_health()
except Exception:
    health_main = {}

if health_main.get("status") == "ok":
    status_html = (
        f'<span class="kb-status-pill">'
        f'<span class="kb-status-dot"></span>'
        f'{total_docs} docs indexed'
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
    <div class="page-hdr">
        <div class="page-hdr-left">
            <div class="page-hdr-icon">⚡</div>
            <div>
                <div class="page-hdr-title">KnowledgeAI Navigator</div>
                <div class="page-hdr-sub">Ask anything about company policies, processes and guidelines</div>
            </div>
        </div>
        <div>{status_html}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Chat History -------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            render_source_cards(msg["sources"])
        if msg["role"] == "assistant" and msg.get("intent"):
            render_intent_chip(msg["intent"])
        if msg["role"] == "assistant" and msg.get("reformulated_query"):
            render_pipeline_trace(
                msg["reformulated_query"],
                msg.get("key_entities", []),
                msg.get("chunks_retrieved", 0),
                msg.get("processing_time_ms", 0),
            )

# --- Welcome State ------------------------------------------------------------

EXAMPLE_QUERIES = [
    "What is the annual leave policy?",
    "How do I request new software?",
    "What are the remote work requirements?",
    "How do I submit an expense claim?",
    "What are the security guidelines?",
    "How does the performance review work?",
]

if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-wrap">
            <div class="welcome-glow">⚡</div>
            <div class="welcome-title">What do you need to know?</div>
            <div class="welcome-sub">
                I have access to your company's internal policies and guides.<br>
                Ask me anything — I'll find the answer and show you the source.
            </div>
            <div class="welcome-hint">Try a question</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for i, q in enumerate(EXAMPLE_QUERIES):
        if cols[i % 3].button(q, key=f"pill_{i}", use_container_width=True):
            st.session_state.prefill_query = q
            st.rerun()

# --- Chat Input ---------------------------------------------------------------

if st.session_state.prefill_query:
    prompt = st.session_state.prefill_query
    st.session_state.prefill_query = ""
else:
    prompt = st.chat_input("Ask about company policies, processes or guidelines...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                data         = call_query_api(prompt, st.session_state.top_k)
                answer       = data["answer"]
                sources      = data.get("sources", [])
                intent       = data.get("intent", "UNKNOWN")
                has_answer   = data.get("has_answer", True)
                reformulated = data.get("reformulated_query", "")
                key_entities = data.get("key_entities", [])
                chunks_n     = data.get("chunks_retrieved", 0)
                elapsed_ms   = data.get("processing_time_ms", 0)

                if has_answer:
                    st.markdown(answer)
                else:
                    st.info(answer)

                render_source_cards(sources)
                render_intent_chip(intent)
                render_pipeline_trace(reformulated, key_entities, chunks_n, elapsed_ms)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "intent": intent,
                    "reformulated_query": reformulated,
                    "key_entities": key_entities,
                    "chunks_retrieved": chunks_n,
                    "processing_time_ms": elapsed_ms,
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
