#!/usr/bin/env python3
"""
Test Chat Logging Functionality
Simple test for user interaction tracking
"""

import sys
import os
from pathlib import Path
import tempfile
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))


def test_chat_logging_simple():
    """Simple test of chat logging without full dependencies"""
    print("[TEST] Testing Chat Logging (Simple)")
    
    # Test chat logger directly
    from src.database.chat_logger import ChatLogger
    
    # Create temporary directory for logs
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize chat logger with temp directory
        chat_logger = ChatLogger(log_dir=temp_dir)
        
        # Test logging an interaction
        test_user = {
            'user_id': 'test_user',
            'name': 'Test User',
            'role': 'R',
            'school_id': 'SCH001'
        }
        
        # Log the interaction using correct parameters
        chat_logger.log_interaction(
            user_info=test_user,
            message='What is my timetable?',
            response='Here is your timetable for today...',
            tools_used=['timetable_tool'],
            response_time=1.23
        )
        
        # Verify files were created
        assert chat_logger.csv_file.exists(), "CSV log file should be created"
        assert chat_logger.json_file.exists(), "JSON log file should be created"
        
        # Test retrieving chat history
        history = chat_logger.get_user_chat_history('test_user', limit=5)
        assert len(history) >= 1, "Should retrieve logged interaction"
        
        retrieved = history[0]
        assert retrieved['user']['user_id'] == 'test_user'
        assert retrieved['interaction']['message'] == 'What is my timetable?'
        
        print("[OK] Chat logging basic functionality works")
        
        # Test analytics
        analytics = chat_logger.get_analytics()
        assert analytics['total_interactions'] >= 1
        assert analytics['unique_users'] >= 1  # Should be count, not list
        
        print("[OK] Chat analytics work")
        
        print("[OK] Chat logging test completed successfully!")
        assert True
        
    except Exception as e:
        print(f"[ERROR] Chat logging test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Chat logging test failed: {e}"
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        print(f"[CLEANUP] Cleaned up temp directory: {temp_dir}")


def test_agent_integration():
    """Test basic agent integration without OpenAI"""
    print("[TEST] Testing Agent Integration (without OpenAI)")
    
    try:
        # Test that we can import agent components
        from src.database.text_db import TextDatabase
        from src.database.chat_logger import ChatLogger
        
        # Test database initialization
        db = TextDatabase()
        print("[OK] TextDatabase initializes correctly")
        
        # Test chat logger initialization
        temp_dir = tempfile.mkdtemp()
        chat_logger = ChatLogger(log_dir=temp_dir)
        print("[OK] ChatLogger initializes correctly")
        
        # Test basic database operations
        users = db._read_table('users')
        print(f"[OK] Database can read tables (found {len(users)} users)")
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
        print("[OK] Agent integration test completed!")
        assert True
        
    except Exception as e:
        print(f"[ERROR] Agent integration test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Agent integration test failed: {e}"


if __name__ == "__main__":
    print("[TEST] SportzVillage Chat Logging Test Suite\n")
    
    # Run tests
    tests = [
        test_chat_logging_simple,
        test_agent_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{'='*50}")
        if test():
            passed += 1
        print(f"{'='*50}")
    
    print(f"\n[RESULT] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("[FAILED] Some tests failed!")
        sys.exit(1)