#!/usr/bin/env python3
"""
Continuous Test Suite Runner for SportzVillage AI
Monitors file changes and runs tests automatically to ensure code quality.

This script provides:
1. File watching for automatic test execution
2. Parallel test execution for speed
3. Coverage reporting
4. HTML test reports
5. Real-time feedback with colored output
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse
from datetime import datetime
import threading
import queue


class TestHandler(FileSystemEventHandler):
    """Handle file system events and trigger test runs"""
    
    def __init__(self, test_queue):
        self.test_queue = test_queue
        self.last_run = 0
        self.debounce_time = 2  # seconds
        
    def should_trigger_tests(self, file_path):
        """Determine if file change should trigger tests"""
        # Only trigger on Python files
        if not file_path.endswith('.py'):
            return False
            
        # Skip __pycache__ and .pyc files
        if '__pycache__' in file_path or file_path.endswith('.pyc'):
            return False
            
        # Skip hidden files and directories
        if any(part.startswith('.') for part in Path(file_path).parts):
            return False
            
        return True
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        current_time = time.time()
        if current_time - self.last_run < self.debounce_time:
            return
            
        if self.should_trigger_tests(event.src_path):
            self.last_run = current_time
            self.test_queue.put(('file_change', event.src_path))


class ContinuousTestRunner:
    """Main test runner with continuous monitoring"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.test_queue = queue.Queue()
        self.observer = Observer()
        self.python_exe = self._get_python_executable()
        
    def _get_python_executable(self):
        """Get the Python executable path"""
        venv_python = self.project_root / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            print(f"🐍 Using virtual environment: {venv_python}")
            return str(venv_python)
        print(f"🐍 Using system Python: {sys.executable}")
        return sys.executable
    
    def run_tests(self, test_type="full", changed_file=None):
        """Run the test suite"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if changed_file:
            print(f"\n🔄 [{timestamp}] File changed: {changed_file}")
        
        print(f"🚀 [{timestamp}] Running {test_type} test suite...")
        
        # Base pytest command
        cmd = [
            self.python_exe, "-m", "pytest",
            "-v",                    # Verbose output
            "--tb=short",           # Short traceback format
            "--color=yes",          # Colored output
            "-x",                   # Stop on first failure
        ]
        
        # Add coverage reporting
        if test_type == "full":
            cmd.extend([
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-report=xml",
            ])
        
        # Add HTML report generation
        if test_type == "full":
            cmd.extend([
                "--html=test_reports/report.html",
                "--self-contained-html"
            ])
        
        # Specify test directory
        cmd.append("tests/")
        
        try:
            # Create reports directory
            reports_dir = self.project_root / "test_reports"
            reports_dir.mkdir(exist_ok=True)
            
            # Run tests
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Print results
            if result.returncode == 0:
                print(f"✅ [{timestamp}] All tests passed!")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"❌ [{timestamp}] Tests failed!")
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
            
            # Print coverage summary if available
            if test_type == "full" and "coverage" in result.stdout.lower():
                coverage_lines = [line for line in result.stdout.split('\n') 
                                if 'coverage' in line.lower() or '%' in line]
                if coverage_lines:
                    print("\n📊 Coverage Summary:")
                    for line in coverage_lines[-5:]:  # Last 5 coverage-related lines
                        print(f"   {line}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"⏰ [{timestamp}] Tests timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"💥 [{timestamp}] Error running tests: {e}")
            return False
    
    def start_file_watching(self):
        """Start watching for file changes"""
        handler = TestHandler(self.test_queue)
        
        # Watch source code directories
        self.observer.schedule(handler, str(self.project_root / "src"), recursive=True)
        self.observer.schedule(handler, str(self.project_root / "tests"), recursive=True)
        self.observer.schedule(handler, str(self.project_root / "main.py"), recursive=False)
        
        self.observer.start()
        print(f"👁️  Watching for file changes in {self.project_root}")
    
    def stop_file_watching(self):
        """Stop watching for file changes"""
        self.observer.stop()
        self.observer.join()
    
    def run_continuous(self, initial_run=True):
        """Run tests continuously"""
        print("🎯 SportzVillage AI - Continuous Test Suite")
        print("=" * 50)
        print("Benefits of LangGraph Migration:")
        print("✅ Modern agent workflows with state management")
        print("✅ Human-in-the-loop capabilities for approval workflows")
        print("✅ Better tool composition and parallel execution")
        print("✅ Robust error handling and recovery")
        print("✅ Future-proof architecture with active development")
        print("=" * 50)
        
        if initial_run:
            print("\n🏁 Running initial full test suite...")
            self.run_tests("full")
        
        self.start_file_watching()
        
        try:
            while True:
                try:
                    # Wait for events with timeout
                    event_type, file_path = self.test_queue.get(timeout=1)
                    
                    if event_type == 'file_change':
                        # Run quick tests on file change
                        self.run_tests("quick", file_path)
                        
                except queue.Empty:
                    continue
                except KeyboardInterrupt:
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping continuous test runner...")
        finally:
            self.stop_file_watching()
    
    def run_single(self, test_type="full"):
        """Run tests once and exit"""
        print("🎯 SportzVillage AI - Single Test Run")
        print("=" * 50)
        success = self.run_tests(test_type)
        return 0 if success else 1


def main():
    parser = argparse.ArgumentParser(
        description="SportzVillage AI Continuous Test Suite"
    )
    parser.add_argument(
        "--mode", 
        choices=["continuous", "single", "watch"],
        default="continuous",
        help="Test execution mode"
    )
    parser.add_argument(
        "--type",
        choices=["full", "quick"],
        default="full", 
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-initial-run",
        action="store_true",
        help="Skip initial test run in continuous mode"
    )
    
    args = parser.parse_args()
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Create test runner
    runner = ContinuousTestRunner(project_root)
    
    if args.mode == "continuous":
        runner.run_continuous(initial_run=not args.no_initial_run)
        return 0
    elif args.mode == "single":
        return runner.run_single(args.type)
    elif args.mode == "watch":
        # Watch mode - only run tests on file changes
        runner.run_continuous(initial_run=False)
        return 0


if __name__ == "__main__":
    sys.exit(main())