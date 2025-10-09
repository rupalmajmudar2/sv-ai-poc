#!/usr/bin/env python3
"""
Vector Database Management Script
Populate, refresh, or reset the vector database
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def populate_vectordb():
    """Populate the vector database with sample data"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    print('🔄 Populating vector database...')
    vs = VectorStoreService()
    
    # The VectorStoreService automatically populates sample data on initialization
    # Let's also manually refresh to ensure we have the latest data
    
    try:
        print('📊 Refreshing vector cache...')
        vs.refresh_cache()
        print('✅ Vector database populated and refreshed successfully!')
        
        # Show summary
        collections = vs.client.list_collections()
        total_docs = sum(collection.count() for collection in collections)
        print(f'📈 Total collections: {len(collections)}')
        print(f'📈 Total documents: {total_docs}')
        
        for collection in collections:
            count = collection.count()
            print(f'   📁 {collection.name}: {count} documents')
            
    except Exception as e:
        print(f'❌ Error populating vector database: {e}')
        import traceback
        traceback.print_exc()

def reset_vectordb():
    """Reset (clear) the vector database"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    print('⚠️  Resetting vector database...')
    response = input('Are you sure you want to delete all vector data? (yes/no): ')
    
    if response.lower() != 'yes':
        print('❌ Reset cancelled')
        return
    
    try:
        vs = VectorStoreService()
        
        # Delete all collections
        collections = vs.client.list_collections()
        for collection in collections:
            print(f'🗑️  Deleting collection: {collection.name}')
            vs.client.delete_collection(collection.name)
        
        print('✅ Vector database reset completed!')
        
    except Exception as e:
        print(f'❌ Error resetting vector database: {e}')
        import traceback
        traceback.print_exc()

def show_stats():
    """Show vector database statistics"""
    print("Loading environment variables...")
    load_dotenv()
    
    from src.database.vector_store import VectorStoreService
    
    print('📊 Vector Database Statistics')
    print('=' * 40)
    
    try:
        vs = VectorStoreService()
        collections = vs.client.list_collections()
        
        total_docs = 0
        for collection in collections:
            count = collection.count()
            total_docs += count
            print(f'📁 {collection.name:<15} {count:>6} documents')
        
        print('-' * 40)
        print(f'📈 Total:           {total_docs:>6} documents')
        print(f'📁 Collections:     {len(collections):>6}')
        
    except Exception as e:
        print(f'❌ Error getting statistics: {e}')

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage vector database')
    parser.add_argument('action', choices=['populate', 'reset', 'stats'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'populate':
        populate_vectordb()
    elif args.action == 'reset':
        reset_vectordb()
    elif args.action == 'stats':
        show_stats()

if __name__ == "__main__":
    main()