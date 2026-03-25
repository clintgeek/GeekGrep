"""Streamlit web interface for geekGrep - Modern, Outstanding UI."""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import tempfile
import shutil

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

# Custom CSS - Refined Minimalism with Precision
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    :root {
        --primary: #0f172a;
        --secondary: #1e293b;
        --accent: #f97316;
        --accent-light: #fed7aa;
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --border: #334155;
        --success: #10b981;
    }
    
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
        color: var(--text-primary);
    }
    
    .main {
        padding: 2rem 3rem;
        background: transparent;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1a1f35 100%);
    }
    
    /* Typography */
    h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #f1f5f9 0%, #fed7aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    h2 {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: var(--text-primary);
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: var(--accent);
        margin-top: 1.5rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f35 0%, #0f172a 100%);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding: 2rem 1.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid var(--border);
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1rem;
        font-weight: 500;
        color: var(--text-secondary);
        border: none;
        border-bottom: 3px solid transparent;
        padding: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: var(--accent);
        border-bottom-color: var(--accent);
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--accent);
        border-bottom-color: var(--accent);
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, #ea580c 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(249, 115, 22, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background: var(--secondary) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed var(--border);
        border-radius: 0.75rem;
        padding: 2rem;
        background: rgba(30, 41, 59, 0.5);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--accent);
        background: rgba(249, 115, 22, 0.05);
    }
    
    /* Divider */
    .stDivider {
        border-color: var(--border);
    }
    
    /* Metrics */
    .stMetric {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid var(--border);
        border-radius: 0.75rem;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: var(--accent);
        box-shadow: 0 4px 20px rgba(249, 115, 22, 0.1);
    }
    
    /* Alerts */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid var(--success);
        border-radius: 0.5rem;
        color: #a7f3d0;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 0.5rem;
        color: #fca5a5;
    }
    
    .stWarning {
        background: rgba(249, 115, 22, 0.1);
        border: 1px solid var(--accent);
        border-radius: 0.5rem;
        color: var(--accent-light);
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid #3b82f6;
        border-radius: 0.5rem;
        color: #93c5fd;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--secondary);
        border: 1px solid var(--border);
        border-radius: 0.5rem;
        color: var(--text-primary);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: var(--accent);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        color: var(--accent);
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 1.5rem;
    }
    
    .stRadio > div > label {
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Checkbox */
    .stCheckbox > label {
        color: var(--text-primary);
        font-weight: 500;
    }
    
    /* Loading message */
    .loading-message {
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.95rem;
        letter-spacing: 0.05em;
    }
    
    /* Smooth transitions */
    * {
        transition: color 0.2s ease, background 0.2s ease, border-color 0.2s ease;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
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
    # Hero section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("geekGrep")
    with col2:
        st.write("")
    
    st.markdown("""
    <div style="margin-bottom: 3rem; color: #cbd5e1; font-size: 1.1rem; letter-spacing: 0.05em;">
    Intelligent document query system powered by local AI
    </div>
    """, unsafe_allow_html=True)
    
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
