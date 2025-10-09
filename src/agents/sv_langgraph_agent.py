"""
SportzVillage LangGraph Agent
Modern replacement for the LangChain agent using LangGraph for better workflow control,
human-in-the-loop capabilities, and state management.
"""

from typing import Dict, List, Any, Optional, Annotated
from typing_extensions import TypedDict
import os
import logging
from dotenv import load_dotenv

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler

# SportzVillage imports
from ..tools.data_tools import (
    TimetableTool, LessonPlanTool, PropsTool, ResidentsTool,
    LessonCompletionTool, PropUpdateTool
)
from ..tools.communication_tools import SmsSenderTool, ReportGeneratorTool
from ..tools.enhanced_tools import (
    SemanticSearchTool, VectorCacheRefreshTool, EnhancedReportTool
)
from ..database.interface import get_database, UserRole
from ..database.chat_logger import get_chat_logger
from ..utils.llm_analytics import capture_llm_interaction

# Debug logging helper
DEBUG_MODE = os.getenv("SV_DEBUG_MODE", "false").lower() == "true"
logger = logging.getLogger(__name__)

def debug_print(message: str):
    """Print debug messages only if DEBUG_MODE is enabled"""
    if DEBUG_MODE:
        print(message)
    else:
        logger.debug(message)

load_dotenv()


class LangGraphLLMCallback(BaseCallbackHandler):
    """Callback to capture LLM interactions in LangGraph"""
    
    def __init__(self):
        super().__init__()
        self.llm_data = None
        self.current_messages = []
        self.response_text = ""
        # LangGraph LLM Callback initialized
    
    def on_chat_model_start(self, serialized, messages, **kwargs):
        """Capture the messages being sent to the chat model"""
        debug_print(f"[CALLBACK] Chat model start - {len(messages)} messages")
        self.current_messages = messages
        self.llm_data = None
        self.response_text = ""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Alternative callback method for LLM start"""
        debug_print(f"[CALLBACK] LLM start - {len(prompts)} prompts")
        if prompts:
            self.current_prompt = prompts[0]
    
    def on_chat_model_end(self, response, **kwargs):
        """Capture the response from the chat model"""
        debug_print(f"[CALLBACK] Chat model end - response type: {type(response)}")
        try:
            if hasattr(response, 'content'):
                self.response_text = str(response.content)
            elif hasattr(response, 'generations') and response.generations:
                self.response_text = str(response.generations[0][0].message.content)
            
            debug_print(f"[CALLBACK] Response captured: {len(self.response_text)} chars")
            
            # Create analytics data
            if self.current_messages and self.response_text:
                from ..utils.llm_analytics import capture_llm_interaction
                self.llm_data = capture_llm_interaction(
                    messages=self.current_messages,
                    response=self.response_text,
                    model_name="gpt-3.5-turbo",
                    temperature=0.0
                )
                debug_print(f"[CALLBACK] LLM analytics created: {self.llm_data is not None}")
        except Exception as e:
            debug_print(f"[CALLBACK] Error capturing LLM analytics: {e}")
            self.llm_data = None
    
    def on_llm_end(self, response, **kwargs):
        """Alternative callback method for LLM end"""
        debug_print(f"[CALLBACK] LLM end - response type: {type(response)}")
        self.on_chat_model_end(response, **kwargs)


class SVAgentState(TypedDict):
    """State schema for SportzVillage LangGraph agent"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    user_info: Dict[str, Any]
    tools_available: List[str]
    current_workflow: Optional[str]
    pending_approval: Optional[Dict[str, Any]]
    session_id: Optional[str]
    context: Dict[str, Any]


