#!/usr/bin/env python3
"""
Virtual Environment Setup Script for SportzVillage AI Assistant

This script creates a clean virtual environment and installs all dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path


def create_venv():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    
    venv_path = Path("venv")
    
    # Remove existing venv if it exists
    if venv_path.exists():
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    # Create new virtual environment
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False


def get_venv_python():
    """Get path to virtual environment Python executable"""
    if os.name == 'nt':  # Windows
        return Path("venv") / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        return Path("venv") / "bin" / "python"


def get_venv_pip():
    """Get path to virtual environment pip executable"""
    if os.name == 'nt':  # Windows
        return Path("venv") / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        return Path("venv") / "bin" / "pip"


def install_dependencies():
    """Install dependencies in virtual environment"""
    print("\n📦 Installing dependencies in virtual environment...")
    
    venv_pip = get_venv_pip()
    
    try:
        # Upgrade pip first
        subprocess.check_call([str(venv_pip), "install", "--upgrade", "pip"])
        print("✅ Pip upgraded successfully!")
        
        # Install requirements
        subprocess.check_call([str(venv_pip), "install", "-r", "requirements.txt"])
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


def create_activation_script():
    """Create activation scripts for easy environment activation"""
    print("\n📝 Creating activation scripts...")
    
    # Windows activation script
    activate_bat = """@echo off
echo 🏆 Activating SportzVillage AI Assistant Environment...
call venv\\Scripts\\activate.bat
echo ✅ Virtual environment activated!
echo.
echo To run the application:
echo   python main.py (for Streamlit)
echo   python test_setup.py (to test setup)
echo.
echo To deactivate: deactivate
"""
    
    with open("activate.bat", "w") as f:
        f.write(activate_bat)
    
    # PowerShell activation script
    activate_ps1 = """Write-Host "🏆 Activating SportzVillage AI Assistant Environment..." -ForegroundColor Cyan
& .\\venv\\Scripts\\Activate.ps1
Write-Host "✅ Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "  streamlit run main.py (for Streamlit UI)" -ForegroundColor White
Write-Host "  python test_setup.py (to test setup)" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate: deactivate" -ForegroundColor Yellow
"""
    
    with open("activate.ps1", "w") as f:
        f.write(activate_ps1)
    
    print("✅ Created activation scripts: activate.bat and activate.ps1")


def create_run_script():
    """Create script to run the application"""
    print("\n🚀 Creating run scripts...")
    
    # Windows run script
    run_bat = """@echo off
echo 🏆 Starting SportzVillage AI Assistant...
call venv\\Scripts\\activate.bat
streamlit run main.py
"""
    
    with open("run.bat", "w") as f:
        f.write(run_bat)
    
    # PowerShell run script
    run_ps1 = """Write-Host "🏆 Starting SportzVillage AI Assistant..." -ForegroundColor Cyan
& .\\venv\\Scripts\\Activate.ps1
streamlit run main.py
"""
    
    with open("run.ps1", "w") as f:
        f.write(run_ps1)
    
    print("✅ Created run scripts: run.bat and run.ps1")


def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    
    venv_python = get_venv_python()
    
    try:
        # Test Python imports
        test_script = """
import sys
print(f"Python: {sys.version}")

try:
    import streamlit
    print("✅ Streamlit imported successfully")
except ImportError as e:
    print(f"❌ Streamlit import failed: {e}")

try:
    import langchain
    print("✅ LangChain imported successfully")
except ImportError as e:
    print(f"❌ LangChain import failed: {e}")

try:
    import chromadb
    print("✅ ChromaDB imported successfully")
except ImportError as e:
    print(f"❌ ChromaDB import failed: {e}")

try:
    import pandas
    print("✅ Pandas imported successfully")
except ImportError as e:
    print(f"❌ Pandas import failed: {e}")

print("✅ Basic import test completed!")
"""
        
        result = subprocess.run([str(venv_python), "-c", test_script], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main setup function"""
    print("🏆 SportzVillage AI Assistant - Virtual Environment Setup")
    print("=" * 60)
    
    # Create virtual environment
    if not create_venv():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Create helper scripts
    create_activation_script()
    create_run_script()
    
    # Test installation
    if not test_installation():
        print("⚠️ Some tests failed, but basic setup is complete")
    
    print("\n" + "=" * 60)
    print("✅ Virtual Environment Setup Complete!")
    print("\nNext steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Activate environment:")
    print("   • Windows: activate.bat")
    print("   • PowerShell: .\\activate.ps1")
    print("3. Run application:")
    print("   • Windows: run.bat")
    print("   • PowerShell: .\\run.ps1")
    print("   • Manual: streamlit run main.py")
    print("4. Test setup: python test_setup.py")


if __name__ == "__main__":
    main()