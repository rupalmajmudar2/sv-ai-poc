#!/usr/bin/env python3
"""
Quick script to start the continuous test suite for SportzVillage AI.
This script provides an easy way to run tests with the new LangGraph-powered agent.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Start the continuous test suite"""
    project_root = Path(__file__).parent
    
    print("🚀 Starting SportzVillage AI Continuous Test Suite")
    print("📋 This will:")
    print("   • Install/update dependencies")
    print("   • Run initial test suite")
    print("   • Monitor files for changes")
    print("   • Run tests automatically on code changes")
    print("   • Generate coverage reports")
    print("\n💡 Press Ctrl+C to stop\n")
    
    # First, install/update dependencies
    print("📦 Installing/updating dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, cwd=project_root)
        print("✅ Dependencies updated")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return 1
    
    # Start continuous test runner
    try:
        subprocess.run([
            sys.executable, "tests/continuous_runner.py", "--mode", "continuous"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n👋 Test suite stopped")
        return 0
    except Exception as e:
        print(f"❌ Error running test suite: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())