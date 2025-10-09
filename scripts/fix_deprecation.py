#!/usr/bin/env python3
"""
Fix LangChain deprecation warnings by updating packages
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {command}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {command} - Exception: {e}")
        return False

def main():
    """Update packages to fix deprecation warnings"""
    print("🔧 Fixing LangChain Deprecation Warnings\n")
    
    # Get Python executable
    python_exe = sys.executable
    
    # Update packages
    commands = [
        f'"{python_exe}" -m pip install --upgrade langchain-openai',
        f'"{python_exe}" -m pip install --upgrade langchain',
        f'"{python_exe}" -m pip install --upgrade openai'
    ]
    
    success_count = 0
    for command in commands:
        if run_command(command):
            success_count += 1
    
    print(f"\n📊 Updated {success_count}/{len(commands)} packages")
    
    if success_count == len(commands):
        print("\n✅ All packages updated successfully!")
        print("\n🚀 The deprecation warnings should now be resolved.")
        print("You can restart the Streamlit app to see the changes.")
    else:
        print("\n⚠️ Some package updates failed.")
        print("You may want to try updating manually:")
        print("   pip install --upgrade langchain-openai langchain openai")
    
    return success_count == len(commands)

if __name__ == "__main__":
    main()