#!/usr/bin/env python3
"""
Setup script for SportzVillage AI Assistant

This script helps set up the development environment and run the application.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration"""
    print("\n⚙️ Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file")
        print("⚠️  Please edit .env file with your configuration (especially OPENAI_API_KEY)")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ .env.example file not found!")
        return False
    
    return True


def create_mock_data():
    """Initialize mock data if needed"""
    print("\n📊 Setting up mock data...")
    
    mock_data_dir = Path("data/mock_data")
    mock_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock data will be created automatically by the database interface
    print("✅ Mock data directory ready")
    return True


def run_application():
    """Run the Streamlit application"""
    print("\n🚀 Starting SportzVillage AI Assistant...")
    print("\nThe application will open in your browser.")
    print("Use Ctrl+C to stop the application.")
    print("\n" + "="*50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install dependencies first.")
        return False
    
    return True


def run_tests():
    """Run the test suite"""
    print("\n🧪 Running test suite...")
    print("This will test the LangGraph-powered agent across all user roles.")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], check=False)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("❌ Some tests failed. Check output above.")
            return False
            
    except FileNotFoundError:
        print("❌ pytest not found. Dependencies may not be installed properly.")
        return False


def start_continuous_tests():
    """Start the continuous test suite"""
    print("\n🔄 Starting continuous test suite...")
    print("This will monitor files and run tests automatically.")
    print("Press Ctrl+C to stop.")
    
    try:
        subprocess.run([sys.executable, "start_tests.py"])
    except KeyboardInterrupt:
        print("\n👋 Continuous testing stopped")
    except Exception as e:
        print(f"❌ Error starting continuous tests: {e}")


def main():
    """Main setup function"""
    print("🏆 SportzVillage AI Assistant Setup")
    print("=" * 40)
    print("🚀 Now powered by LangGraph for advanced agent workflows!")
    print("✨ Features: Human-in-the-loop, state management, parallel execution")
    print("=" * 40)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create mock data structure
    if not create_mock_data():
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\nAvailable options:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Run app: python setup.py --run")
    print("3. Run tests: python setup.py --test")
    print("4. Continuous tests: python setup.py --watch")
    print("5. Or use: streamlit run main.py")
    
    # Check command line arguments
    if "--run" in sys.argv or "-r" in sys.argv:
        print("\n" + "="*50)
        run_application()
    elif "--test" in sys.argv or "-t" in sys.argv:
        run_tests()
    elif "--watch" in sys.argv or "-w" in sys.argv:
        start_continuous_tests()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("\nUsage:")
        print("  python setup.py           # Setup only")
        print("  python setup.py --run     # Setup and run app")
        print("  python setup.py --test    # Setup and run tests")
        print("  python setup.py --watch   # Setup and start continuous testing")
        print("  python setup.py --help    # Show this help")


if __name__ == "__main__":
    main()