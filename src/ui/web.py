"""geekGrep — Dark Luxury Document Intelligence"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import tempfile
import shutil

# Setup
app_root = Path(__file__).parent.parent.parent
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from src.pipeline import ingest, query, get_store_info

load_dotenv()

# Page config
st.set_page_config(
    page_title="geekGrep",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Targeted CSS — typography, spacing, polish only.
# All component colors come from .streamlit/config.toml native theme.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* Typography only — let Streamlit theme handle colors */
h1, h2, h3 {
    font-family: 'Playfair Display', Georgia, serif !important;
}

p, span, label, li, div, input, textarea, button, a, td, th, .stMarkdown {
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide default hamburger + footer */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }

/* Spacing */
.block-container {
    padding: 3rem 4rem 2rem 4rem !important;
    max-width: 1200px !important;
}

/* Tab styling — keep Streamlit colors, refine shape */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important;
}

.stTabs [data-baseweb="tab-list"] button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 1.8rem !important;
}

/* Button refinement — keep theme colors */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-radius: 4px !important;
    transition: all 0.25s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(212, 160, 74, 0.3) !important;
}

/* Input refinement — keep theme colors */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] {
    border-radius: 4px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Metric cards — subtle border */
[data-testid="stMetric"] {
    border: 1px solid rgba(212, 160, 74, 0.2);
    border-radius: 6px;
    padding: 1rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0D0D0D; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #D4A04A; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────

_store_cache = {}

def load_store_info(persist_dir):
    """Get store info with simple caching."""
    if persist_dir not in _store_cache:
        _store_cache[persist_dir] = get_store_info(persist_dir)
    return _store_cache[persist_dir]


# ─── UI Sections ────────────────────────────────────────────────────────────

def render_header():
    """Render the brand header"""
    st.markdown("# geekGrep")
    st.caption("Document intelligence, locally powered.")
    st.markdown("")


def render_upload_tab():
    """Render the upload / ingest tab"""
    st.markdown("### Ingest Documents")
    st.markdown("Upload PDF, Markdown, or plain-text files to build your searchable knowledge base.")
    st.markdown("")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "md", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) ready**")
        for f in uploaded_files:
            st.caption(f"  {f.name}  —  {f.size:,} bytes")

    st.markdown("")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        reset = st.checkbox("Reset store first")
    with col2:
        go = st.button("Ingest", use_container_width=True, type="primary")

    if go:
        if not uploaded_files:
            st.warning("Select at least one file first.")
        else:
            with st.spinner("Processing …"):
                temp_dir = tempfile.mkdtemp()
                try:
                    for f in uploaded_files:
                        Path(temp_dir, f.name).write_bytes(f.getbuffer())
                    result = ingest(temp_dir, "./data/chroma_db", reset=reset)

                    if result["status"] == "success":
                        st.success(
                            f"Done — {result['documents_loaded']} docs, "
                            f"{result['chunks_created']} chunks indexed."
                        )
                    else:
                        st.error(result["message"])
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)


def render_query_tab():
    """Render the query tab"""
    st.markdown("### Ask Your Documents")
    st.markdown("")

    # Metrics row
    store_info = load_store_info("./data/chroma_db")
    if store_info["status"] == "success":
        m1, m2, m3 = st.columns(3)
        m1.metric("Indexed Docs", store_info["document_count"])
        m2.metric("Store Status", "Ready" if store_info["document_count"] > 0 else "Empty")
        m3.metric("LLM Backend", os.getenv("GEEKGREP_LLM_BACKEND", "openai").title())
        st.markdown("")

    # Query input
    question = st.text_area(
        "Your question",
        placeholder="e.g.  What are the key findings in section 3?",
        height=100,
    )

    # Settings row
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        top_k = st.slider("Sources to retrieve", 1, 10, 4)
    with c2:
        file_type = st.selectbox("File type filter", ["All", "PDF", "Markdown", "Text"])
    with c3:
        st.markdown("")
        ask = st.button("Search & Answer", use_container_width=True, type="primary")

    # Execute
    if ask:
        if not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Searching …"):
                ft_map = {"All": None, "PDF": "pdf", "Markdown": "md", "Text": "txt"}
                result = query(
                    question, "./data/chroma_db",
                    k=top_k, file_type=ft_map[file_type],
                )

            if result["status"] == "success":
                st.markdown("---")
                st.markdown("#### Answer")
                st.markdown(result["answer"])

                if result["sources"]:
                    st.markdown("#### Sources")
                    for i, src in enumerate(result["sources"], 1):
                        with st.expander(f"Source {i} — {Path(src['filename']).name}"):
                            st.caption(src["filename"])
                            st.caption(f"Type: {src['file_type']}")
                else:
                    st.info("No matching sources found.")
            else:
                st.error(result["answer"])


def render_settings_tab():
    """Render the settings tab"""
    st.markdown("### Configuration")
    st.markdown("")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**LLM Backend**")
        backend = st.radio(
            "Backend", ["OpenAI", "Ollama"],
            horizontal=True, label_visibility="collapsed",
        )
        os.environ["GEEKGREP_LLM_BACKEND"] = backend.lower()

    with c2:
        st.markdown("**Model**")
        models = (
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
            if backend == "OpenAI"
            else ["mistral", "llama2", "neural-chat"]
        )
        model = st.selectbox("Model", models, label_visibility="collapsed")
        os.environ["GEEKGREP_MODEL"] = model


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    render_header()

    tab_upload, tab_query, tab_settings = st.tabs([
        "UPLOAD", "QUERY", "SETTINGS"
    ])

    with tab_upload:
        render_upload_tab()

    with tab_query:
        render_query_tab()

    with tab_settings:
        render_settings_tab()

    # Footer
    st.markdown("---")
    st.caption("geekGrep v1.0  ·  Local RAG Document Query System")


if __name__ == "__main__":
    main()
