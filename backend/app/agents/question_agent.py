"""
Question Agent - Generates contextual follow-up questions

Uses MedGemma to create intelligent, medically relevant questions
to gather missing patient information.
"""

from typing import Dict, List, Optional
import logging
import json
import asyncio

from .base_agent import BaseAgent
from ..services.medgemma import get_medgemma_service

logger = logging.getLogger(__name__)


class QuestionAgent(BaseAgent):
    """
    Generates contextual follow-up questions using MedGemma.
    
    Responsible for:
    - Understanding what information is missing
    - Generating medically appropriate questions
    - Asking in patient-friendly language
    - Avoiding repetition
    """
    
    # Question templates for different categories
    QUESTION_TEMPLATES = {
        'symptoms': [
            "Can you describe your main symptom in more detail?",
            "What other symptoms are you experiencing?",
            "Have you noticed any other changes in how you feel?",
        ],
        'duration': [
            "When did you first notice this symptom?",
            "How long have you been experiencing this?",
            "Did this start suddenly or gradually?",
        ],
        'severity': [
            "On a scale of 1 to 10, how bad is your {symptom}?",
            "How much does this affect your daily activities?",
            "Is it getting worse, staying the same, or improving?",
        ],
        'location': [
            "Can you point to where you feel the {symptom}?",
            "Which part of your body is affected?",
            "Is the {symptom} in one area or spread out?",
        ],
        'medical_history': [
            "Do you have any medical conditions or chronic diseases?",
            "Are you currently taking any medications?",
            "Are you allergic to any medications or substances?",
        ]
    }
    
    def __init__(self, model_service=None):
        """
        Initialize question agent.
        
        Args:
            model_service: MedGemma service for question generation
        """
        super().__init__("Question", model_service)
        self.medgemma_service = get_medgemma_service()
    
    def process(self,
               conversation_history: List[str],
               patient_context: Optional[Dict] = None) -> Dict:
        """
        Generate next question based on conversation.
        
        Args:
            conversation_history: Previous messages
            patient_context: Patient demographics
            
        Returns:
            Response with generated question
        """
        try:
            question = self.generate_question(
                conversation_history,
                patient_context
            )
            
            return self._format_response(
                content=question,
                role="assistant",
                metadata={"agent": "question_generator"}
            )
        
        except Exception as e:
            logger.error(f"Question generation error: {str(e)}")
            return self._format_response(
                content="Could you tell me more about your condition?",
                role="assistant",
                metadata={"agent": "question_generator", "error": True}
            )
    
    def generate_question(self,
                         conversation_history: List[str],
                         patient_context: Optional[Dict] = None,
                         missing_category: str = None) -> str:
        """
        Generate intelligent follow-up question using MedGemma.
        
        Args:
            conversation_history: Patient messages
            patient_context: Patient info (age, sex)
            missing_category: What info is missing
            
        Returns:
            Generated question string
        """
        # Try MedGemma AI first
        if self.medgemma_service and self.medgemma_service.is_available():
            try:
                question = self._generate_dynamic_question(
                    conversation_history,
                    patient_context,
                    missing_category
                )
                if question:
                    return question
            except Exception as e:
                logger.warning(f"MedGemma question generation failed: {e}, using template fallback")
        
        # Fall back to template
        return self._get_template_question(conversation_history, missing_category)
    
    def _generate_dynamic_question(self,
                                  conversation_history: List[str],
                                  patient_context: Optional[Dict] = None,
                                  missing_category: Optional[str] = None) -> Optional[str]:
        """
        Generate dynamic question using MedGemma AI.
        
        Args:
            conversation_history: Patient messages
            patient_context: Patient demographics
            missing_category: What information is missing
            
        Returns:
            AI-generated question or None if failed
        """
        try:
            # Extract recent conversation context
            recent_history = self._truncate_history(conversation_history, max_items=5)
            
            # Extract symptoms from conversation as list
            symptoms = []
            symptom_keywords = ['pain', 'ache', 'fever', 'cough', 'fatigue', 'nausea',
                              'headache', 'dizziness', 'rash', 'itch', 'swelling']
            conversation_text = " ".join(recent_history).lower()
            for keyword in symptom_keywords:
                if keyword in conversation_text:
                    symptoms.append(keyword)
            if not symptoms:
                symptoms = ["general wellness inquiry"]
            
            # Format conversation history as list of dicts
            formatted_history = []
            for i, msg in enumerate(recent_history):
                formatted_history.append({
                    'patient': msg,
                    'assistant': 'Assistant response' if i > 0 else ''
                })
            
            # Identify what information might be missing
            missing_info_list = self._identify_missing_info(conversation_history, patient_context)
            missing_info_str = ", ".join(missing_info_list) if missing_info_list else "additional clinical context"
            
            # Run async MedGemma generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            question = loop.run_until_complete(
                self.medgemma_service.generate_question(
                    symptoms=symptoms,
                    conversation_history=formatted_history,
                    missing_info=missing_info_str
                )
            )
            loop.close()
            
            logger.info("✅ Dynamic question generated using MedGemma")
            return question
            
        except Exception as e:
            logger.error(f"Dynamic question generation error: {e}")
            return None
    
    def _identify_missing_info(self,
                              conversation_history: List[str],
                              patient_context: Optional[Dict] = None) -> List[str]:
        """
        Identify what information is missing from conversation.
        
        Args:
            conversation_history: All patient messages
            patient_context: Patient demographics
            
        Returns:
            List of missing information categories
        """
        conversation_text = " ".join(conversation_history).lower()
        missing = []
        
        # Check for symptom severity
        if any(word in conversation_text for word in ['pain', 'ache', 'hurt', 'sharp']):
            if not any(num in conversation_text for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']):
                missing.append("severity scale")
        
        # Check for duration
        if not any(word in conversation_text for word in ['day', 'week', 'month', 'year', 'hours', 'minutes']):
            missing.append("symptom duration")
        
        # Check for location (if applicable to pain)
        if 'pain' in conversation_text:
            if not any(word in conversation_text for word in ['left', 'right', 'back', 'front', 'head', 'chest', 'leg', 'arm']):
                missing.append("symptom location")
        
        # Check for medications/history
        if patient_context is None or len(patient_context) < 3:
            missing.append("medical history and medications")
        
        return missing
    
    def _get_template_question(self, 
                              conversation_history: List[str],
                              missing_category: Optional[str] = None) -> str:
        """
        Get question from template if AI fails.
        
        Args:
            conversation_history: Patient messages
            missing_category: What's missing
            
        Returns:
            Template-based question
        """
        conversation_text = " ".join(conversation_history).lower()
        
        # Detect category if not provided
        if not missing_category:
            if 'pain' in conversation_text or 'ache' in conversation_text:
                if '10' not in conversation_text and '/' not in conversation_text:
                    symptom = 'pain' if 'pain' in conversation_text else 'symptom'
                    return f"On a scale of 1 to 10, how severe is your {symptom}?"
                if 'left' not in conversation_text and 'right' not in conversation_text:
                    return "Where exactly do you feel the pain?"
            
            if 'day' not in conversation_text and 'week' not in conversation_text:
                return "When did this symptom start?"
            
            if 'medication' not in conversation_text and 'condition' not in conversation_text:
                return "Do you have any medical conditions or take any medications?"
        
        # Use category-specific templates
        if missing_category in self.QUESTION_TEMPLATES:
            questions = self.QUESTION_TEMPLATES[missing_category]
            return questions[0]
        
        # Default fallback
        return "Can you tell me more about how you're feeling?"
    
    def extract_symptom_from_history(self, conversation_history: List[str]) -> str:
        """Extract main symptom mentioned"""
        conversation_text = " ".join(conversation_history).lower()
        
        symptoms = ['pain', 'fever', 'cough', 'headache', 'nausea', 'fatigue']
        for symptom in symptoms:
            if symptom in conversation_text:
                return symptom
        
        return 'symptom'
