# Vector Database Explorer Scripts

This directory contains scripts to explore and manage the ChromaDB vector database.

## Scripts Overview

### Python Scripts

1. **`explore_vectordb.py`** - Explore all collections and show sample documents
2. **`test_semantic_search.py`** - Test semantic search with predefined or custom queries  
3. **`manage_vectordb.py`** - Populate, refresh, or reset the vector database
4. **`simple_test.py`** - Simple vector database connection and search test

### Utility Scripts

5. **`disable_telemetry.py`** - Disable ChromaDB telemetry (standalone utility)
6. **`fix_deprecation.py`** - Update packages to fix LangChain deprecation warnings

### Interactive Menu Scripts

4. **`vector_explorer.bat`** - Windows batch file with interactive menu
5. **`vector_explorer.sh`** - Unix/Linux/macOS shell script with interactive menu

## Quick Usage

### Windows
```batch
# Run interactive explorer
scripts\vector_explorer.bat

# Or run individual scripts
cd scripts
python explore_vectordb.py
python test_semantic_search.py
python manage_vectordb.py stats
```

### Unix/Linux/macOS
```bash
# Make executable and run interactive explorer
chmod +x scripts/vector_explorer.sh
scripts/vector_explorer.sh

# Or run individual scripts
cd scripts
python explore_vectordb.py
python test_semantic_search.py
python manage_vectordb.py stats
```

## Individual Script Usage

### Explore Vector Database
```bash
python scripts/explore_vectordb.py
```
Shows all collections, document counts, and sample documents with metadata.

### Test Semantic Search
```bash
# Test with predefined queries
python scripts/test_semantic_search.py

# Test with custom query
python scripts/test_semantic_search.py --query "What football equipment is available?"

# Return more results
python scripts/test_semantic_search.py --query "PE lessons" --top-k 5
```

### Manage Vector Database
```bash
# Show statistics
python scripts/manage_vectordb.py stats

# Populate/refresh database
python scripts/manage_vectordb.py populate

# Reset (clear) database
python scripts/manage_vectordb.py reset
```

## Current Vector Database Contents

The database contains 5 collections:

- **`lessons`** (3 documents) - PE lesson plans and descriptions
- **`documents`** (4 documents) - Curriculum documents and equipment requirements
- **`timetables`** (4 documents) - Class schedules and PE periods
- **`props`** (2 documents) - Sports equipment inventory 
- **`user_context`** (0 documents) - User interaction context (populated during use)

## Sample Queries

Try these semantic search queries:
- "What football equipment is available?"
- "Show me the PE lessons about football"
- "What classes have PE periods?"
- "Tell me about physical education curriculum"
- "How many footballs do we have?"
- "What sports equipment needs repair?"
- "Show me advanced lessons for older students"

## Environment Requirements

Make sure your `.env` file contains:
```
OPENAI_API_KEY=your_openai_api_key
CHROMA_PERSIST_DIRECTORY=./data/chromadb
```

The scripts automatically load environment variables and activate the virtual environment.