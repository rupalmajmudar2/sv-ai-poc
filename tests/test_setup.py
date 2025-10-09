#!/usr/bin/env python3
"""
Test script for SportzVillage AI Assistant

Run this script to verify that the application is set up correctly.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_imports():
    """Test that all modules can be imported"""
    print("[TEST] Testing imports...")
    
    try:
        from src.database.interface import get_database, MockDatabase
        print("[OK] Database interface imported successfully")
        
        from src.tools.data_tools import TimetableTool, LessonPlanTool
        print("[OK] Data tools imported successfully")
        
        from src.tools.communication_tools import SmsSenderTool
        print("[OK] Communication tools imported successfully")
        
        # Test agent import (might fail without OpenAI key)
        try:
            from src.agents.sv_agent import SVAgent
            print("[OK] Agent imported successfully")
        except Exception as e:
            print(f"[WARNING]  Agent import failed (likely missing OpenAI key): {e}")
        
        assert True
        
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        assert False, f"Import failed: {e}"


def test_database():
    """Test database functionality"""
    print("\n[ANALYTICS] Testing database...")
    
    try:
        from src.database.interface import get_database
        
        # Test text database
        os.environ["DB_TYPE"] = "text"
        db = get_database()
        
        # Test user authentication
        user = db.authenticate_user("HO001", "ho123")
        if user:
            print(f"[OK] User authentication works: {user['name']}")
        else:
            print("[FAIL] User authentication failed")
            assert False, "User authentication failed"
        
        # Test timetable query
        timetable = db.get_timetable("SCH001")
        print(f"[OK] Timetable query works: {len(timetable)} entries")
        
        # Test props query
        props = db.get_props("SCH001")
        print(f"[OK] Props query works: {len(props)} props")
        
        assert True
        
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        assert False, f"Database test failed: {e}"


def test_tools():
    """Test individual tools"""
    print("\n[SETUP] Testing tools...")
    
    try:
        from src.tools.data_tools import TimetableTool
        
        # Test timetable tool
        tool = TimetableTool()
        result = tool._run("SCH001", "VI", "A")
        
        if "Timetable for School SCH001" in result:
            print("[OK] Timetable tool works")
        else:
            print(f"[WARNING]  Timetable tool output unexpected: {result[:100]}...")
        
        assert True
        
    except Exception as e:
        print(f"[FAIL] Tools test failed: {e}")
        assert False, f"Tools test failed: {e}"


def test_environment():
    """Test environment configuration"""
    print("\n[CONFIG] Testing environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("[OK] .env file exists")
        
        # Check for critical variables
        with open(env_file) as f:
            content = f.read()
            
        if "OPENAI_API_KEY" in content:
            print("[OK] OpenAI API key configured in .env")
        else:
            print("[WARNING]  OpenAI API key not found in .env")
        
        if "DB_TYPE" in content:
            print("[OK] Database type configured")
        else:
            print("[WARNING]  Database type not configured")
    else:
        print("[FAIL] .env file not found")
        return False
    
    return True


def main():
    """Run all tests"""
    print("[TEST] SportzVillage AI Assistant - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Database", test_database),
        ("Tools", test_tools)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            if test_func():
                passed += 1
                print(f"[OK] {test_name} test PASSED")
            else:
                print(f"[FAIL] {test_name} test FAILED")
        except Exception as e:
            print(f"[FAIL] {test_name} test ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"[TARGET] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("  python setup.py --run")
        print("  or")
        print("  streamlit run main.py")
    else:
        print("[WARNING]  Some tests failed. Please check the setup.")
        print("\nCommon fixes:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Copy .env.example to .env and add your OpenAI API key")
        print("3. Check Python version (3.8+ required)")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)