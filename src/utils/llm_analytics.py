"""
LLM Analytics Utilities for SportzVillage AI
Captures detailed LLM interaction data for analytics
"""

import tiktoken
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage
import json
from datetime import datetime


class LLMAnalyticsCapture:
    """Utility to capture LLM analytics data"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except:
            # Fallback to cl100k_base encoding for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text) -> int:
        """Count tokens in text using tiktoken"""
        try:
            # Handle different input types
            if hasattr(text, 'content'):
                # It's a message object
                text_content = text.content
            elif isinstance(text, str):
                text_content = text
            else:
                text_content = str(text)
            
            return len(self.encoding.encode(text_content))
        except Exception as e:
            print(f"[ANALYTICS] Error in tiktoken encoding: {e}")
            # Fallback: approximate token count
            if hasattr(text, 'content'):
                text_content = text.content
            elif isinstance(text, str):
                text_content = text
            else:
                text_content = str(text)
            
            # More robust fallback
            try:
                return len(text_content.split()) * 1.3  # Rough approximation
            except Exception as e2:
                print(f"[ANALYTICS] Error in fallback: {e2}")
                return 0
    
    def count_message_tokens(self, messages: List[BaseMessage]) -> int:
        """Count tokens in a list of messages"""
        total_tokens = 0
        for message in messages:
            # Add tokens for message content
            total_tokens += self.count_tokens(str(message.content))
            # Add tokens for message metadata (role, etc.)
            total_tokens += 4  # Approximate overhead per message
        
        # Add system message overhead
        total_tokens += 3
        return total_tokens
    
    def extract_full_prompt(self, messages: List[BaseMessage]) -> str:
        """Extract the complete prompt being sent to LLM"""
        prompt_parts = []
        
        print(f"[ANALYTICS] Extracting prompt from {len(messages)} messages")
        
        # Handle case where messages might be nested lists
        flat_messages = []
        for item in messages:
            if isinstance(item, list):
                flat_messages.extend(item)
            else:
                flat_messages.append(item)
        
        for i, message in enumerate(flat_messages):
            try:
                # Check if message has content attribute
                if hasattr(message, 'content'):
                    role = message.__class__.__name__.replace("Message", "").lower()
                    content = str(message.content)
                elif hasattr(message, '__dict__'):
                    # Fallback for objects with dict representation
                    role = str(type(message).__name__).lower()
                    content = str(message)
                else:
                    # Last resort for other types
                    role = "unknown"
                    content = str(message)
                
                print(f"[ANALYTICS] Message {i}: {role} - Content: '{content[:200]}...'")
                
                # Better role mapping
                if role == "human":
                    role_display = "USER"
                elif role == "ai":
                    role_display = "ASSISTANT"  
                elif role == "system":
                    role_display = "SYSTEM"
                else:
                    role_display = role.upper()
                
                prompt_parts.append(f"[{role_display}]: {content}")
            except Exception as e:
                print(f"[ANALYTICS] Error processing message {i}: {e}")
                prompt_parts.append(f"[ERROR]: Could not process message - {str(message)[:100]}")
        
        full_prompt = "\n\n".join(prompt_parts)
        print(f"[ANALYTICS] Full prompt created - Length: {len(full_prompt)}")
        print(f"[ANALYTICS] First 300 chars: '{full_prompt[:300]}...'")
        print(f"[ANALYTICS] Last 300 chars: '...{full_prompt[-300:]}'")
        return full_prompt
    
    def create_llm_analytics(self, 
                           messages: List[BaseMessage],
                           response,  # Can be str or AIMessage
                           model_name: str = None,
                           temperature: float = 0.0,
                           usage_metadata: dict = None) -> Dict[str, Any]:
        """Create comprehensive LLM analytics data"""
        
        try:
            model = model_name or self.model_name
            
            # Extract full prompt
            full_prompt = self.extract_full_prompt(messages)
            
            # Handle response content
            if hasattr(response, 'content'):
                response_content = response.content
            else:
                response_content = str(response)
            
            # Use usage metadata if available, otherwise count tokens manually
            if usage_metadata:
                prompt_tokens = usage_metadata.get('input_tokens', 0)
                completion_tokens = usage_metadata.get('output_tokens', 0)
                total_tokens = usage_metadata.get('total_tokens', 0)
            else:
                # Count tokens manually
                prompt_tokens = self.count_message_tokens(messages)
                completion_tokens = self.count_tokens(response_content)
                total_tokens = prompt_tokens + completion_tokens
            
            return {
                "llm_prompt": full_prompt,
                "llm_response": response_content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "model_used": model,
                "temperature": temperature,
                "prompt_length_chars": len(full_prompt),
                "response_length_chars": len(response_content),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[ANALYTICS] Error creating analytics: {e}")
            # Return minimal analytics data
            return {
                "llm_prompt": "Error extracting prompt",
                "llm_response": str(response) if response else "Error extracting response",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "model_used": model_name or "unknown",
                "temperature": temperature,
                "prompt_length_chars": 0,
                "response_length_chars": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def analyze_prompt_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt complexity for insights"""
        words = prompt.split()
        sentences = prompt.count('.') + prompt.count('!') + prompt.count('?')
        
        return {
            "word_count": len(words),
            "sentence_count": sentences,
            "avg_words_per_sentence": len(words) / max(sentences, 1),
            "contains_code": any(keyword in prompt.lower() for keyword in ['def ', 'class ', 'import ', '```']),
            "contains_data": any(keyword in prompt.lower() for keyword in ['table', 'database', 'query', 'sql']),
            "contains_instructions": any(keyword in prompt.lower() for keyword in ['please', 'can you', 'help me', 'show me'])
        }


# Global analytics instance
_analytics_capture = None

def get_llm_analytics() -> LLMAnalyticsCapture:
    """Get global LLM analytics capture instance"""
    global _analytics_capture
    if _analytics_capture is None:
        _analytics_capture = LLMAnalyticsCapture()
    return _analytics_capture


def capture_llm_interaction(messages: List[BaseMessage], 
                          response,  # Can be str or AIMessage
                          model_name: str = "gpt-3.5-turbo",
                          temperature: float = 0.0,
                          usage_metadata: dict = None) -> Dict[str, Any]:
    """Convenience function to capture LLM interaction data"""
    analytics = get_llm_analytics()
    return analytics.create_llm_analytics(messages, response, model_name, temperature, usage_metadata)