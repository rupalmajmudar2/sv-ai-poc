#!/usr/bin/env python3
"""
Test Agent Initialization and Tool Loading
Tests that the SVAgent can be properly initialized with all tools
"""

import sys
import os
from pathlib import Path
import tempfile

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def test_agent_initialization():
    """Test that SVAgent initializes correctly with all tools"""
    print("[TEST] Testing Agent Initialization")
    
    # Set up test environment
    os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-testing'
    os.environ['DB_TYPE'] = 'text'
    os.environ['ANONYMIZED_TELEMETRY'] = 'False'
    
    try:
        from src.agents.agent_factory import create_agent
        from src.database.text_db import TextDatabase
        
        # Initialize database first
        db = TextDatabase()
        print("[OK] Database initialized successfully")
        
        # Test agent initialization with different roles
        test_users = [
            {'user_id': 'HO001', 'name': 'Head Office User', 'role': 'HO'},
            {'user_id': 'RM001', 'name': 'Regional Manager 1', 'role': 'RM'},
            {'user_id': 'DM001', 'name': 'Delivery Manager 1', 'role': 'DM'},
            {'user_id': 'R001', 'name': 'Resident 1', 'role': 'R'},
            {'user_id': 'P001', 'name': 'Principal 1', 'role': 'PRINCIPAL'},
        ]
        
        for user_info in test_users:
            try:
                # Create agent using factory (will use LangGraph by default)
                agent = create_agent(user_id=user_info['user_id'])
                print(f"[OK] Agent initialized for role {user_info['role']} with {len(agent.tools)} tools")
                
                # Test that tools are loaded
                tool_names = [tool.name for tool in agent.tools]
                assert len(tool_names) > 0, f"No tools loaded for role {user_info['role']}"
                print(f"[INFO] Available tools for {user_info['role']}: {tool_names}")
                
            except Exception as e:
                print(f"[FAIL] Agent initialization failed for role {user_info['role']}: {e}")
                assert False, f"Agent initialization failed for role {user_info['role']}: {e}"
        
        print("[OK] All agent role initializations successful!")
        assert True
        
    except Exception as e:
        print(f"[FAIL] Agent initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Agent initialization test failed: {e}"


def test_agent_chat_functionality():
    """Test basic chat functionality without requiring real OpenAI API"""
    print("[TEST] Testing Agent Chat Functionality")
    
    try:
        from src.agents.agent_factory import create_agent
        from src.database.text_db import TextDatabase
        
        # Initialize with test user
        db = TextDatabase()
        test_user_id = "HO001"  # Use existing user from mock data
        agent = create_agent(user_id=test_user_id)
        
        # Test that agent has required components
        assert hasattr(agent, 'memory'), "Agent should have memory component"
        assert hasattr(agent, 'tools'), "Agent should have tools"
        assert hasattr(agent, 'chat_logger'), "Agent should have chat logger"
        
        print("[OK] Agent has all required components")
        
        # Test get_user_context
        context = agent.get_user_context()
        assert context['user_id'] == 'HO001', "User context should match initialization"
        assert context['role'] == 'HO', "Role should match initialization"
        
        print("[OK] Agent user context working correctly")
        
        # Test tool access by role
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = ['timetable_tool', 'lesson_plan_tool', 'props_tool']  # Basic tools all roles should have
        
        for expected_tool in expected_tools:
            assert any(expected_tool in name for name in tool_names), f"Expected tool {expected_tool} not found"
        
        print("[OK] Required tools are available")
        
        assert True
        
    except Exception as e:
        print(f"[FAIL] Agent chat functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Agent chat functionality test failed: {e}"


def test_tool_pydantic_compatibility():
    """Test that all tools work with Pydantic v2"""
    print("[TEST] Testing Tool Pydantic v2 Compatibility")
    
    try:
        from src.tools.data_tools import TimetableTool, LessonPlanTool, PropsTool
        from src.tools.communication_tools import SmsSenderTool, ReportGeneratorTool
        
        # Test that tools can be instantiated
        tools_to_test = [
            TimetableTool(),
            LessonPlanTool(),
            PropsTool(),
            SmsSenderTool(),
            ReportGeneratorTool()
        ]
        
        for tool in tools_to_test:
            # Test that tool has required attributes
            assert hasattr(tool, 'name'), f"Tool {type(tool).__name__} missing name"
            assert hasattr(tool, 'description'), f"Tool {type(tool).__name__} missing description"
            assert hasattr(tool, 'args_schema'), f"Tool {type(tool).__name__} missing args_schema"
            
            # Test that args_schema is a Pydantic model
            import pydantic
            assert issubclass(tool.args_schema, pydantic.BaseModel), f"Tool {type(tool).__name__} args_schema not a BaseModel"
            
            print(f"[OK] Tool {tool.name} is Pydantic v2 compatible")
        
        print("[OK] All tools are Pydantic v2 compatible!")
        assert True
        
    except Exception as e:
        print(f"[FAIL] Tool Pydantic compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Tool Pydantic compatibility test failed: {e}"


def test_langchain_imports():
    """Test that all LangChain imports are using non-deprecated versions"""
    print("[TEST] Testing LangChain Import Compatibility")
    
    try:
        # Test new imports work
        from langchain_openai import OpenAI
        from langchain.agents import create_structured_chat_agent, AgentExecutor
        from langchain_core.tools import BaseTool
        from langchain_core.chat_history import InMemoryChatMessageHistory
        from langchain_core.messages import HumanMessage, AIMessage
        
        print("[OK] All LangChain imports successful")
        
        # Test that we can create basic components
        llm = OpenAI(api_key="dummy-key", temperature=0)
        # Use modern chat history instead of deprecated memory
        chat_history = InMemoryChatMessageHistory()
        chat_history.add_message(HumanMessage(content="test"))
        chat_history.add_message(AIMessage(content="response"))
        
        print("[OK] LangChain components can be instantiated")
        assert len(chat_history.messages) == 2
        
    except Exception as e:
        print(f"[FAIL] LangChain import test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"LangChain import test failed: {e}"


if __name__ == "__main__":
    print("[TEST] SportzVillage Agent Initialization Test Suite\n")
    
    # Run tests
    tests = [
        test_langchain_imports,
        test_tool_pydantic_compatibility,
        test_agent_initialization,
        test_agent_chat_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{'='*50}")
        if test():
            passed += 1
        print(f"{'='*50}")
    
    print(f"\n[RESULT] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All agent tests passed!")
        sys.exit(0)
    else:
        print("[FAILED] Some agent tests failed!")
        sys.exit(1)