"""
Agent Factory for SportzVillage
Provides a consistent interface for creating agents with different backends
"""

import os
from typing import Union
from .sv_agent import SVAgent
from .sv_langgraph_agent import SVLangGraphAgent


def create_agent(user_id: str, use_langgraph: bool = True) -> Union[SVAgent, SVLangGraphAgent]:
    """
    Create an agent instance with the specified backend
    
    Args:
        user_id: User ID for authentication
        use_langgraph: If True, use LangGraph agent. If False, use traditional LangChain agent
    
    Returns:
        Agent instance with consistent interface
    """
    
    # Check environment variable for agent type preference
    agent_type = os.getenv("AGENT_TYPE", "langgraph" if use_langgraph else "langchain")
    
    if agent_type.lower() == "langgraph":
        print(f"[AGENT] Creating LangGraph agent for user {user_id}")
        return SVLangGraphAgent(user_id)
    else:
        print(f"[AGENT] Creating LangChain agent for user {user_id}")
        return SVAgent(user_id)


# For backward compatibility
def get_agent(user_id: str) -> Union[SVAgent, SVLangGraphAgent]:
    """Legacy function name for compatibility"""
    return create_agent(user_id, use_langgraph=True)