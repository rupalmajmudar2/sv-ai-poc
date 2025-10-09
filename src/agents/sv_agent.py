from langchain.agents import initialize_agent, AgentType
from langchain_openai import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage
from langchain.callbacks.base import BaseCallbackHandler
from typing import List, Dict, Any, Optional
import os
import time
from dotenv import load_dotenv

from ..tools.data_tools import (
    TimetableTool, LessonPlanTool, PropsTool, ResidentsTool,
    LessonCompletionTool, PropUpdateTool
)
from ..tools.communication_tools import SmsSenderTool, ReportGeneratorTool
from ..tools.enhanced_tools import (
    SemanticSearchTool, VectorCacheRefreshTool, EnhancedReportTool
)
from ..database.interface import get_database, UserRole
from ..database.sv_docs import get_sv_document_manager
from ..database.chat_logger import get_chat_logger
from ..utils.llm_analytics import capture_llm_interaction

load_dotenv()


class LLMAnalyticsCallback(BaseCallbackHandler):
    """Callback handler to capture LLM analytics data"""
    
    def __init__(self):
        self.llm_data = None
        self.messages = []
        self.response = ""
        self.model_name = "gpt-3.5-turbo"
        self.temperature = 0.0
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts generating"""
        # Capture the prompt being sent
        if prompts:
            self.prompt_text = prompts[0]
        
        # Extract model info if available
        if "model_name" in kwargs:
            self.model_name = kwargs["model_name"]
        if "temperature" in kwargs:
            self.temperature = kwargs["temperature"]
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes generating"""
        try:
            # Extract response text
            if hasattr(response, 'generations') and response.generations:
                self.response = response.generations[0][0].text
            
            # Create analytics data
            from ..utils.llm_analytics import get_llm_analytics
            analytics = get_llm_analytics()
            
            if hasattr(self, 'prompt_text'):
                prompt_tokens = analytics.count_tokens(self.prompt_text)
                completion_tokens = analytics.count_tokens(self.response)
                
                self.llm_data = {
                    "llm_prompt": self.prompt_text,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "model_used": self.model_name,
                    "temperature": self.temperature,
                    "prompt_length_chars": len(self.prompt_text),
                    "response_length_chars": len(self.response)
                }
        except Exception as e:
            print(f"Error capturing LLM analytics: {e}")
            self.llm_data = None


class SVAgent:
    """Main SportzVillage AI Agent that handles user interactions"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.user_info = self._authenticate_user()
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.session_id = None  # Will be set when first message is sent
        self.chat_logger = get_chat_logger()
        
        # Initialize LLM analytics callback
        self.llm_callback = LLMAnalyticsCallback()
        
        # Initialize LLM
        self.llm = OpenAI(
            temperature=0,  # Low temperature for accuracy
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            callbacks=[self.llm_callback]
        )
        
        # Initialize tools based on user role
        self.tools = self._get_tools_for_role()
        
        # Create agent - Using STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION to support multi-input tools
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=5
        )
        
        # Set system prompt based on role
        self._set_system_prompt()
    
    def _authenticate_user(self) -> Dict[str, Any]:
        """Authenticate user and get user info"""
        db = get_database()
        user = db.get_user(self.user_id)
        
        if not user:
            raise ValueError(f"User {self.user_id} not found")
        
        return user
    
    def _get_tools_for_role(self) -> List:
        """Get appropriate tools based on user role"""
        base_tools = [
            TimetableTool(),
            LessonPlanTool(),
            PropsTool(),
            SemanticSearchTool()  # All users get semantic search
        ]
        
        role = self.user_info["role"]
        
        if role in ["R"]:  # Residents
            base_tools.extend([
                LessonCompletionTool(),
                PropUpdateTool(),
                SmsSenderTool()
            ])
        
        if role in ["DM", "RM"]:  # Delivery Managers, Regional Managers
            base_tools.extend([
                ResidentsTool(),
                ReportGeneratorTool(),
                EnhancedReportTool()  # Smart reports for managers
            ])
        
        if role in ["HO", "RM", "DM"]:  # Management roles
            base_tools.extend([
                ReportGeneratorTool(),
                EnhancedReportTool(),
                VectorCacheRefreshTool()  # Cache management for admins
            ])
        
        return base_tools
    
    def _set_system_prompt(self):
        """Set system prompt based on user role"""
        role = self.user_info["role"]
        name = self.user_info["name"]
        
        base_prompt = f"""
You are an AI assistant for SportzVillage (SV), helping {name} ({role}) with sports program management.

CRITICAL RULES:
1. ACCURACY IS PARAMOUNT - No hallucinations allowed. All information must be factual.
2. Always verify data before providing information to stakeholders.
3. When unsure, ask clarifying questions rather than guessing.
4. Use appropriate tools to fetch real-time data.
5. Be concise but comprehensive in responses.
6. USE SEMANTIC SEARCH for better context when answering questions.
7. Leverage RAG capabilities to provide enriched, contextual responses.

RAG CAPABILITIES:
- Use semantic_search_tool to find relevant information across all cached data
- Enhanced reports provide AI-powered insights and recommendations
- Vector database contains indexed timetables, lessons, props, and documents

Your role: {role}
Your capabilities are enhanced with intelligent search and analysis tools.
"""
        
        if role == "R":
            base_prompt += """
