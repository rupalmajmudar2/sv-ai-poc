# SportzVillage AI Assistant

A comprehensive AI-powered application for managing school sports programs across multiple stakeholders in the SportzVillage ecosystem.

## ⚡ New: LangGraph-Powered Architecture

**Major Update**: Migrated from LangChain to LangGraph for advanced agent workflows!

### 🚀 Why LangGraph?
- **Human-in-the-Loop**: Built-in approval workflows for critical operations
- **State Management**: Persistent conversation context and workflow tracking
- **Parallel Execution**: Multiple tools can run simultaneously for better performance
- **Robust Error Handling**: Graceful recovery from failures with checkpointing
- **Future-Proof**: Active development with cutting-edge agent capabilities

### 🔄 Continuous Testing Suite
- **Always-Running Tests**: File monitoring with automatic test execution
- **Parallel Testing**: Fast execution with pytest-xdist
- **Coverage Tracking**: HTML reports and real-time coverage feedback
- **Smart Filtering**: Only relevant tests run based on changed files

## Overview

This application serves different roles in the SportzVillage organization:
- **Residents (R)**: Log lesson completions, update prop status, communicate with HO
- **Delivery/Regional Managers (DM/RM)**: Monitor teams, generate reports, oversee multiple schools
- **Head Office (HO)**: System-wide oversight, comprehensive reporting, stakeholder communication
- **School Principals**: View SV activities in their schools, receive regular reports

## Architecture

- **LangGraph Agent**: Modern workflow-based agent with state management and human-in-the-loop capabilities
- **RAG Architecture**: ChromaDB for vector storage + semantic search across all data
- **UI**: Streamlit with role-based interfaces and real-time updates
- **Database**: Abstracted interface (Mock files → MySQL → MCP progression)
- **Testing**: Continuous test suite with file monitoring and parallel execution
- **Agent Factory**: Seamless switching between LangChain/LangGraph backends

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for LLM functionality)

### One-Command Setup & Run

```bash
# Clone and setup everything in one go
git clone <repository-url>
cd sv-ai-poc-v1
python setup.py --run
```

### Manual Setup

1. **Install & Configure**:
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
```

2. **Choose Your Experience**:
```bash
# Regular app
streamlit run main.py

# With continuous testing
python setup.py --watch

# Run tests once
python setup.py --test
```

### Demo Credentials

Try these demo accounts:
- **Resident**: ID: `R001`, Password: `r123`
- **Delivery Manager**: ID: `DM001`, Password: `dm123`
- **Regional Manager**: ID: `RM001`, Password: `rm123`
- **Head Office**: ID: `HO001`, Password: `ho123`
- **Principal**: ID: `P001`, Password: `p123`

## Project Structure

```
sv-ai-poc-v1/
├── src/
│   ├── agents/
│   │   ├── sv_langgraph_agent.py    # New LangGraph-powered agent
│   │   ├── sv_agent.py              # Legacy LangChain agent
│   │   └── agent_factory.py         # Factory for backend selection
│   ├── database/
│   │   ├── interface.py             # Database abstraction layer
│   │   └── vector_store.py          # ChromaDB vector operations
│   └── tools/
│       ├── data_tools.py            # Core business logic tools
│       ├── communication_tools.py   # SMS, reporting tools
│       └── enhanced_tools.py        # RAG-powered semantic tools
├── tests/
│   ├── continuous_runner.py         # Continuous test suite runner
│   └── test_*.py                    # Comprehensive test suite
├── data/
│   ├── mock_data/                   # Mock JSON files for development
│   └── chromadb/                    # Vector database persistence
├── main.py                          # Streamlit application entry point
├── start_tests.py                   # Easy continuous testing launcher
├── pytest.ini                      # Test configuration
└── requirements.txt                 # Comprehensive dependencies
```

## 🔥 Key Features

### Advanced LangGraph Agent
- **StateGraph Workflows**: Complex approval and routing workflows
- **Human Approval Nodes**: Built-in checkpoints for sensitive operations
- **Parallel Tool Execution**: Multiple tools can run simultaneously
- **Memory Persistence**: Conversation state preserved across sessions
- **Error Recovery**: Graceful handling with workflow resumption

### RAG & Vector Database
- **ChromaDB Integration**: Persistent vector storage for semantic search
- **Automatic Indexing**: Timetables, lessons, props automatically cached
- **Semantic Search Tool**: Natural language queries across all data
- **Enhanced Reports**: AI-powered insights with trend analysis
- **Context Caching**: User preferences and behavior patterns stored

### Continuous Testing & Quality
- **File Monitoring**: Automatic test execution on code changes
- **Parallel Execution**: Fast test runs with pytest-xdist
- **Coverage Reports**: HTML coverage reports with detailed metrics
- **Test Classification**: Unit, integration, agent, and smoke tests
- **Smart Debouncing**: Efficient test triggering without spam

### Role-Based Access
- Different UI and functionality based on user role
- Contextual data loading (only relevant school/class/section data)
- Specialized tools per role with LangGraph workflow management

### Data Management
- **Timetables**: Real-time class schedules with PE periods
- **Lesson Plans**: Structured lessons for school sessions with completion tracking
- **Props**: Equipment tracking and status management with approval workflows
- **Events**: Special activities and comprehensive reporting

### Communication & Reporting
- **SMS Integration**: Standardized format messaging to HO with validation
- **Report Generation**: Dynamic weekly/monthly reports with AI insights
- **Multi-stakeholder Updates**: Principal reports, manager dashboards
- **Workflow Approvals**: Human-in-the-loop for critical communications

## Configuration

### Agent Backend Selection
```bash
# .env configuration
AGENT_TYPE=langgraph    # langgraph (recommended) or langchain (legacy)
```

### Database Modes
- `mock`: Uses JSON files in `data/mock_data/` (default for development)
- `mysql`: Connects to MySQL database (future)
- `mcp`: Model Context Protocol integration (future)

### Environment Variables
```bash
# Agent Configuration
AGENT_TYPE=langgraph               # Use LangGraph agent (recommended)
OPENAI_API_KEY=your_key_here      # Required for AI agent and embeddings

