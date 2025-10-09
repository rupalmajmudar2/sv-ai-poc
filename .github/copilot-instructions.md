# Copilot Instructions for sv-ai-poc-v1

## Project Overview
SportzVillage (SV) AI LLM application for managing school sports programs across multiple stakeholders in an educational environment.

## Domain Context
**Organizational Hierarchy:**
- SV HeadOffice (HO) → Regional Manager (RM) → Delivery Lead/Manager (DL/DM) → Residents (R)
- Each school has 1-2 Residents allocated, managed by a School Principal
- Each school has unique ChannelId (ChId)

**Key Entities:**
- **Timetables**: Class schedules (Nursery-XII, multiple sections) with 1-10 periods (8am-5pm)
- **LessonPlans (LP)**: Define lessons (L) to be completed during school sessions
- **Events**: Special activities (e.g., Annual Day Practice)
- **Props**: Physical equipment (balls, nets) required for classes

## Architecture Implementation
**Current Stack:**
- **RAG Architecture**: ChromaDB vector database + LangChain + OpenAI embeddings
- **UI**: Streamlit with role-based interfaces (`main.py`)
- **Database**: Clean abstraction layer (`src/database/interface.py`)
- **Vector Store**: Semantic search and caching (`src/database/vector_store.py`)
- **Agent Pattern**: Central agent (`src/agents/sv_agent.py`) with RAG-enhanced tools

**Project Structure:**
```
src/
├── agents/sv_agent.py          # Main AI agent with RAG capabilities
├── database/
│   ├── interface.py           # Database abstraction (mock → MySQL → MCP)
│   └── vector_store.py        # ChromaDB vector database service
├── tools/
│   ├── data_tools.py          # Basic timetable, lesson, props tools
│   ├── communication_tools.py  # SMS, reporting tools
│   └── enhanced_tools.py      # RAG-powered semantic search & smart reports
data/
├── mock_data/                 # JSON files for development
└── chromadb/                  # Vector database persistence
main.py                        # Streamlit application entry point
```

## Critical Requirements
⚠️ **Zero Hallucinations**: All information must be accurate - critique answers before providing to stakeholders
⚠️ **Contextual Data Loading**: Only load specific school-class-section data, not entire tables (thousands of schools)
⚠️ **Real-time Timetables**: Fetch latest versions as schedules change frequently

## Database Schema & Implementation
**Current**: Mock JSON files in `data/mock_data/`
**Future**: MySQL → MCP progression

```python
# Key tables
Users: id, password, role, name, school_id, reports_to
Timetables: school_id, class, section, period_number, time_slot, subject, is_pe_period
LessonPlans: id, school_id, session, lessons[]
Lessons: id, name, description, duration, required_props[]
Props: id, type, school_id, quantity, available, status
Events: school_id, date, type, description
```

## Development Patterns

### RAG & Vector Database Integration
- `VectorStoreService` handles ChromaDB operations and semantic search
- Automatic data indexing: timetables, lessons, props cached as embeddings
- `SemanticSearchTool` enables natural language queries across all data
- Enhanced reports with AI insights via `EnhancedReportTool`

### Agent-Tool Architecture
- `SVAgent` class orchestrates tools with RAG preprocessing
- Tools inherit from `BaseTool` with Pydantic schemas
- Role-based tool access in `_get_tools_for_role()`
- Vector search integration for contextual responses

### Database Abstraction
```python
# Factory pattern for database switching
def get_database() -> DatabaseInterface:
    db_type = os.getenv("DB_TYPE", "mock")
    if db_type == "mock":
        return MockDatabase()
    elif db_type == "mysql":
        return MySQLDatabase(...)
```

### Role-Based UI
- `main.py` contains separate interfaces per role
- `resident_interface()`, `manager_interface()`, etc.
- Tab-based organization: Info Update, Ask Questions, Reports, Chat

### Tool Development Pattern
```python
class NewTool(BaseTool):
    name = "tool_name"
    description = "What this tool does"
    args_schema = InputSchema  # Pydantic model
    
    def _run(self, **kwargs) -> str:
        db = get_database()
        # Tool logic here
        return result_string
```

## User Workflows by Role
**Residents (R):**
- Log lesson completion: `LessonCompletionTool`
- Update prop status: `PropUpdateTool`
- Send SMS to HO: `SmsSenderTool`

**DM/RM:**
- Monitor residents: `ResidentsTool`
- Generate reports: `ReportGeneratorTool`
- Track multiple schools: All data tools

**School Principal:**
- Receive SV reports: `ReportGeneratorTool`
- Monitor activities: Read-only access to school data

**SV HeadOffice:**
- System-wide oversight: All tools available
- Stakeholder communication: Advanced reporting

## Critical Implementation Details

### Accuracy Validation
```python
def _validate_response(self, response: str) -> str:
    # Check for hallucination indicators
    hallucination_keywords = ["I believe", "I think", "probably"]
    # Add disclaimers for critical info
    # Return validated response
```

### Context Management
- Tools filter by `school_id`, `class`, `section`
- Agent stores user context in `self.user_info`
- Database methods accept filtering parameters

### SMS Integration
- Standardized formats: `[SV-LC] school|class-section|period|lesson|resident|date`
- Tool handles API integration with fallback simulation
- Format validation before sending

## Development Commands
```bash
# Setup
python setup.py          # Install deps, create .env
python test_setup.py     # Verify installation

# Run
streamlit run main.py    # Start application
python setup.py --run    # Setup + run

# Test
python test_setup.py     # Run test suite
```

## Environment Configuration
```bash
# .env file (copy from .env.example)
DB_TYPE=mock                    # mock, mysql, mcp
OPENAI_API_KEY=your_key        # Required for agent
SMS_API_ENDPOINT=...           # For SMS functionality
```

## Key Files to Understand
- `main.py`: Role-based Streamlit UI with authentication
- `src/agents/sv_agent.py`: Main agent with role-aware tool selection
- `src/database/interface.py`: Database abstraction with mock implementation
- `src/tools/data_tools.py`: Core business logic tools
- `data/mock_data/*.json`: Sample data structure (auto-generated)

## Common Patterns
- **Error Handling**: All tools return user-friendly strings, never raise exceptions to UI
- **Data Filtering**: Always filter by school/class/section to avoid loading massive datasets
- **Role Validation**: Agent checks user role before tool execution
- **State Management**: Streamlit session state for authentication and chat history