class SVLangGraphAgent:
    """SportzVillage LangGraph Agent with workflow support and human-in-the-loop capabilities"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_info = self._authenticate_user()
        self.chat_logger = get_chat_logger()
        
        # Initialize LLM analytics callback
        self.llm_callback = LangGraphLLMCallback()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            callbacks=[self.llm_callback]
        )
        
        # Get role-specific tools
        self.tools = self._get_tools_for_role()
        self.tool_node = ToolNode(self.tools)
        
        # Create the graph
        self.graph = self._create_graph()
        
        # Memory for state persistence
        self.memory = MemorySaver()
        
        # Compile the graph with checkpointer for human-in-the-loop
        self.app = self.graph.compile(checkpointer=self.memory)
        
    def _authenticate_user(self) -> Dict[str, Any]:
        """Authenticate user and get user info"""
        db = get_database()
        user = db.get_user(self.user_id)
        
        if not user:
            raise ValueError(f"User {self.user_id} not found")
        
        return user
    
    def _get_tools_for_role(self) -> List[BaseTool]:
        """Get appropriate tools based on user role"""
        base_tools = [
            TimetableTool(),
            LessonPlanTool(),
            PropsTool(),
            SemanticSearchTool()  # All users get semantic search
        ]
        
        role = self.user_info['role']
        
        if role == UserRole.R.value:
            # Residents can update information and send messages
            base_tools.extend([
                LessonCompletionTool(),
                PropUpdateTool(),
                SmsSenderTool()
            ])
        
        elif role in [UserRole.DM.value, UserRole.RM.value]:
            # Managers can view residents and generate reports
            base_tools.extend([
                ResidentsTool(),
                ReportGeneratorTool(),
                EnhancedReportTool(),
                ReportGeneratorTool(),  # Additional reporting capabilities
                EnhancedReportTool(),
                VectorCacheRefreshTool()
            ])
        
        elif role == UserRole.HO.value:
            # HO gets all tools
            base_tools.extend([
                ReportGeneratorTool(),
                EnhancedReportTool(),
                VectorCacheRefreshTool()
            ])
        
        # Principals get read-only access (base tools only)
        
        return base_tools
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(SVAgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self.tool_node)
        workflow.add_node("human_approval", self._human_approval_node)
        workflow.add_node("supervisor_check", self._supervisor_check_node)
        
        # Add edges
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
                "approval_needed": "human_approval",
                "supervisor_check": "supervisor_check"
            }
        )
        workflow.add_edge("tools", "agent")
        workflow.add_edge("human_approval", "agent")
        workflow.add_edge("supervisor_check", "agent")
        
        return workflow
    
    def _agent_node(self, state: SVAgentState) -> SVAgentState:
        """Main agent reasoning node"""
        debug_print("[AGENT_NODE] Starting agent node")
        debug_print(f"[AGENT_NODE] User info: {state['user_info']}")
        debug_print(f"[AGENT_NODE] Input messages: {[msg.content[:100] + '...' if len(msg.content) > 100 else msg.content for msg in state['messages']]}")
        
        # Bind tools to the model
        model_with_tools = self.llm.bind_tools(self.tools)
        
        # Add system message with role context
        system_message = self._get_system_message(state["user_info"])
        messages = [system_message] + state["messages"]
        
        debug_print(f"[AGENT_NODE] Total messages to send: {len(messages)}")
        debug_print(f"[AGENT_NODE] System message: {system_message.content[:200]}...")
        for i, msg in enumerate(messages):
            debug_print(f"[AGENT_NODE] Message {i}: {type(msg).__name__} - {msg.content[:100]}...")
        
        # Capture the exact messages being sent
        try:
            from ..utils.llm_analytics import capture_llm_interaction
            from datetime import datetime
            
            debug_print("[AGENT_NODE] About to invoke LLM...")
            
            # Get response from LLM
            response = model_with_tools.invoke(messages)
            
            debug_print(f"[AGENT_NODE] Got response type: {type(response)}")
            debug_print(f"[AGENT_NODE] Response content: {response.content[:200]}...")
            
            # Check for usage metadata
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                debug_print(f"[AGENT_NODE] Usage metadata: {response.usage_metadata}")
                
                # Create comprehensive analytics data with usage metadata
                analytics_data = capture_llm_interaction(
                    messages=messages,
                    response=response,
                    model_name="gpt-3.5-turbo",
                    temperature=0.0,
                    usage_metadata=response.usage_metadata
                )
            else:
                print("[AGENT_NODE] No usage metadata, creating manual analytics")
                # Create manual analytics data
                analytics_data = capture_llm_interaction(
                    messages=messages,
                    response=response,
                    model_name="gpt-3.5-turbo",
                    temperature=0.0
                )
            
            # Store analytics in callback for retrieval
            self.llm_callback.llm_data = analytics_data
            
            print(f"[AGENT_NODE] Analytics captured: {analytics_data is not None}")
            if analytics_data:
                print(f"[AGENT_NODE] Total tokens: {analytics_data.get('total_tokens', 0)}")
                print(f"[AGENT_NODE] Prompt length: {len(analytics_data.get('llm_prompt', ''))}")
        
        except Exception as e:
            print(f"[AGENT_NODE] Error capturing analytics: {e}")
            import traceback
            traceback.print_exc()
            response = model_with_tools.invoke(messages)
            self.llm_callback.llm_data = None
        
        # Update state
        return {
            **state,
            "messages": [response]
        }
    
    def _human_approval_node(self, state: SVAgentState) -> SVAgentState:
        """Handle human-in-the-loop approval workflows"""
        # For now, auto-approve. In future, this can integrate with UI
        # This is where you'd implement actual human approval logic
        
        if state.get("pending_approval"):
            # Log the approval request
            approval_data = state["pending_approval"]
            print(f"[APPROVAL NEEDED] {approval_data}")
            
            # For demo purposes, auto-approve
            # In production, this would wait for human input
            approval_message = AIMessage(
                content=f"Approval granted for: {approval_data.get('action', 'unknown action')}"
            )
            
            return {
                **state,
                "messages": [approval_message],
                "pending_approval": None
            }
        
        return state
    
    def _supervisor_check_node(self, state: SVAgentState) -> SVAgentState:
        """Check if action needs supervisor approval based on role hierarchy"""
        user_role = state["user_info"]["role"]
        
        # Define actions that need supervisor approval
        sensitive_actions = ["send_sms", "generate_report", "update_props"]
        
        last_message = state["messages"][-1] if state["messages"] else None
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                if any(action in tool_call['name'] for action in sensitive_actions):
                    if user_role == UserRole.RESIDENT.value:
                        # Residents need DM approval for certain actions
                        state["pending_approval"] = {
                            "action": tool_call['name'],
                            "requires_role": "DM",
                            "user_id": state["user_id"]
                        }
                        break
        
        return state
    
    def _should_continue(self, state: SVAgentState) -> str:
        """Decide next step in the workflow"""
        last_message = state["messages"][-1] if state["messages"] else None
        
        # Check if we need human approval
        if state.get("pending_approval"):
            return "approval_needed"
        
        # Check for tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            # Check if supervisor approval needed
            if self._needs_supervisor_approval(last_message, state):
                return "supervisor_check"
            return "continue"
        
        return "end"
    
    def _needs_supervisor_approval(self, message: BaseMessage, state: SVAgentState) -> bool:
        """Check if the action needs supervisor approval"""
        user_role = state["user_info"]["role"]
        
        # Only residents need supervisor approval for now
        if user_role != UserRole.R.value:
            return False
        
        # Check for sensitive operations
        if hasattr(message, 'tool_calls') and message.tool_calls:
            sensitive_tools = ["sms_sender_tool", "prop_update_tool"]
            for tool_call in message.tool_calls:
                if tool_call['name'] in sensitive_tools:
                    return True
        
        return False
    
    def _get_system_message(self, user_info: Dict[str, Any]) -> BaseMessage:
        """Get role-specific system message"""
        role = user_info['role']
        name = user_info['name']
        
        system_content = f"""You are the SportzVillage AI Assistant helping {name} ({role}).

