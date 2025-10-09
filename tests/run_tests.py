#!/usr/bin/env python3
"""
SportzVillage AI Test Runner
Runs all tests in the tests folder
"""

import sys
import os
from pathlib import Path
import subprocess

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def run_test(test_file):
    """Run a single test file"""
    print(f"[TEST] Running {test_file.name}...")
    
    try:
        # Get Python executable from virtual environment
        python_exe = project_root / "venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = "python"  # Fallback to system python
        
        result = subprocess.run(
            [str(python_exe), str(test_file)],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"[OK] {test_file.name} PASSED")
            if result.stdout:
                print("Output:")
                print(result.stdout)
            return True
        else:
            print(f"[FAIL] {test_file.name} FAILED")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {test_file.name} TIMEOUT")
        return False
    except Exception as e:
        print(f"[ERROR] {test_file.name} ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("[TEST] SportzVillage AI Test Suite")
    print(f"Project root: {project_root}")
    print("=" * 50)
    
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("[WARNING] No test files found!")
        return 1
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file.name}")
    
    print("\n" + "=" * 50)
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        print(f"\n{'-' * 30}")
        if run_test(test_file):
            passed += 1
        print(f"{'-' * 30}")
    
    print(f"\n{'=' * 50}")
    print(f"[RESULT] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        return 0
    else:
        print("[FAILED] Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())