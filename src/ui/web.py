"""geekGrep - Modern, Outstanding Document Query Interface v2.0"""

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

# Page config - must come before any other st calls
st.set_page_config(
    page_title="geekGrep",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS - Focus on what works in Streamlit
st.markdown("""
<style>
body {
    background-color: #0f1419;
    color: #e0e7ff;
}
</style>
""", unsafe_allow_html=True)

# Simple cache for store info
_store_cache = {}

def load_store_info(persist_dir):
    """Get store info with simple caching."""
    if persist_dir not in _store_cache:
        _store_cache[persist_dir] = get_store_info(persist_dir)
    return _store_cache[persist_dir]

def render_hero():
    """Render the hero section"""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h1>geekGrep</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p class="subtitle">
        Intelligent document query system powered by local AI
        </p>
        """, unsafe_allow_html=True)

def render_upload_section():
    """Render the upload section"""
    st.markdown("<h2>📤 Upload & Ingest</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Drag files here or click to browse",
            type=["pdf", "md", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} file(s) selected**")
            for f in uploaded_files:
                st.caption(f"📄 {f.name} ({f.size:,} bytes)")
    
    with col2:
        reset = st.checkbox("Reset store", value=False)
        if st.button("🚀 Ingest", use_container_width=True, type="primary"):
            if uploaded_files:
                with st.spinner("Processing documents..."):
                    temp_dir = tempfile.mkdtemp()
                    try:
                        for f in uploaded_files:
                            Path(temp_dir, f.name).write_bytes(f.getbuffer())
                        result = ingest(temp_dir, "./data/chroma_db", reset=reset)
                        
                        if result["status"] == "success":
                            st.success(f"✓ Ingested {result['documents_loaded']} documents into {result['chunks_created']} chunks")
                            st.balloons()
                        else:
                            st.error(f"Failed: {result['message']}")
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)

def render_query_section():
    """Render the query section"""
    st.markdown("<h2>🔍 Query Documents</h2>", unsafe_allow_html=True)
    
    # Store info
    store_info = load_store_info("./data/chroma_db")
    if store_info["status"] == "success":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Documents", store_info["document_count"])
        with col2:
            st.metric("Status", "Ready" if store_info["document_count"] > 0 else "Empty")
        with col3:
            st.metric("Backend", os.getenv("GEEKGREP_LLM_BACKEND", "openai").upper())
    
    st.divider()
    
    # Query input
    question = st.text_area(
        "Ask a question about your documents:",
        placeholder="What is the main topic of these documents?",
        height=120,
        label_visibility="collapsed"
    )
    
    # Query settings
    col1, col2, col3 = st.columns(3)
    with col1:
        top_k = st.slider("Results", 1, 10, 4)
    with col2:
        file_type = st.selectbox(
            "Filter by type",
            ["All", "PDF", "Markdown", "Text"],
            label_visibility="collapsed"
        )
    with col3:
        st.write("")  # Spacer
    
    # Query button
    if st.button("🎯 Ask", use_container_width=True, type="primary"):
        if not question.strip():
            st.warning("Please enter a question")
        else:
            with st.spinner("Searching and generating answer..."):
                file_type_map = {"All": None, "PDF": "pdf", "Markdown": "md", "Text": "txt"}
                result = query(
                    question,
                    "./data/chroma_db",
                    k=top_k,
                    file_type=file_type_map[file_type]
                )
            
            if result["status"] == "success":
                st.markdown("### Answer")
                st.markdown(result["answer"])
                
                if result["sources"]:
                    st.markdown("### 📚 Sources")
                    for i, source in enumerate(result["sources"], 1):
                        with st.expander(f"Source {i}: {Path(source['filename']).name}"):
                            st.caption(f"📄 {source['filename']}")
                            st.caption(f"Type: {source['file_type']}")
                else:
                    st.info("No sources found")
            else:
                st.error(f"Query failed: {result['answer']}")

def render_config_section():
    """Render configuration section"""
    st.markdown("<h2>⚙️ Configuration</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        backend = st.radio(
            "LLM Backend",
            ["OpenAI", "Ollama"],
            horizontal=True
        )
        os.environ["GEEKGREP_LLM_BACKEND"] = backend.lower()
    
    with col2:
        if backend == "OpenAI":
            models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
        else:
            models = ["mistral", "llama2", "neural-chat"]
        
        model = st.selectbox("Model", models, label_visibility="collapsed")
        os.environ["GEEKGREP_MODEL"] = model

def main():
    """Main app"""
    render_hero()
    st.divider()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "🔍 Query", "⚙️ Settings"])
    
    with tab1:
        render_upload_section()
    
    with tab2:
        render_query_section()
    
    with tab3:
        render_config_section()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 3rem;">
    geekGrep v1.0 • Local RAG Document Query System
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
