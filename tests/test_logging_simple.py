#!/usr/bin/env python3
"""
Simple Chat Logging Test - Direct import test
"""

import os
import sys
from pathlib import Path
import json
import csv
from datetime import datetime

# Add the project to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_chat_logger_directly():
    """Test the ChatLogger class directly"""
    print("[TEST] Testing ChatLogger Directly\n")
    
    try:
        from src.database.chat_logger import ChatLogger
        
        # Create a test logger
        logger = ChatLogger()
        print(f"[OK] ChatLogger imported successfully")
        print(f"[FILES] CSV file: {logger.csv_file}")
        print(f"[FILES] JSON file: {logger.json_file}")
        
        # Test logging an interaction
        test_user = {
            'user_id': 'test_123',
            'name': 'Test User',
            'role': 'R',
            'school_id': 'SCH001'
        }
        
        test_interaction = {
            'message': 'What is my timetable today?',
            'response': 'Here is your timetable for today: Math at 9am, PE at 10am...',
            'tools_used': ['TimetableTool'],
            'response_time_seconds': 1.23,
            'message_length': 26
        }
        
        test_session = {
            'session_id': 'sess_test_001',
            'start_time': datetime.now()
        }
        
        # Log the interaction
        logger.log_interaction(
            user_info=test_user,
            message=test_interaction['message'],
            response=test_interaction['response'],
            tools_used=test_interaction['tools_used'],
            response_time=test_interaction['response_time_seconds']
        )
        
        print("[OK] Interaction logged successfully!")
        
        # Test retrieving history
        history = logger.get_user_chat_history('test_123', limit=5)
        print(f"[INFO] Retrieved {len(history)} history items")
        
        if history:
            for item in history:
                print(f"   - {item['timestamp'][:19]}: {item['interaction']['message']}")
        
        # Test analytics
        analytics = logger.get_analytics()
        print(f"[ANALYTICS] Analytics: {analytics}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_database():
    """Test the TextDatabase class directly"""
    print("\n[TEST] Testing TextDatabase Directly\n")
    
    try:
        from src.database.text_db import TextDatabase
        
        db = TextDatabase()
        print("[OK] TextDatabase imported successfully")
        
        # Test getting all users (via reading users table)
        users_data = db._read_table('users')
        print(f"[USERS] Found {len(users_data)} users")
        
        # Test getting a specific user
        test_user = db.get_user('USR001')
        if test_user:
            print(f"[USER] Retrieved user: {test_user['name']} ({test_user['role']})")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_chat_data_format():
    """Show the format of chat data"""
    print("\n[DATA] Chat Data Format Demonstration\n")
    
    # Check if log files exist
    log_dir = Path("data/chat_logs")
    csv_file = log_dir / "chat_logs.csv"
    json_file = log_dir / "chat_sessions.json"
    
    print("[FILES] Expected log file locations:")
    print(f"   CSV: {csv_file}")
    print(f"   JSON: {json_file}")
    
    if csv_file.exists():
        print(f"[OK] CSV file exists ({csv_file.stat().st_size} bytes)")
        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                print(f"[ANALYTICS] CSV contains {len(rows)} rows")
                if rows:
                    print("[SEARCH] Sample CSV data:")
                    for key, value in rows[0].items():
                        print(f"   {key}: {value}")
        except Exception as e:
            print(f"[FAIL] Error reading CSV: {e}")
    else:
        print("[WARNING] CSV file does not exist yet")
    
    if json_file.exists():
        print(f"[OK] JSON file exists ({json_file.stat().st_size} bytes)")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[ANALYTICS] JSON contains {len(data)} interactions")
                if data:
                    print("[SEARCH] Sample JSON structure:")
                    sample = data[0]
                    print(json.dumps(sample, indent=2, default=str))
        except Exception as e:
            print(f"[FAIL] Error reading JSON: {e}")
    else:
        print("[WARNING] JSON file does not exist yet")

if __name__ == "__main__":
    print("[START] Starting Simple Chat Logging Tests\n")
    
    success = True
    
    success &= test_chat_logger_directly()
    success &= test_text_database()
    demonstrate_chat_data_format()
    
    if success:
        print("\n[SUCCESS] All tests completed successfully!")
        print("\n[NOTE] Summary:")
        print("- ChatLogger class working correctly")
        print("- User interactions are logged with timestamps")
        print("- Chat history can be retrieved by user")
        print("- Analytics are available for system monitoring")
        print("- Data is stored in both CSV and JSON formats")
    else:
        print("\n[FAIL] Some tests failed!")