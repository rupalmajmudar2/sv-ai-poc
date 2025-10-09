"""
Chat logging functionality for SportzVillage AI
"""
import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger


class ChatLogger:
    """Logs all user interactions with timestamps and metadata"""
    
    def __init__(self, log_dir: str = "data/chat_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV file for structured logging
        self.csv_file = self.log_dir / "chat_logs.csv"
        self.json_file = self.log_dir / "chat_sessions.json"
        
        # Initialize CSV if it doesn't exist
        if not self.csv_file.exists():
            self._init_csv_log()
    
    def _init_csv_log(self):
        """Initialize CSV log file with headers"""
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'session_id', 'user_id', 'username', 'role', 
                'school_id', 'message', 'response', 'tools_used', 'response_time',
                'llm_prompt', 'prompt_tokens', 'completion_tokens', 'total_tokens',
                'model_used', 'temperature'
            ])
    
    def log_interaction(self, user_info: Dict[str, Any], message: str, 
                       response: str, tools_used: List[str] = None, 
                       response_time: float = None, session_id: str = None,
                       llm_data: Dict[str, Any] = None) -> str:
        """Log a user interaction with optional LLM analytics
        
        Args:
            user_info: User information dictionary
            message: User's original message
            response: AI's response
            tools_used: List of tools used
            response_time: Response time in seconds
            session_id: Session identifier
            llm_data: Dictionary containing:
                - llm_prompt: Complete prompt sent to LLM
                - prompt_tokens: Number of tokens in prompt
                - completion_tokens: Number of tokens in response
                - total_tokens: Total tokens used
                - model_used: Model name
                - temperature: Temperature setting
        """
        
        timestamp = datetime.now().isoformat()
        session_id = session_id or self._generate_session_id()
        
        # Extract LLM data if provided
        llm_prompt = ""
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        model_used = ""
        temperature = 0.0
        
        if llm_data:
            llm_prompt = llm_data.get('llm_prompt', '')
            prompt_tokens = llm_data.get('prompt_tokens', 0)
            completion_tokens = llm_data.get('completion_tokens', 0)
            total_tokens = llm_data.get('total_tokens', 0)
            model_used = llm_data.get('model_used', '')
            temperature = llm_data.get('temperature', 0.0)
        
        # Log to CSV
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                session_id,
                user_info.get('user_id', ''),
                user_info.get('name', ''),
                user_info.get('role', ''),
                user_info.get('school_id', ''),
                message,
                response,
                json.dumps(tools_used or []),
                response_time or 0,
                llm_prompt,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                model_used,
                temperature
            ])
        
        # Log to JSON for more detailed analysis
        self._log_to_json(timestamp, session_id, user_info, message, response, tools_used, response_time, {
            'llm_prompt': llm_prompt,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'model_used': model_used,
            'temperature': temperature
        })
        
        logger.info(f"Chat interaction logged: {user_info.get('user_id')} - {len(message)} chars")
        return session_id
    
    def _log_to_json(self, timestamp: str, session_id: str, user_info: Dict[str, Any], 
                     message: str, response: str, tools_used: List[str], response_time: float,
                     llm_analytics: Dict[str, Any] = None):
        """Log detailed interaction to JSON with LLM analytics"""
        
        interaction = {
            "timestamp": timestamp,
            "session_id": session_id,
            "user": {
                "user_id": user_info.get('user_id'),
                "name": user_info.get('name'),
                "role": user_info.get('role'),
                "school_id": user_info.get('school_id')
            },
            "interaction": {
                "message": message,
                "message_length": len(message),
                "response": response,
                "response_length": len(response),
                "tools_used": tools_used or [],
                "response_time_seconds": response_time
            },
            "llm_analytics": llm_analytics or {
                "llm_prompt": "",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "model_used": "",
                "temperature": 0.0
            },
            "metadata": {
                "message_type": self._classify_message(message),
                "contains_school_data": "school" in message.lower(),
                "contains_resident_data": "resident" in message.lower(),
                "is_question": message.strip().endswith('?')
            }
        }
        
        # Append to JSON file
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"interactions": []}
            
            data["interactions"].append(interaction)
            
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to log to JSON: {e}")
    
    def _classify_message(self, message: str) -> str:
        """Classify the type of message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['report', 'generate', 'show me']):
            return "request"
        elif message_lower.strip().endswith('?'):
            return "question"
        elif any(word in message_lower for word in ['update', 'log', 'complete']):
            return "action"
        elif any(word in message_lower for word in ['help', 'how', 'what']):
            return "help"
        else:
            return "general"
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_user_chat_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a specific user"""
        try:
            if not self.json_file.exists():
                return []
            
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_interactions = [
                interaction for interaction in data.get("interactions", [])
                if interaction["user"]["user_id"] == user_id
            ]
            
            # Sort by timestamp (newest first) and limit
            user_interactions.sort(key=lambda x: x["timestamp"], reverse=True)
            return user_interactions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get user chat history: {e}")
            return []
    
    def get_all_chat_logs(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get all chat logs with optional date filtering"""
        try:
            if not self.json_file.exists():
                return []
            
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            interactions = data.get("interactions", [])
            
            # Filter by date if provided
            if start_date or end_date:
                filtered = []
                for interaction in interactions:
                    timestamp = interaction["timestamp"]
                    if start_date and timestamp < start_date:
                        continue
                    if end_date and timestamp > end_date:
                        continue
                    filtered.append(interaction)
                interactions = filtered
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get chat logs: {e}")
            return []
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get chat analytics"""
        try:
            logs = self.get_all_chat_logs()
            
            if not logs:
                return {"total_interactions": 0}
            
            # Basic analytics
            total_interactions = len(logs)
            unique_users = len(set(log["user"]["user_id"] for log in logs))
            
            # Message type distribution
            message_types = {}
            roles = {}
            schools = {}
            
            # LLM Analytics
            total_prompt_tokens = 0
            total_completion_tokens = 0
            total_tokens_used = 0
            models_used = {}
            temperature_stats = []
            
            for log in logs:
                msg_type = log["metadata"]["message_type"]
                message_types[msg_type] = message_types.get(msg_type, 0) + 1
                
                role = log["user"]["role"]
                roles[role] = roles.get(role, 0) + 1
                
                school = log["user"]["school_id"]
                if school:
                    schools[school] = schools.get(school, 0) + 1
                
                # Extract LLM analytics
                llm_data = log.get("llm_analytics", {})
                if llm_data:
                    total_prompt_tokens += llm_data.get("prompt_tokens", 0)
                    total_completion_tokens += llm_data.get("completion_tokens", 0)
                    total_tokens_used += llm_data.get("total_tokens", 0)
                    
                    model = llm_data.get("model_used", "unknown")
                    if model:
                        models_used[model] = models_used.get(model, 0) + 1
                    
                    temp = llm_data.get("temperature", 0)
                    if temp > 0:
                        temperature_stats.append(temp)
            
            # Calculate token costs (approximate, using OpenAI pricing)
            # GPT-4: $0.03/1K prompt tokens, $0.06/1K completion tokens
            # GPT-3.5-turbo: $0.0015/1K prompt tokens, $0.002/1K completion tokens
            estimated_cost_gpt4 = (total_prompt_tokens * 0.03/1000) + (total_completion_tokens * 0.06/1000)
            estimated_cost_gpt35 = (total_prompt_tokens * 0.0015/1000) + (total_completion_tokens * 0.002/1000)
            
            # Average temperature
            avg_temperature = sum(temperature_stats) / len(temperature_stats) if temperature_stats else 0
            
            return {
                "total_interactions": total_interactions,
                "unique_users": unique_users,
                "message_types": message_types,
                "roles": roles,
                "schools": schools,
                "llm_analytics": {
                    "total_prompt_tokens": total_prompt_tokens,
                    "total_completion_tokens": total_completion_tokens,
                    "total_tokens_used": total_tokens_used,
                    "models_used": models_used,
                    "average_temperature": round(avg_temperature, 2),
                    "estimated_costs": {
                        "gpt4_estimate": round(estimated_cost_gpt4, 4),
                        "gpt35_estimate": round(estimated_cost_gpt35, 4)
                    },
                    "tokens_per_interaction": round(total_tokens_used / total_interactions, 1) if total_interactions > 0 else 0
                },
                "date_range": {
                    "earliest": min(log["timestamp"] for log in logs),
                    "latest": max(log["timestamp"] for log in logs)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {"error": str(e)}


# Global chat logger instance
_chat_logger = None

def get_chat_logger() -> ChatLogger:
    """Get global chat logger instance"""
    global _chat_logger
    if _chat_logger is None:
        _chat_logger = ChatLogger()
    return _chat_logger