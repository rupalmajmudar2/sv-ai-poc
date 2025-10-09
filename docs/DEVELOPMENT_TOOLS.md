# Development Tools Documentation

This document describes the development and build tools in the `tools/` directory.

## 🛠️ Core Development Scripts

### `tools/setup.py` - Main Setup & Environment Manager
**Purpose**: Comprehensive project setup, dependency management, and application launcher

**Usage**:
```bash
# Full setup and run
python tools/setup.py --run

# Setup with continuous testing
python tools/setup.py --watch

# Run tests only
python tools/setup.py --test

# Setup only (no run)
python tools/setup.py
```

**Features**:
- Python version validation (3.8+)
- Virtual environment creation/validation
- Dependency installation
- Environment variable setup
- Application launching
- Test execution

### `tools/setup_venv.py` - Virtual Environment Creator
**Purpose**: Clean virtual environment creation with fresh dependencies

**Usage**:
```bash
# Create clean virtual environment
python tools/setup_venv.py
```

**Features**:
- Removes existing venv if present
- Creates new virtual environment
- Installs all requirements
- Validates installation
- Cross-platform compatibility

### `tools/start_tests.py` - Continuous Test Runner
**Purpose**: Easy launcher for continuous testing suite

**Usage**:
```bash
# Start continuous testing
python tools/start_tests.py
```

**Features**:
- Dependency validation
- Initial test suite execution
- File monitoring for changes
- Automatic test re-execution
- Real-time feedback

## ⚙️ Configuration Files

### `pytest.ini` - Test Configuration
**Location**: Project root (required by pytest)
**Purpose**: Centralized pytest configuration for consistent testing

**Key Settings**:
- Test discovery paths and patterns
- Output formatting and verbosity
- Test markers for categorization
- Coverage settings
- Timeout and failure limits
- Warning filters for clean output

**Test Markers**:
- `unit` - Fast, isolated unit tests
- `integration` - Slower integration tests
- `agent` - LangGraph/LangChain agent tests
- `database` - Database operation tests
- `tools` - Tool functionality tests
- `ui` - Streamlit interface tests
- `slow` - Time-intensive tests
- `smoke` - Basic functionality tests

## 📁 Project Structure Integration

These tools integrate with the project structure:

```
sv-ai-poc-v1/
├── tools/
│   ├── setup.py             # 🚀 Main setup & launcher
│   ├── setup_venv.py       # 🐍 Virtual environment creator
│   └── start_tests.py      # 🧪 Continuous test runner
├── pytest.ini              # ⚙️ Test configuration (root required)
├── requirements.txt         # 📦 Dependencies
├── .env                     # 🔐 Environment variables
└── ...
```

## 🔧 Development Workflow

### Initial Setup
1. Run `python tools/setup_venv.py` for clean environment
2. Run `python tools/setup.py` to validate setup
3. Run `python tools/setup.py --test` to verify everything works

### Daily Development
1. Use `python tools/setup.py --run` for quick start
2. Use `python tools/start_tests.py` for test-driven development
3. Use `python tools/setup.py --watch` for full development mode

### Testing
- **Quick Tests**: `python tools/setup.py --test`
- **Continuous Tests**: `python tools/start_tests.py`
- **Specific Tests**: `pytest -m unit` (using markers)

## 🆘 Troubleshooting

### Common Issues
- **Environment Issues**: Run `python tools/setup_venv.py` to reset
- **Dependency Issues**: Check `requirements.txt` and re-run setup
- **Test Issues**: Check `pytest.ini` configuration
- **Permission Issues**: Ensure virtual environment is activated

### Debug Mode
Most scripts have verbose output to help debug setup issues. Check the console output for specific error messages and suggestions.

## 🔄 Maintenance

These tools are designed to be:
- **Self-contained**: No external dependencies beyond Python
- **Cross-platform**: Work on Windows, macOS, and Linux
- **Idempotent**: Safe to run multiple times
- **Validated**: Include error checking and user feedback

Regular maintenance involves keeping `requirements.txt` updated and ensuring pytest configuration stays current with project needs.