As a Resident, you can:
- View timetables for your assigned school
- Log lesson completions after each class
- Update prop status and usage
- Send standardized SMS updates to SV Head Office
- View lesson plans for your school

Remember to log all activities accurately and report any issues promptly.
"""
        
        elif role in ["DM", "RM"]:
            base_prompt += """
As a Manager, you can:
- View information for schools under your management
- Monitor residents under your supervision  
- Generate reports for SV Head Office
- Track prop inventory across your schools
- Access timetables and lesson plans for oversight

Focus on monitoring performance and ensuring quality delivery.
"""
        
        elif role == "HO":
            base_prompt += """
As Head Office, you have access to:
- All school data and reports
- System-wide analytics and monitoring
- Communication tools for stakeholder updates
- Comprehensive reporting capabilities

Ensure accurate reporting to school principals and maintain system oversight.
"""
        
        elif role == "PRINCIPAL":
            base_prompt += """
As a School Principal, you can:
- View SV activities in your school
- Access reports about resident performance
- Monitor lesson completion and prop usage
- Review sports program progress

You receive regular updates about SV activities in your school.
"""
        
        # Store the prompt for the agent
        self.system_prompt = base_prompt
    
    def chat(self, message: str) -> str:
        """Process user message and return response"""
        start_time = time.time()
        tools_used = []
        
        try:
            # Reset callback data for this interaction
            self.llm_callback.llm_data = None
            
            # Pre-process with semantic search for better context
            school_id = self.user_info.get('school_id')
            doc_manager = get_sv_document_manager()
            
            # Get relevant SV documentation context
            sv_context = doc_manager.get_relevant_documentation(message)
            
            # Add RAG context to the message for better responses
            enhanced_message = f"""
User: {self.user_info['name']} ({self.user_info['role']})
School: {school_id or 'Multiple/Unknown'}
Query: {message}

SV OFFICIAL DOCUMENTATION CONTEXT:
{sv_context if sv_context else 'No specific SV documentation found for this query'}

Context: Use semantic search and available tools to provide accurate, contextual information.
Always reference SV documentation and standards when applicable.
If the query could benefit from semantic search across cached data, use the semantic_search_tool first.

{self.system_prompt}
"""
            
            response = self.agent.run(enhanced_message)
            
            # Validate response for accuracy
            validated_response = self._validate_response(response)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log the interaction with LLM analytics
            if not self.session_id:
                self.session_id = self.chat_logger._generate_session_id()
            
            # Pass LLM analytics data to chat logger
            llm_data = self.llm_callback.llm_data if self.llm_callback.llm_data else None
            
            self.chat_logger.log_interaction(
                user_info=self.user_info,
                message=message,
                response=validated_response,
                tools_used=tools_used,
                response_time=response_time,
                session_id=self.session_id,
                llm_data=llm_data
            )
            
            return validated_response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or contact support."
            
            # Log error interactions too
            response_time = time.time() - start_time
            if not self.session_id:
                self.session_id = self.chat_logger._generate_session_id()
                
            self.chat_logger.log_interaction(
                user_info=self.user_info,
                message=message,
                response=error_response,
                tools_used=["error"],
                response_time=response_time,
                session_id=self.session_id,
                llm_data=None  # No LLM data for errors
            )
            
            return error_response
    
    def _validate_response(self, response: str) -> str:
        """Validate response for accuracy and completeness"""
        
        # Check for common hallucination indicators
        hallucination_keywords = [
            "I believe", "I think", "probably", "might be", "could be",
            "I assume", "typically", "usually", "in general"
        ]
        
        for keyword in hallucination_keywords:
            if keyword.lower() in response.lower():
                return f"I need to verify this information before providing a definitive answer. Let me check the exact data for you. Could you please rephrase your question to be more specific?"
        
        # Add disclaimer for critical information
        if any(word in response.lower() for word in ["report", "status", "completion", "count"]):
            response += "\n\n[Note: This information is based on current data. Please verify critical details before making decisions.]"
        
        return response
    
    def get_user_context(self) -> Dict[str, Any]:
        """Get user context for UI personalization"""
        context = {
            "user_id": self.user_id,
            "name": self.user_info["name"],
            "role": self.user_info["role"],
            "school_id": self.user_info.get("school_id"),
            "reports_to": self.user_info.get("reports_to"),
            "session_id": self.session_id
        }
        
        return context
    
    def get_chat_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent chat history for this user"""
        return self.chat_logger.get_user_chat_history(self.user_id, limit)
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """Get analytics for current session"""
        return self.chat_logger.get_analytics()
    
    def warm_vector_cache(self) -> str:
        """Warm up vector cache for better performance"""
        try:
            # Cache user context
            from ..database.vector_store import get_vector_store
            vector_store = get_vector_store()
            
            if vector_store:
                vector_store.cache_user_context(
                    self.user_id,
                    {
                        "role": self.user_info["role"],
                        "school_id": self.user_info.get("school_id"),
                        "recent_activity": {"login": "success"},
                        "preferences": {"interface": "streamlit"}
                    }
                )
                return "Vector cache warmed successfully"
            else:
                return "Vector cache not available"
                
        except Exception as e:
            return f"Cache warming failed: {str(e)}"