SportzVillage manages school sports programs with this hierarchy:
- Head Office (HO) → Regional Manager (RM) → Delivery Manager (DM) → Residents (R)
- School Principals (PRINCIPAL) receive reports

Your role-specific capabilities:"""

        if role == UserRole.HO.value:
            system_content += """
- System-wide oversight and reporting
- Access to all schools and data
- Generate executive reports and analytics"""
        
        elif role == UserRole.RM.value:
            system_content += """
- Manage multiple Delivery Managers
- Regional reporting and analytics
- Oversee resident performance"""
        
        elif role == UserRole.DM.value:
            system_content += """
- Manage residents in assigned schools
- Generate operational reports
- Monitor daily activities"""
        
        elif role == UserRole.R.value:
            system_content += """
- Log lesson completions and activities
- Update props and equipment status
- Request assistance and send updates"""
        
        elif role == UserRole.PRINCIPAL.value:
            system_content += """
- View school overview and reports
- Monitor sports program activities
- Read-only access to school data"""

        system_content += """

CRITICAL: Always provide accurate, helpful information. Never hallucinate data.
Use semantic search when you need to find specific information.
Be concise but comprehensive in your responses."""

        return SystemMessage(content=system_content)
    
    def chat(self, message: str, session_id: Optional[str] = None) -> str:
        """Main chat interface - maintains compatibility with existing code"""
        try:
            # Create session ID if not provided
            if not session_id:
                import time
                session_id = f"session_{int(time.time())}"
            
            # Reset callback data for this interaction
            self.llm_callback.llm_data = None
            
            # Create initial state
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "user_id": self.user_id,
                "user_info": self.user_info,
                "tools_available": [tool.name for tool in self.tools],
                "current_workflow": None,
                "pending_approval": None,
                "session_id": session_id,
                "context": {}
            }
            
            # Configure for this session
            config = {"configurable": {"thread_id": session_id}}
            
            # Run the graph
            result = self.app.invoke(initial_state, config=config)
            
            # Extract response
            last_message = result["messages"][-1]
            response = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Log the interaction with LLM analytics
            try:
                # Get LLM analytics data from callback
                llm_data = self.llm_callback.llm_data if self.llm_callback.llm_data else None
                print(f"[CHAT] LLM data captured: {llm_data is not None}")
                if llm_data:
                    print(f"[CHAT] Tokens: {llm_data.get('total_tokens', 0)}")
                
                self.chat_logger.log_interaction(
                    user_info=self.user_info,
                    message=message,
                    response=response,
                    tools_used=[tool.name for tool in self.tools],
                    response_time=0.0,  # TODO: Add timing
                    session_id=session_id,
                    llm_data=llm_data
                )
                print(f"[CHAT] Interaction logged successfully")
            except Exception as e:
                print(f"Failed to log interaction: {e}")
            
            return response
            
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try again or contact support."
            print(f"Agent error: {e}")
            return error_msg
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get current user context"""
        return self.user_info
    
    def get_chat_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for the user"""
        try:
            return self.chat_logger.get_user_chat_history(self.user_id, limit=limit)
        except Exception as e:
            print(f"Failed to get chat history: {e}")
            return []
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get session analytics"""
        try:
            return self.chat_logger.get_analytics()
        except Exception as e:
            print(f"Failed to get analytics: {e}")
            return {"error": str(e)}
    
    def clear_memory(self):
        """Clear conversation memory - for compatibility"""
        # In LangGraph, memory is managed by checkpointer
        # This method exists for compatibility with existing code
        pass