# Database Configuration
DB_TYPE=mock                       # mock, mysql, mcp
CHROMA_PERSIST_DIRECTORY=./data/chromadb  # Vector database storage

# Testing Configuration
TESTING=true                       # Enable test mode (set automatically in tests)

# Optional: SMS Configuration
SMS_API_ENDPOINT=https://api.example.com/sms
SMS_API_KEY=your_sms_key
```

## 🧪 Testing & Development

### Continuous Testing
```bash
# Start continuous test suite (recommended for development)
python start_tests.py

# Or use setup script
python setup.py --watch

# Manual continuous runner
python tests/continuous_runner.py --mode continuous
```

### Single Test Runs
```bash
# Quick test run
python setup.py --test

# Full test suite with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Specific test categories
python -m pytest -m "agent"        # Agent tests only
python -m pytest -m "unit"         # Unit tests only
python -m pytest -m "integration"  # Integration tests only
```

### Development Workflow
1. **Start Continuous Tests**: `python start_tests.py`
2. **Develop Features**: Tests run automatically on file changes
3. **Check Coverage**: View HTML reports in `htmlcov/`
4. **Run App**: `streamlit run main.py` in another terminal

### Adding New Features

#### New Tools
1. Create tool class inheriting from `BaseTool`
2. Define input schema with Pydantic
3. Implement `_run` method
4. Add to appropriate role in agent factory
5. Add tests to verify functionality

#### LangGraph Workflows
1. Define new workflow nodes in `sv_langgraph_agent.py`
2. Add state management for complex operations
3. Include human approval nodes for sensitive actions
4. Test workflow state transitions

## 📊 Performance & Quality

### Test Metrics (as of latest run)
- ✅ **4/4 Agent Tests Passing**: All user roles tested
- ✅ **100% Agent Coverage**: LangGraph agents work for all roles
- ✅ **Tool Integration**: All tools verified with new agent
- ⚡ **Fast Execution**: Parallel tests complete in seconds

### Agent Capabilities
- **Zero Hallucination Policy**: Accuracy-first responses with validation
- **Contextual Understanding**: Role-aware interactions with state persistence
- **Tool Orchestration**: Intelligent use of specialized tools with parallel execution
- **Memory Management**: Conversation history and workflow state preserved

### Quality Assurance
- **Continuous Testing**: Always-running test suite catches issues immediately
- **Coverage Tracking**: Comprehensive test coverage with HTML reports
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **Pre-commit Hooks**: Automated quality checks before commits

## 🚀 Critical Requirements

### Accuracy
- No hallucinations allowed in stakeholder communications
- All data validated before presentation with LangGraph checkpoints
- Real-time timetable fetching for current information

### Performance
- Contextual data loading (specific school-class-section only)
- Efficient tool usage with parallel execution
- Memory management for conversation context and workflow state

### Security
- Role-based access control with workflow validation
- Secure credential handling
- Audit trail for critical operations through LangGraph state

### Testing
- Continuous test execution for immediate feedback
- Comprehensive coverage across all user roles and workflows
- Automated quality assurance with pre-commit hooks

## 🔮 Future Enhancements

### Immediate (LangGraph Foundation)
- **Advanced Approval Workflows**: Multi-step approval chains for complex operations
- **Workflow Templates**: Reusable workflow patterns for common tasks
- **State Persistence**: Long-running workflows across sessions
- **Error Recovery**: Automatic retry and human intervention workflows

### Medium Term
- **Real-time Notifications**: WebSocket integration for live updates
- **Mobile Support**: Progressive Web App capabilities
- **Advanced Analytics**: ML-powered insights and predictions
- **Integration APIs**: Third-party school management systems

### Long Term
- **Multi-Agent Coordination**: Multiple specialized agents working together
- **Learning Workflows**: Agents that improve based on user feedback
- **Distributed Execution**: Scale workflows across multiple instances
- **Advanced Human-AI Collaboration**: Sophisticated approval and oversight systems

## 🆘 Support & Troubleshooting

### Common Issues
1. **Tests failing**: Run `python setup.py --test` to see specific errors
2. **Agent not responding**: Check OPENAI_API_KEY in `.env`
3. **Import errors**: Run `pip install -r requirements.txt`
4. **Vector database issues**: Delete `data/chromadb/` to reset

### Development Support
- **Continuous Tests**: Monitor `python start_tests.py` output for real-time feedback
- **Coverage Reports**: Check `htmlcov/index.html` for test coverage details
- **Agent Debugging**: Use `AGENT_TYPE=langchain` for simpler debugging if needed
- **Test Categories**: Run specific test types with `-m` markers

### Getting Help
1. Check the continuous test output for immediate feedback
2. Review test coverage reports for missing functionality
3. Verify environment configuration in `.env`
4. Check role permissions and data access patterns
5. Contact development team for system-level issues

## 📄 License

[Add appropriate license information]