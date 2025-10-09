"""
Simple text-based database implementation for SportzVillage AI
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger

from .interface import DatabaseInterface
from .vector_store import VectorStoreService


class TextDatabase(DatabaseInterface):
    """Simplified text-file based database for development"""
    
    def __init__(self):
        # Initialize vector store
        self._init_vector_store()
        
        # Path to text table files
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'txt_tables')
        
        # In-memory storage for runtime data
        self.lesson_completions = []
        self.prop_updates = []
        
        logger.info("TextDatabase initialized")
    
    def _init_vector_store(self):
        """Initialize vector store service"""
        try:
            # Disable ChromaDB telemetry
            os.environ["ANONYMIZED_TELEMETRY"] = "False"
            
            from .vector_store import get_vector_store
            self.vector_store = get_vector_store()
            logger.info("Vector store initialized")
        except Exception as e:
            logger.warning(f"Vector store initialization failed: {e}")
            self.vector_store = None
    
    def _read_table(self, table_name: str) -> List[Dict[str, Any]]:
        """Read a table from a text file and return as list of dictionaries"""
        file_path = os.path.join(self.data_dir, f"{table_name}.txt")
        if not os.path.exists(file_path):
            logger.warning(f"Table file not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) < 2:  # Need header + at least one data row
                return []
            
            headers = lines[0].strip().split('|')
            data = []
            
            for line in lines[1:]:
                if line.strip():  # Skip empty lines
                    values = line.strip().split('|')
                    if len(values) == len(headers):
                        row = {}
                        for i, header in enumerate(headers):
                            value = values[i]
                            # Convert special fields
                            if header in ['period_number', 'duration', 'quantity', 'available']:
                                row[header] = int(value) if value else 0
                            elif header in ['is_pe_period']:
                                row[header] = value.lower() == 'true'
                            elif header in ['lessons', 'required_props'] and ',' in value:
                                row[header] = value.split(',') if value else []
                            else:
                                row[header] = value if value else None
                        data.append(row)
            return data
        except Exception as e:
            logger.error(f"Error reading table {table_name}: {e}")
            return []
    
    # Authentication (simplified for mock)
    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """For text database, skip authentication validation and return user if exists"""
        users = self._read_table('users')
        user = next((u for u in users if u.get('user_id') == user_id), None)
        if user:
            logger.info(f"Mock authentication successful for user: {user_id}")
            return user
        logger.warning(f"User not found: {user_id}")
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        users = self._read_table('users')
        return next((user for user in users if user.get("user_id") == user_id), None)
    
    # Timetable operations
    def get_timetable(self, school_id: str, class_name: str = None, section: str = None) -> List[Dict[str, Any]]:
        timetables = self._read_table('timetables')
        result = [tt for tt in timetables if tt.get("school_id") == school_id]
        if class_name:
            result = [tt for tt in result if tt.get("class") == class_name]
        if section:
            result = [tt for tt in result if tt.get("section") == section]
        return result
    
    # Lesson operations
    def get_lesson_plans(self, school_id: str) -> List[Dict[str, Any]]:
        lesson_plans = self._read_table('lesson_plans')
        return [lp for lp in lesson_plans if lp.get("school_id") == school_id]
    
    def get_lessons(self, lesson_plan_id: str = None) -> List[Dict[str, Any]]:
        lessons_data = self._read_table('lessons')
        
        if lesson_plan_id:
            lesson_plans = self._read_table('lesson_plans')
            lp = next((lp for lp in lesson_plans if lp.get("lesson_plan_id") == lesson_plan_id), None)
            if lp and lp.get("lessons"):
                lesson_ids = lp["lessons"]
                return [lesson for lesson in lessons_data if lesson.get("lesson_id") in lesson_ids]
            return []
        
        return lessons_data
    
    def log_lesson_completion(self, data: Dict[str, Any]) -> bool:
        # Add timestamp if not provided
        if 'timestamp' not in data:
            from datetime import datetime
            data['timestamp'] = datetime.now().isoformat()
            
        self.lesson_completions.append(data.copy())
        logger.info(f"Lesson completion logged: {data.get('lesson_id', 'unknown')}")
        return True
    
    # Props operations
    def get_props(self, school_id: str = None) -> List[Dict[str, Any]]:
        props = self._read_table('props')
        if school_id:
            return [prop for prop in props if prop.get("school_id") == school_id]
        return props
    
    def update_prop_status(self, prop_id: str, status: str, resident_id: str) -> bool:
        update = {
            "timestamp": "2024-01-01 10:00:00",  # Simplified for mock
            "prop_id": prop_id,
            "status": status,
            "resident_id": resident_id
        }
        self.prop_updates.append(update)
        logger.info(f"Prop status updated: {prop_id} -> {status}")
        return True
    
    # Event operations
    def get_events(self, school_id: str, date_range: tuple = None) -> List[Dict[str, Any]]:
        # For now, return empty list since we don't have events table
        return []
    
    # Communication operations
    def send_sms(self, to: str, message: str, sender_id: str) -> bool:
        logger.info(f"SMS sent (mock): {message}")
        return True
    
    # Management operations
    def get_residents_for_manager(self, manager_id: str) -> List[Dict[str, Any]]:
        users = self._read_table('users')
        return [user for user in users if user.get("reports_to") == manager_id]
    
    def get_residents_under_manager(self, manager_id: str) -> List[Dict[str, Any]]:
        """Alias for get_residents_for_manager to match interface"""
        return self.get_residents_for_manager(manager_id)
    
    # Vector store operations
    def semantic_search(self, query: str, context_type: str = "all", school_id: str = None) -> str:
        if not self.vector_store:
            return "Vector search not available"
        
        try:
            results = self.vector_store.search(query, n_results=5)
            if results and results.get('documents'):
                return f"Search results for '{query}':\\n" + "\\n".join(results['documents'])
            return f"No results found for '{query}'"
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return f"Search error: {str(e)}"
    
    def refresh_vector_cache(self) -> bool:
        if not self.vector_store:
            return False
        
        try:
            # Read all data and refresh vector cache
            timetables = self._read_table('timetables')
            lessons = self._read_table('lessons')
            lesson_plans = self._read_table('lesson_plans')
            props = self._read_table('props')
            
            # Index all data
            if timetables:
                self.vector_store.index_timetables(timetables)
            if lessons:
                self.vector_store.index_lessons(lessons)
            if lesson_plans:
                self.vector_store.index_lesson_plans(lesson_plans)
            if props:
                self.vector_store.index_props(props)
                
            logger.info("Vector cache refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Vector cache refresh failed: {e}")
            return False