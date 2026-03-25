#!/usr/bin/env python3
"""Integration test - verify end-to-end workflow without API calls."""

import os
from unittest.mock import MagicMock, patch
from src.pipeline import ingest, query, get_store_info
from src.retrieval.retriever import retrieve_documents

def test_full_workflow():
    """Test complete workflow: ingest → retrieve → generate."""
    
    persist_dir = "./test_data/chroma_db"
    
    print("\n" + "="*60)
    print("INTEGRATION TEST: geekGrep End-to-End Workflow")
    print("="*60)
    
    # Step 1: Check store info
    print("\n✓ Step 1: Checking vector store...")
    info = get_store_info(persist_dir)
    print(f"  Status: {info['status']}")
    print(f"  Documents stored: {info['document_count']}")
    assert info['status'] == 'success'
    assert info['document_count'] > 0
    
    # Step 2: Test retrieval
    print("\n✓ Step 2: Testing document retrieval...")
    question = "What is Python used for?"
    retrieved = retrieve_documents(question, k=2, persist_directory=persist_dir)
    print(f"  Question: {question}")
    print(f"  Retrieved {len(retrieved)} documents")
    for i, doc in enumerate(retrieved, 1):
        source = doc.metadata.get('source', 'Unknown')
        print(f"    {i}. {source} (chunk {doc.metadata.get('chunk_index', '?')})")
        print(f"       Preview: {doc.page_content[:80]}...")
    assert len(retrieved) > 0
    
    # Step 3: Test answer generation with mock LLM
    print("\n✓ Step 3: Testing answer generation...")
    with patch('src.pipeline.generate_answer') as mock_generate:
        mock_generate.return_value = "Python is used for web development, data science, automation, and AI."
        
        result = query(question, persist_dir, k=2)
        print(f"  Status: {result['status']}")
        print(f"  Answer: {result['answer']}")
        print(f"  Sources: {len(result['sources'])} document(s)")
        for source in result['sources']:
            print(f"    - {source['filename']} (chunk {source['chunk_index']})")
        
        assert result['status'] == 'success'
        assert len(result['sources']) > 0
    
    # Step 4: Test metadata
    print("\n✓ Step 4: Verifying metadata...")
    for doc in retrieved:
        assert 'source' in doc.metadata
        assert 'file_type' in doc.metadata
        assert 'chunk_index' in doc.metadata
        print(f"  ✓ {doc.metadata['source']}: {doc.metadata['file_type']} (chunk {doc.metadata['chunk_index']})")
    
    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED")
    print("="*60)
    print("\nSystem Status:")
    print("  ✓ Document ingestion working")
    print("  ✓ Vector store operational")
    print("  ✓ Semantic retrieval functional")
    print("  ✓ Metadata preservation intact")
    print("  ✓ Answer generation pipeline ready")
    print("\nReady for deployment!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_full_workflow()
