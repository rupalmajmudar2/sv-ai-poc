# SportzVillage AI Tests

This folder contains all tests for the SportzVillage AI application.

## Test Organization

### Test Files

- `test_database_interface.py` - Tests database interface compliance and TextDatabase implementation
- `test_chat_logging.py` - Tests chat logging functionality and user interaction tracking
- `test_setup.py` - Tests basic project setup and dependency validation
- `test_logging_simple.py` - Simple logging tests without complex dependencies

### Test Runner

- `run_tests.py` - Main test runner that executes all tests

## Running Tests

### Run All Tests
```bash
cd tests
python run_tests.py
```

### Run Individual Tests
```bash
# Database tests
python test_database_interface.py

# Chat logging tests  
python test_chat_logging.py

# Setup validation
python test_setup.py

# Simple logging tests
python test_logging_simple.py
```

### Run from Project Root
```bash
# Using virtual environment
C:/Users/rupal/work/repos/sv-ai-poc-v1/venv/Scripts/python.exe tests/run_tests.py

# Or activate environment first
.\venv\Scripts\Activate.ps1
python tests/run_tests.py
```

## Test Requirements

- Virtual environment with dependencies installed
- `.env` file configured (see `.env.example`)
- Text database files in `data/txt_tables/` (auto-created if missing)

## Test Types

### Unit Tests
- Database interface compliance
- Chat logging functionality
- Data validation

### Integration Tests  
- Database and chat logger integration
- Agent component interaction
- File system operations

### System Tests
- End-to-end functionality
- Configuration validation
- Environment setup

## Coverage

Tests cover:
- ✅ Database abstraction layer (interface compliance)
- ✅ Text-based database implementation
- ✅ Chat logging and interaction tracking
- ✅ User authentication (simplified for text DB)
- ✅ Timetable, lesson, and props operations
- ✅ Vector store integration (graceful degradation)
- ✅ Configuration and environment setup

## Notes

- Tests use temporary directories for file operations
- Vector store tests gracefully handle missing OpenAI API keys
- Database tests use mock data to avoid requiring real data files
- All tests include proper cleanup procedures

## Adding New Tests

1. Create new test file following naming pattern: `test_<feature>.py`
2. Include proper imports and path setup
3. Add comprehensive error handling
4. Include cleanup in finally blocks
5. Follow the existing test patterns and documentation