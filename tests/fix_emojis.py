#!/usr/bin/env python3
"""
Fix Unicode emojis in test files for Windows compatibility
"""

import os
import re
from pathlib import Path

def fix_emojis_in_file(file_path):
    """Replace emojis with text equivalents in a file"""
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Emoji replacements
    replacements = {
        '🧪': '[TEST]',
        '✅': '[OK]',
        '❌': '[FAIL]',
        '⚠️': '[WARNING]',
        '🎉': '[SUCCESS]',
        '📊': '[ANALYTICS]',
        '📚': '[INFO]',
        '🔍': '[SEARCH]',
        '🚀': '[START]',
        '🧹': '[CLEANUP]',
        '⏰': '[TIMEOUT]',
        '💥': '[ERROR]',
        '🔄': '[REFRESH]',
        '📁': '[FILES]',
        '📋': '[DATA]',
        '⚡': '[SPEED]',
        '🛠️': '[TOOLS]',
        '💬': '[CHAT]',
        '🤖': '[BOT]',
        '👤': '[USER]',
        '👥': '[USERS]',
        '📈': '[METRICS]',
        '🏆': '[TROPHY]',
        '⚙️': '[CONFIG]',
        '🔧': '[SETUP]',
        '🎯': '[TARGET]',
        '📝': '[NOTE]',
        '🔐': '[SECURE]'
    }
    
    # Apply replacements
    original_content = content
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    # Only write if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed emojis in: {file_path}")
        return True
    else:
        print(f"No emojis found in: {file_path}")
        return False

def main():
    """Fix emojis in all test files"""
    tests_dir = Path(__file__).parent
    
    test_files = list(tests_dir.glob("test_*.py"))
    
    print(f"Fixing emojis in {len(test_files)} test files...")
    
    fixed_count = 0
    for test_file in test_files:
        if fix_emojis_in_file(test_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()