#!/usr/bin/env python3
"""
Vector Database Semantic Search Tester
Test semantic search capabilities with various queries
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_semantic_search():
    """Test semantic search with predefined queries"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    # Initialize the vector store
    print('🔍 Testing semantic search capabilities...\n')
    vs = VectorStoreService()
    
    # Test queries
    queries = [
        'What football equipment is available?',
        'Show me the PE lessons about football',
        'What classes have PE periods?',
        'Tell me about physical education curriculum',
        'How many footballs do we have?',
        'What sports equipment needs repair?',
        'Show me advanced lessons for older students'
    ]
    
    for query in queries:
        print(f'🔎 Query: "{query}"')
        print('=' * 60)
        
        try:
            results = vs.search(query, n_results=3)
            
            # Process the search results
            if results and 'documents' in results and results['documents']:
                processed_results = []
                docs = results['documents']
                metas = results['metadatas'] if 'metadatas' in results else []
                dists = results['distances'] if 'distances' in results else []
                
                for i in range(len(docs)):
                    processed_results.append({
                        'content': docs[i],
                        'metadata': metas[i] if i < len(metas) else {},
                        'score': 1.0 - dists[i] if i < len(dists) else 0.0
                    })
                
                for i, result in enumerate(processed_results, 1):
                    print(f'   {i}. 📊 Score: {result["score"]:.3f}')
                    print(f'      🏷️  Type: {result["metadata"].get("type", "unknown")}')
                    print(f'      📄 Content: {result["content"][:150]}...')
                    
                    # Show key metadata
                    meta = result["metadata"]
                    key_fields = ['school_id', 'class', 'lesson_id', 'prop_id', 'subject']
                    relevant_meta = {k: v for k, v in meta.items() if k in key_fields}
                    if relevant_meta:
                        print(f'      🔗 Key Info: {relevant_meta}')
                    print()
            else:
                print("   ⚠️  No results found")
        
        except Exception as e:
            print(f"   ❌ Error searching: {e}")
        
        print('\n' + '='*80 + '\n')

def test_custom_query(query: str, top_k: int = 3):
    """Test a custom search query"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    print(f'🔍 Testing custom query: "{query}"\n')
    vs = VectorStoreService()
    
    try:
        results = vs.search(query, n_results=top_k)
        
        # Process the search results
        if results and 'documents' in results and results['documents']:
            processed_results = []
            docs = results['documents']
            metas = results['metadatas'] if 'metadatas' in results else []
            dists = results['distances'] if 'distances' in results else []
            
            for i in range(len(docs)):
                processed_results.append({
                    'content': docs[i],
                    'metadata': metas[i] if i < len(metas) else {},
                    'score': 1.0 - dists[i] if i < len(dists) else 0.0
                })
            
            for i, result in enumerate(processed_results, 1):
                print(f'{i}. 📊 Score: {result["score"]:.3f}')
                print(f'   🏷️  Type: {result["metadata"].get("type", "unknown")}')
                print(f'   📄 Content: {result["content"][:200]}...')
                print(f'   🔗 Metadata: {result["metadata"]}')
                print()
        else:
            print("   ⚠️  No results found")
    
    except Exception as e:
        print(f"❌ Error searching: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test vector database semantic search')
    parser.add_argument('--query', '-q', type=str, help='Custom query to test')
    parser.add_argument('--top-k', '-k', type=int, default=3, help='Number of results to return')
    
    args = parser.parse_args()
    
    try:
        if args.query:
            test_custom_query(args.query, args.top_k)
        else:
            test_semantic_search()
        
        print("✅ Semantic search testing completed successfully!")
    
    except Exception as e:
        print(f"❌ Error testing semantic search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()