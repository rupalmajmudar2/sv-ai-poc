#!/usr/bin/env python3
"""
Vector Database Explorer Script
Explore ChromaDB collections and their contents
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def explore_collections():
    """Explore all ChromaDB collections and show their contents"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    # Initialize the vector store
    print('Initializing vector store...')
    vs = VectorStoreService()
    
    # Get collection info
    collections = vs.client.list_collections()
    print(f'\n=== ChromaDB Collections ({len(collections)} total) ===')
    
    total_documents = 0
    
    for collection in collections:
        print(f'\n📁 Collection: {collection.name}')
        count = collection.count()
        total_documents += count
        print(f'   📊 Documents: {count}')
        
        # Get a sample of documents
        if count > 0:
            sample = collection.get(limit=3, include=['metadatas', 'documents'])
            print(f'   📄 Sample documents:')
            for i, (doc, meta) in enumerate(zip(sample['documents'], sample['metadatas'])):
                print(f'      {i+1}. {doc[:120]}...')
                print(f'         🏷️  Metadata: {json.dumps(meta, indent=10)}')
        else:
            print('   ⚠️  No documents found')
        print()
    
    print(f'📈 Total documents across all collections: {total_documents}')
    return vs

def main():
    """Main function"""
    try:
        vs = explore_collections()
        print("✅ Vector database exploration completed successfully!")
        return vs
    except Exception as e:
        print(f"❌ Error exploring vector database: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()