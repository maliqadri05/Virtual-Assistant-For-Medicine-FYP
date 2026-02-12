"""
Agent Manager - Orchestrates multi-agent workflow

Manages the flow between validation, question, and doctor agents.
Coordinates the multi-turn conversation for medical assessment.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from .validation_agent import HybridValidationAgent
from .question_agent import QuestionAgent
from .doctor_agent import DoctorAgent

logger = logging.getLogger(__name__)


@dataclass
class AgentResponse:
    """Standard response from agent processing"""
    agent_name: str
    content: str
    should_continue: bool
    metadata: Optional[Dict] = None


class AgentManager:
    """
    Orchestrates multi-agent system.
    
    Flow:
    1. User sends message → Added to conversation
    2. ValidationAgent checks completeness
    3. If incomplete → QuestionAgent generates question
    4. If complete → DoctorAgent generates report
    5. Return response to user
    """
    
    def __init__(self,
                 model_service=None):
        """
        Initialize agent manager.
        
        Args:
            model_service: MedGemma service for agents
        """
        self.validation_agent = HybridValidationAgent(model_service)
        self.question_agent = QuestionAgent(model_service)
        self.doctor_agent = DoctorAgent(model_service)
        self.model_service = model_service
        
        logger.info("AgentManager initialized")
    
    def process_message(self,
                       user_message: str,
                       conversation_history: List[str],
                       patient_context: Optional[Dict] = None) -> Dict:
        """
        Process user message and generate response.
        
        Main orchestration method.
        
        Args:
            user_message: New message from user
            conversation_history: Previous messages
            patient_context: Patient demographics
            
        Returns:
            Response from appropriate agent
        """
        try:
            # Add user message to history
            updated_history = conversation_history + [user_message]
            
            logger.info(
                f"Processing message. History length: {len(updated_history)}"
            )
            
            # Step 1: Validate information completeness
            validation_result = self.validation_agent.evaluate_completeness(
                updated_history,
                patient_context
            )
            
            logger.debug(
                f"Validation result: "
                f"continue={validation_result['should_continue_asking']}, "
                f"missing={validation_result['missing_category']}"
            )
            
            # Step 2: Route to appropriate agent
            should_continue = validation_result['should_continue_asking']
            
            if should_continue:
                # Generate next question
                missing_category = validation_result['missing_category']
                response = self.question_agent.process(
                    updated_history,
                    patient_context
                )
                response['validation'] = validation_result
                response['conversation_length'] = len(updated_history)
                return response
            else:
                # Generate medical report
                response = self.doctor_agent.process(
                    updated_history,
                    patient_context
                )
                response['validation'] = validation_result
                response['conversation_length'] = len(updated_history)
                return response
        
        except Exception as e:
            logger.error(f"Agent processing error: {str(e)}")
            return {
                "role": "assistant",
                "content": "I encountered an error processing your message. Please try again.",
                "error": True
            }
    
    def start_conversation(self, patient_context: Optional[Dict] = None) -> Dict:
        """
        Start new conversation with opening question.
        
        Args:
            patient_context: Patient info
            
        Returns:
            Opening statement and first question
        """
        opening = (
            "Hello! I'm here to help assess your medical condition. "
            "Please start by telling me what brings you in today and what symptoms you're experiencing."
        )
        
        return {
            "role": "assistant",
            "content": opening,
            "agent": "system",
            "conversation_length": 0
        }
    
    def reset_conversation(self) -> None:
        """Reset agents for new conversation"""
        self.validation_agent.reset()
        logger.info("Conversation reset")
    
    def get_conversation_status(self,
                               conversation_history: List[str],
                               patient_context: Optional[Dict] = None) -> Dict:
        """
        Get current conversation status.
        
        Args:
            conversation_history: Current messages
            patient_context: Patient info
            
        Returns:
            Status information
        """
        validation_result = self.validation_agent.evaluate_completeness(
            conversation_history,
            patient_context
        )
        
        return {
            "message_count": len(conversation_history),
            "validation": validation_result,
            "is_complete": not validation_result['should_continue_asking'],
            "missing_category": validation_result['missing_category']
        }
    
    def can_generate_report(self,
                           conversation_history: List[str],
                           patient_context: Optional[Dict] = None) -> bool:
        """
        Check if conversation has enough information for report.
        
        Args:
            conversation_history: Current messages
            patient_context: Patient info
            
        Returns:
            True if ready for report generation
        """
        status = self.get_conversation_status(conversation_history, patient_context)
        return status['is_complete']
    
    def force_report_generation(self,
                               conversation_history: List[str],
                               patient_context: Optional[Dict] = None) -> Dict:
        """
        Force report generation regardless of validation.
        
        Use only when needed (user explicitly requests report).
        
        Args:
            conversation_history: Current messages
            patient_context: Patient info
            
        Returns:
            Generated report
        """
        logger.warning("Force generating report regardless of validation")
        
        return self.doctor_agent.process(
            conversation_history,
            patient_context
        )
