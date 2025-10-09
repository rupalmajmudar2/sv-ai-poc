# Vector Database Explorer Tools - Quick Reference

## 🚀 Quick Start

### Windows Users
```batch
# Interactive menu (recommended)
scripts\vector_explorer.bat

# Direct commands
venv\Scripts\python.exe scripts\explore_vectordb.py
venv\Scripts\python.exe scripts\test_semantic_search.py --query "your question"
```

### Unix/Linux/macOS Users
```bash
# Interactive menu (recommended)
chmod +x scripts/vector_explorer.sh
scripts/vector_explorer.sh

# Direct commands
venv/bin/python scripts/explore_vectordb.py
venv/bin/python scripts/test_semantic_search.py --query "your question"
```

## 📊 Current Database Status

**Collections:** 5 total
- `lessons` (3 docs) - PE lesson plans and descriptions
- `documents` (4 docs) - Curriculum and safety guidelines  
- `timetables` (4 docs) - Class schedules with PE periods
- `props` (2 docs) - Sports equipment inventory
- `user_context` (0 docs) - User interaction context

**Total Documents:** 13 across all collections

## 🔍 Sample Queries That Work

```
"What football equipment is available?"
"Show me the PE lessons about football" 
"What classes have PE periods?"
"Tell me about physical education curriculum"
"How many footballs do we have?"
"What sports equipment needs repair?"
"Show me advanced lessons for older students"
```

## 📁 Available Scripts

| Script | Purpose | Example Usage |
|--------|---------|---------------|
| `explore_vectordb.py` | Browse collections & documents | `python scripts/explore_vectordb.py` |
| `test_semantic_search.py` | Test search with queries | `python scripts/test_semantic_search.py --query "football"` |
| `manage_vectordb.py` | Database management | `python scripts/manage_vectordb.py stats` |
| `vector_explorer.bat` | Windows interactive menu | `scripts\vector_explorer.bat` |
| `vector_explorer.sh` | Unix interactive menu | `scripts/vector_explorer.sh` |

## 🛠 Management Commands

```bash
# Show database statistics
python scripts/manage_vectordb.py stats

# Refresh/populate database
python scripts/manage_vectordb.py populate

# Reset database (DANGER!)
python scripts/manage_vectordb.py reset
```

## 🔧 Environment Requirements

Ensure your `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key
CHROMA_PERSIST_DIRECTORY=./data/chromadb
SV_DEBUG_MODE=false  # for clean output
```

The scripts automatically load environment variables and work with your existing setup!