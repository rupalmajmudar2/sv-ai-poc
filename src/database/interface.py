from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum
import os
import json
import pandas as pd
from pathlib import Path
from loguru import logger


class UserRole(Enum):
    HO = "HO"  # Head Office
    RM = "RM"  # Regional Manager
    DM = "DM"  # Delivery Manager
    DL = "DL"  # Delivery Lead
    R = "R"    # Resident
    PRINCIPAL = "PRINCIPAL"


class DatabaseInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user credentials"""
        pass
    
    @abstractmethod
    def get_timetable(self, school_id: str, class_name: str = None, section: str = None) -> List[Dict[str, Any]]:
        """Get timetable for specific school/class/section"""
        pass
    
    @abstractmethod
    def get_lesson_plans(self, school_id: str) -> List[Dict[str, Any]]:
        """Get lesson plans for a school"""
        pass
    
    @abstractmethod
    def get_lessons(self, lesson_plan_id: str = None) -> List[Dict[str, Any]]:
        """Get lesson details"""
        pass
    
    @abstractmethod
    def get_props(self, school_id: str = None) -> List[Dict[str, Any]]:
        """Get props information"""
        pass
    
    @abstractmethod
    def get_events(self, school_id: str, date_range: tuple = None) -> List[Dict[str, Any]]:
        """Get events for a school within date range"""
        pass
    
    @abstractmethod
    def log_lesson_completion(self, data: Dict[str, Any]) -> bool:
        """Log completed lesson"""
        pass
    
    @abstractmethod
    def update_prop_status(self, prop_id: str, status: str, resident_id: str) -> bool:
        """Update prop status"""
        pass
    
    @abstractmethod
    def get_residents_under_manager(self, manager_id: str) -> List[Dict[str, Any]]:
        """Get residents under a DM/RM"""
        pass
    
    @abstractmethod
    def semantic_search(self, query: str, context_type: str = "all", school_id: str = None) -> str:
        """Perform semantic search across cached data"""
        pass
    
    @abstractmethod
    def refresh_vector_cache(self) -> bool:
        """Refresh vector database cache"""
        pass


class MySQLDatabase(DatabaseInterface):
    """MySQL database implementation - placeholder for future implementation"""
    
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        logger.info(f"MySQLDatabase initialized (not implemented yet)")
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_timetable(self, school_id: str, class_name: str = None, section: str = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_lesson_plans(self, school_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_lessons(self, lesson_plan_id: str = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_props(self, school_id: str = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_events(self, school_id: str, date_range: tuple = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def log_lesson_completion(self, data: Dict[str, Any]) -> bool:
        raise NotImplementedError("MySQL implementation pending")
    
    def update_prop_status(self, prop_id: str, status: str, resident_id: str) -> bool:
        raise NotImplementedError("MySQL implementation pending")
    
    def get_residents_under_manager(self, manager_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError("MySQL implementation pending")
    
    def semantic_search(self, query: str, context_type: str = "all", school_id: str = None) -> str:
        raise NotImplementedError("MySQL implementation pending")
    
    def refresh_vector_cache(self) -> bool:
        raise NotImplementedError("MySQL implementation pending")


# Global database instance
_database_instance = None

def get_database() -> DatabaseInterface:
    """Factory function to get database instance based on configuration"""
    global _database_instance
    
    if _database_instance is None:
        db_type = os.getenv("DB_TYPE", "text")
        
        if db_type == "text":
            from .text_db import TextDatabase
            _database_instance = TextDatabase()
        elif db_type == "mysql":
            _database_instance = MySQLDatabase(
                host=os.getenv("MYSQL_HOST"),
                port=int(os.getenv("MYSQL_PORT", 3306)),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE")
            )
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _database_instance


def reset_database_instance():
    """Reset the database instance - useful for testing or configuration changes"""
    global _database_instance
    _database_instance = None
        
        
# Legacy alias for backwards compatibility
MockDatabase = None  # Use TextDatabase instead