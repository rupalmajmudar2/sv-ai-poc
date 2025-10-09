import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# Disable ChromaDB telemetry globally
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY"] = "False"


class VectorStoreService:
    """Vector database service for caching and semantic search"""
    
    def __init__(self, persist_directory: str = None):
        # Disable ChromaDB telemetry completely
        os.environ["ANONYMIZED_TELEMETRY"] = "False"
        
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chromadb")
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize collections
        self._init_collections()
        
        # Text splitter for large documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def _init_collections(self):
        """Initialize ChromaDB collections for different data types"""
        try:
            # Collection for timetables
            self.timetables_collection = self.client.get_or_create_collection(
                name="timetables",
                metadata={"description": "School timetable data"}
            )
            
            # Collection for lesson plans
            self.lessons_collection = self.client.get_or_create_collection(
                name="lessons",
                metadata={"description": "Lesson plans and lesson details"}
            )
            
            # Collection for props
            self.props_collection = self.client.get_or_create_collection(
                name="props",
                metadata={"description": "Sports equipment and props data"}
            )
            
            # Collection for reports and documents
            self.documents_collection = self.client.get_or_create_collection(
                name="documents",
                metadata={"description": "Reports, guidelines, and documentation"}
            )
            
            # Collection for user context and preferences
            self.context_collection = self.client.get_or_create_collection(
                name="user_context",
                metadata={"description": "User preferences and context data"}
            )
            
            logger.info("ChromaDB collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collections: {e}")
            raise
    
    def index_timetable_data(self, timetable_data: List[Dict[str, Any]]):
        """Index timetable data for semantic search"""
        documents = []
        metadatas = []
        ids = []
        
        for i, entry in enumerate(timetable_data):
            # Create searchable text
            text = f"""
            School: {entry['school_id']}
            Class: {entry['class']} Section: {entry['section']}
            Period: {entry['period_number']} ({entry['time_slot']})
            Subject: {entry['subject']}
            PE Period: {entry.get('is_pe_period', False)}
            """
            
            documents.append(text.strip())
            metadatas.append({
                "school_id": entry['school_id'],
                "class": entry['class'],
                "section": entry['section'],
                "period_number": entry['period_number'],
                "subject": entry['subject'],
                "type": "timetable"
            })
            ids.append(f"tt_{entry['school_id']}_{entry['class']}_{entry['section']}_{entry['period_number']}")
        
        if documents:
            self.timetables_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} timetable entries")
    
    def index_lesson_data(self, lessons_data: List[Dict[str, Any]], lesson_plans_data: List[Dict[str, Any]]):
        """Index lesson plans and lessons for semantic search"""
        documents = []
        metadatas = []
        ids = []
        
        # Index individual lessons
        for lesson in lessons_data:
            text = f"""
            Lesson: {lesson['name']}
            Description: {lesson['description']}
            Duration: {lesson['duration']} minutes
            Required Props: {', '.join(lesson.get('required_props', []))}
            """
            
            documents.append(text.strip())
            metadatas.append({
                "lesson_id": lesson['lesson_id'],
                "name": lesson['name'],
                "duration": lesson['duration'],
                "type": "lesson"
            })
            ids.append(f"lesson_{lesson['lesson_id']}")
        
        # Index lesson plans
        for lp in lesson_plans_data:
            text = f"""
            Lesson Plan: {lp['lesson_plan_id']}
            School: {lp['school_id']}
            Session: {lp['session']}
            Lessons: {', '.join(lp.get('lessons', []))}
            """
            
            documents.append(text.strip())
            metadatas.append({
                "lesson_plan_id": lp['lesson_plan_id'],
                "school_id": lp['school_id'],
                "session": lp['session'],
                "type": "lesson_plan"
            })
            ids.append(f"lp_{lp['lesson_plan_id']}")
        
        if documents:
            self.lessons_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} lesson entries")
    
    def index_props_data(self, props_data: List[Dict[str, Any]]):
        """Index props data for semantic search"""
        documents = []
        metadatas = []
        ids = []
        
        for prop in props_data:
            text = f"""
            Prop: {prop['type']}
            School: {prop['school_id']}
            Total Quantity: {prop['quantity']}
            Available: {prop['available']}
            Status: {prop['status']}
            Utilization: {((prop['quantity'] - prop['available'])/prop['quantity']*100):.1f}%
            """
            
            documents.append(text.strip())
            metadatas.append({
                "prop_id": prop['prop_id'],
                "type": prop['type'],
                "school_id": prop['school_id'],
                "quantity": prop['quantity'],
                "available": prop['available'],
                "status": prop['status']
            })
            ids.append(f"prop_{prop['prop_id']}")
        
        if documents:
            self.props_collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} props entries")
    
    def semantic_search_timetables(self, query: str, school_id: str = None, 
                                 class_name: str = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search for timetable information"""
        where_clause = {}
        if school_id:
            where_clause["school_id"] = school_id
        if class_name:
            where_clause["class"] = class_name
        
        results = self.timetables_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        return self._format_search_results(results)
    
    def semantic_search_lessons(self, query: str, school_id: str = None, 
                              n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search for lesson information"""
        where_clause = {}
        if school_id:
            where_clause["school_id"] = school_id
        
        results = self.lessons_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        return self._format_search_results(results)
    
    def semantic_search_props(self, query: str, school_id: str = None, 
                            n_results: int = 5) -> List[Dict[str, Any]]:
        """Semantic search for props information"""
        where_clause = {}
        if school_id:
            where_clause["school_id"] = school_id
        
        results = self.props_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        return self._format_search_results(results)
    
    def search(self, query: str, n_results: int = 5, school_id: str = None) -> Dict[str, Any]:
        """Generic search across all collections"""
        all_results = {
            'documents': [],
            'metadatas': [],
            'distances': []
        }
        
        try:
            # Search timetables
            timetable_results = self.semantic_search_timetables(query, school_id, n_results)
            all_results['documents'].extend([r['document'] for r in timetable_results])
            all_results['metadatas'].extend([r['metadata'] for r in timetable_results])
            all_results['distances'].extend([r.get('distance', 0.0) for r in timetable_results])
            
            # Search lessons
            lesson_results = self.semantic_search_lessons(query, school_id, n_results)
            all_results['documents'].extend([r['document'] for r in lesson_results])
            all_results['metadatas'].extend([r['metadata'] for r in lesson_results])
            all_results['distances'].extend([r.get('distance', 0.0) for r in lesson_results])
            
            # Search props
            props_results = self.semantic_search_props(query, school_id, n_results)
            all_results['documents'].extend([r['document'] for r in props_results])
            all_results['metadatas'].extend([r['metadata'] for r in props_results])
            all_results['distances'].extend([r.get('distance', 0.0) for r in props_results])
            
            # Sort by relevance and limit results
            combined = list(zip(all_results['documents'], all_results['metadatas'], all_results['distances']))
            combined.sort(key=lambda x: x[2])  # Sort by distance (lower is better)
            combined = combined[:n_results]
            
            if combined:
                all_results = {
                    'documents': [item[0] for item in combined],
                    'metadatas': [item[1] for item in combined],
                    'distances': [item[2] for item in combined]
                }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            
        return all_results
    
    def cache_user_context(self, user_id: str, context_data: Dict[str, Any]):
        """Cache user context and preferences"""
        text = f"""
        User: {user_id}
        Role: {context_data.get('role', 'Unknown')}
        School: {context_data.get('school_id', 'Unknown')}
        Recent Activity: {json.dumps(context_data.get('recent_activity', {}), indent=2)}
        Preferences: {json.dumps(context_data.get('preferences', {}), indent=2)}
        """
        
        self.context_collection.upsert(
            documents=[text.strip()],
            metadatas=[{
                "user_id": user_id,
                "role": context_data.get('role'),
                "school_id": context_data.get('school_id'),
                "type": "user_context"
            }],
            ids=[f"context_{user_id}"]
        )
    
    def get_cached_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached user context"""
        try:
            results = self.context_collection.query(
                query_texts=[f"User: {user_id}"],
                n_results=1,
                where={"user_id": user_id}
            )
            
            if results['documents'] and len(results['documents'][0]) > 0:
                return results['metadatas'][0][0]
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached context for {user_id}: {e}")
            return None
    
    def store_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Store document for RAG retrieval"""
        # Split large documents into chunks
        chunks = self.text_splitter.split_text(content)
        
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": i,
                "total_chunks": len(chunks),
                "type": "document"
            })
            metadatas.append(chunk_metadata)
            ids.append(f"{doc_id}_chunk_{i}")
        
        self.documents_collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Stored document {doc_id} in {len(chunks)} chunks")
    
    def retrieve_relevant_context(self, query: str, context_type: str = "all", 
                                n_results: int = 5) -> str:
        """Retrieve relevant context for RAG"""
        relevant_docs = []
        
        if context_type in ["all", "timetables"]:
            tt_results = self.semantic_search_timetables(query, n_results=n_results)
            relevant_docs.extend([f"Timetable: {doc['document']}" for doc in tt_results])
        
        if context_type in ["all", "lessons"]:
            lesson_results = self.semantic_search_lessons(query, n_results=n_results)
            relevant_docs.extend([f"Lesson: {doc['document']}" for doc in lesson_results])
        
        if context_type in ["all", "props"]:
            props_results = self.semantic_search_props(query, n_results=n_results)
            relevant_docs.extend([f"Props: {doc['document']}" for doc in props_results])
        
        if context_type in ["all", "documents"]:
            doc_results = self.documents_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            formatted_docs = self._format_search_results(doc_results)
            relevant_docs.extend([f"Document: {doc['document']}" for doc in formatted_docs])
        
        return "\n\n".join(relevant_docs)
    
    def _format_search_results(self, results: Dict) -> List[Dict[str, Any]]:
        """Format ChromaDB search results"""
        formatted = []
        
        if not results['documents'] or not results['documents'][0]:
            return formatted
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        distances = results['distances'][0] if results['distances'] else []
        
        for i, doc in enumerate(documents):
            formatted.append({
                "document": doc,
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "score": 1 - distances[i] if i < len(distances) else 0.0
            })
        
        return formatted
    
    def refresh_all_data(self, database_interface):
        """Refresh all cached data from database"""
        try:
            logger.info("Refreshing vector store data...")
            
            # Clear existing collections
            self.client.delete_collection("timetables")
            self.client.delete_collection("lessons")
            self.client.delete_collection("props")
            
            # Recreate collections
            self._init_collections()
            
            # Re-index all data
            # Note: This is a simplified example - in production, you'd want to 
            # iterate through all schools efficiently
            sample_schools = ["SCH001", "SCH002", "SCH003"]
            
            for school_id in sample_schools:
                # Index timetable data
                timetables = database_interface.get_timetable(school_id)
                if timetables:
                    self.index_timetable_data(timetables)
                
                # Index props data
                props = database_interface.get_props(school_id)
                if props:
                    self.index_props_data(props)
                
                # Index lesson plans
                lesson_plans = database_interface.get_lesson_plans(school_id)
                if lesson_plans:
                    lessons = database_interface.get_lessons()
                    self.index_lesson_data(lessons, lesson_plans)
            
            logger.info("Vector store refresh completed")
            
        except Exception as e:
            logger.error(f"Error refreshing vector store: {e}")
            raise


# Global vector store instance
_vector_store = None


def get_vector_store() -> VectorStoreService:
    """Get global vector store instance"""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStoreService()
    
    return _vector_store