#!/usr/bin/env python3
"""
Simple Vector Database Test Script
Quick test of semantic search functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_search():
    """Simple search test"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    print('🔍 Testing vector database search...\n')
    vs = VectorStoreService()
    
    # Test search
    query = "What football equipment is available?"
    print(f'Query: "{query}"')
    print('=' * 50)
    
    try:
        # Try the generic search method
        results = vs.search(query, n_results=3)
        print(f"Search results type: {type(results)}")
        print(f"Search results keys: {results.keys() if isinstance(results, dict) else 'Not a dict'}")
        
        if isinstance(results, dict) and 'documents' in results:
            print(f"Found {len(results['documents'])} document groups")
            for i, docs in enumerate(results['documents']):
                print(f"Group {i}: {len(docs) if isinstance(docs, list) else 1} documents")
                if isinstance(docs, list):
                    for j, doc in enumerate(docs[:2]):  # Show first 2
                        print(f"  Doc {j}: {doc[:100]}...")
                else:
                    print(f"  Doc: {docs[:100]}...")
        else:
            print("Unexpected results format")
            print(f"Results: {results}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search()