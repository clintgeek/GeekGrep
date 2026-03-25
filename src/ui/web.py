"""Streamlit web interface for geekGrep."""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add app root to path for imports
app_root = Path(__file__).parent.parent.parent
if str(app_root) not in sys.path:
    sys.path.insert(0, str(app_root))

from src.pipeline import ingest, query, get_store_info

load_dotenv()

# Cache expensive operations
@st.cache_resource
def load_store_info(persist_dir):
    """Cache store info to avoid repeated initialization."""
    return get_store_info(persist_dir)

# Page configuration
st.set_page_config(
    page_title="geekGrep",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
    }
    .loading-message {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Show loading message on first run
if "initialized" not in st.session_state:
    with st.spinner("🚀 Initializing geekGrep... (first load may take 30 seconds)"):
        # Trigger cache initialization
        load_store_info("./data/chroma_db")
    st.session_state.initialized = True


def main():
    st.title("📚 geekGrep")
    st.markdown("*Intelligent document query system powered by local AI*")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Backend selection
        backend = st.radio(
            "LLM Backend",
            options=["OpenAI", "Ollama"],
            help="Choose between cloud (OpenAI) or local (Ollama) inference"
        )
        
        backend_value = "openai" if backend == "OpenAI" else "ollama"
        os.environ["GEEKGREP_LLM_BACKEND"] = backend_value
        
        # Model selection
        if backend == "OpenAI":
            model = st.selectbox(
                "Model",
                options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
                help="Select the OpenAI model to use"
            )
        else:
            model = st.selectbox(
                "Model",
                options=["mistral", "llama2", "neural-chat"],
                help="Select the Ollama model to use"
            )
        
        os.environ["GEEKGREP_MODEL"] = model
        
        # Vector store settings
        st.divider()
        st.subheader("Vector Store")
        
        persist_dir = st.text_input(
            "Store Location",
            value="./data/chroma_db",
            help="Path where the vector store is saved"
        )
        
        # Store info (cached)
        store_info = load_store_info(persist_dir)
        if store_info["status"] == "success":
            st.metric("Documents Stored", store_info["document_count"])
        
        # Ingestion section
        st.divider()
        st.subheader("📥 Ingest Documents")
        
        # File upload option
        uploaded_files = st.file_uploader(
            "Upload documents (drag & drop or click)",
            type=["pdf", "md", "txt"],
            accept_multiple_files=True,
            help="Upload PDF, Markdown, or text files"
        )
        
        if uploaded_files:
            reset_store = st.checkbox("Reset Store", value=False)
            if st.button("📤 Upload & Ingest", use_container_width=True, type="primary"):
                with st.spinner("Uploading and ingesting documents..."):
                    # Create temp directory for uploads
                    import tempfile
                    import shutil
                    
                    temp_dir = tempfile.mkdtemp()
                    try:
                        # Save uploaded files
                        for uploaded_file in uploaded_files:
                            file_path = Path(temp_dir) / uploaded_file.name
                            file_path.write_bytes(uploaded_file.getbuffer())
                        
                        # Ingest from temp directory
                        result = ingest(temp_dir, persist_dir, reset=reset_store)
                        
                        if result["status"] == "success":
                            st.success(
                                f"✓ Ingested {result['documents_loaded']} documents "
                                f"into {result['chunks_created']} chunks"
                            )
                        else:
                            st.error(f"Ingestion failed: {result['message']}")
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            # Directory ingestion option
            st.info("Or ingest from a directory:")
            docs_dir = st.text_input(
                "Documents Directory",
                value="./documents",
                help="Directory containing PDF, Markdown, or text files"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                reset_store = st.checkbox("Reset Store", value=False)
            
            with col2:
                if st.button("🔄 Ingest", use_container_width=True):
                    if not Path(docs_dir).exists():
                        st.error(f"Directory not found: {docs_dir}")
                    else:
                        with st.spinner("Ingesting documents..."):
                            result = ingest(docs_dir, persist_dir, reset=reset_store)
                        
                        if result["status"] == "success":
                            st.success(
                                f"✓ Ingested {result['documents_loaded']} documents "
                                f"into {result['chunks_created']} chunks"
                            )
                        else:
                            st.error(f"Ingestion failed: {result['message']}")
    
    # Main content area
    tab1, tab2 = st.tabs(["📤 Upload", "🔍 Query"])
    
    with tab1:
        st.header("Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Drag and drop files here or click to browse",
            type=["pdf", "md", "txt"],
            accept_multiple_files=True,
            key="main_uploader",
            help="Upload PDF, Markdown, or text files"
        )
        
        if uploaded_files:
            col1, col2 = st.columns(2)
            with col1:
                reset_store = st.checkbox("Reset Store before uploading", value=False, key="main_reset")
            
            with col2:
                st.write("")  # Spacer
            
            # Display file list
            st.subheader("Files to upload:")
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size:,} bytes)")
            
            if st.button("📤 Upload & Ingest", use_container_width=True, type="primary", key="main_upload_btn"):
                with st.spinner("Uploading and ingesting documents..."):
                    import tempfile
                    import shutil
                    
                    temp_dir = tempfile.mkdtemp()
                    try:
                        # Save uploaded files
                        for uploaded_file in uploaded_files:
                            file_path = Path(temp_dir) / uploaded_file.name
                            file_path.write_bytes(uploaded_file.getbuffer())
                        
                        # Ingest from temp directory
                        result = ingest(temp_dir, persist_dir, reset=reset_store)
                        
                        if result["status"] == "success":
                            st.success(
                                f"✓ Ingested {result['documents_loaded']} documents "
                                f"into {result['chunks_created']} chunks"
                            )
                            st.balloons()
                        else:
                            st.error(f"Ingestion failed: {result['message']}")
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            st.info("👆 Upload documents to get started")
    
    with tab2:
        st.header("🔍 Query Documents")
        
        # Query input
        question = st.text_area(
            "Ask a question about your documents:",
            placeholder="What is...",
            height=100
        )
        
        # Query settings
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider(
                "Number of documents to retrieve",
                min_value=1,
                max_value=10,
                value=4
            )
        
        with col2:
            file_type_filter = st.selectbox(
                "Filter by file type (optional)",
                options=["All", "PDF", "Markdown", "Text"],
                help="Limit search to specific file types"
            )
        
        file_type_map = {
            "All": None,
            "PDF": "pdf",
            "Markdown": "md",
            "Text": "txt"
        }
        
        # Query button
        if st.button("🚀 Ask", use_container_width=True, type="primary"):
            if not question.strip():
                st.warning("Please enter a question")
            else:
                with st.spinner("Searching and generating answer..."):
                    result = query(
                        question,
                        persist_dir,
                        k=top_k,
                        file_type=file_type_map[file_type_filter]
                    )
                
                if result["status"] == "success":
                    # Display answer
                    st.markdown("### Answer")
                    st.markdown(result["answer"])
                    
                    # Display sources
                    if result["sources"]:
                        st.markdown("### 📄 Sources")
                        
                        for i, source in enumerate(result["sources"], 1):
                            with st.expander(
                                f"Source {i}: {Path(source['filename']).name} "
                                f"(chunk {source['chunk_index']})"
                            ):
                                st.caption(f"File: {source['filename']}")
                                st.caption(f"Type: {source['file_type']}")
                    else:
                        st.info("No sources found for this query")
                else:
                    st.error(f"Query failed: {result['answer']}")
    
    # Footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8rem;'>
        geekGrep v1.0 | Local RAG Document Query System
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
