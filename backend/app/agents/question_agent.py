"""
Question Agent - Generates contextual follow-up questions

Uses MedGemma to create intelligent, medically relevant questions
to gather missing patient information.
"""

from typing import Dict, List, Optional
import logging
import json

from .base_agent import BaseAgent

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
        Generate intelligent follow-up question.
        
        Args:
            conversation_history: Patient messages
            patient_context: Patient info (age, sex)
            missing_category: What info is missing
            
        Returns:
            Generated question string
        """
        # Build context
        recent_history = self._truncate_history(conversation_history, max_items=5)
        conversation_text = "\n".join(recent_history)
        
        # Build patient context string
        patient_str = ""
        if patient_context:
            patient_str = f"Patient Profile:\n"
            if 'age' in patient_context:
                patient_str += f"- Age: {patient_context['age']}\n"
            if 'sex' in patient_context:
                patient_str += f"- Sex: {patient_context['sex']}\n"
            if 'weight' in patient_context:
                patient_str += f"- Weight: {patient_context['weight']}kg\n"
        
        # Generate question using MedGemma
        if self.model_service:
            prompt = f"""You are a helpful medical assistant. Based on the patient conversation, generate ONE natural follow-up question to gather more information about their condition.

{patient_str}

Patient Conversation:
{conversation_text}

Guidelines:
- Ask one clear, specific question
- Use simple, patient-friendly language
- Avoid medical jargon when possible
- Don't repeat questions already asked
- Be empathetic and supportive
- If asking about pain, ask for a scale (1-10)

Generate only the question, no explanation."""

            try:
                response = self.model_service.generate(prompt, max_tokens=100)
                # Clean response
                question = response.strip()
                if question.endswith('?'):
                    return question
                return question + "?"
            except Exception as e:
                logger.warning(f"MedGemma failed, using template: {str(e)}")
                return self._get_template_question(conversation_history, missing_category)
        
        # Fallback to template
        return self._get_template_question(conversation_history, missing_category)
    
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
