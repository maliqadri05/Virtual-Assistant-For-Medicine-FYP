"""
Base Agent Class - Abstract interface for all agents

All agents implement this interface for consistency.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    
    All agents follow the same interface:
    - Input: Conversation history + patient context
    - Processing: Agent-specific logic
    - Output: Standard response format
    """
    
    def __init__(self, name: str, model_service=None):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (for logging)
            model_service: AI model service (MedGemma, etc.)
        """
        self.name = name
        self.model_service = model_service
        logger.info(f"{self.name} Agent initialized")
    
    @abstractmethod
    def process(self,
               conversation_history: List[str],
               patient_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process agent logic.
        
        Args:
            conversation_history: Previous messages
            patient_context: Patient info (age, sex, history)
            
        Returns:
            Standard response dictionary
        """
        pass
    
    def _format_response(self,
                        content: str,
                        role: str = "assistant",
                        metadata: Optional[Dict] = None) -> Dict:
        """
        Format standard agent response.
        
        Args:
            content: Response text
            role: "assistant" | "system"
            metadata: Additional data
            
        Returns:
            Formatted response dict
        """
        response = {
            "role": role,
            "content": content
        }
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    def _extract_keywords(self, text: str, keywords: set) -> list:
        """Extract matched keywords from text"""
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower]
    
    def _truncate_history(self, history: List[str], max_items: int = 10) -> List[str]:
        """Keep recent history"""
        return history[-max_items:] if len(history) > max_items else history
