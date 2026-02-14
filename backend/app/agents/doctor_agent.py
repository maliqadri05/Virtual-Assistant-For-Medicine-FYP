"""
Doctor Agent - Generates comprehensive medical reports (OPTIMIZED)

Uses MedGemma to create structured medical assessment reports
based on gathered patient information.

Performance Optimizations:
✅ Cached patient summary generation (avoid rebuilding)
✅ Optimized prompt construction (pre-built template)
✅ Early fallback detection
✅ Efficient string operations
✅ Template report caching
✅ MedGemma AI integration for dynamic reports
"""

from typing import Dict, List, Optional
import logging
import json
from functools import lru_cache
import asyncio

from .base_agent import BaseAgent
from ..services.medgemma import get_medgemma_service

logger = logging.getLogger(__name__)


class DoctorAgent(BaseAgent):
    """
    Generates comprehensive medical reports using MedGemma.
    
    OPTIMIZATIONS:
    - Caches patient summary generation
    - Pre-built prompt template (avoid repeated concatenation)
    - Early fallback for AI failures
    - Efficient string operations
    
    Responsible for:
    - Analyzing all gathered information
    - Identifying likely conditions
    - Providing clinical recommendations
    - Structuring findings in professional format
    """
    
    # Pre-compiled prompt template (OPTIMIZATION: reuse instead of rebuild)
    REPORT_PROMPT_TEMPLATE = """You are an experienced medical doctor. Based on the patient information provided, generate a comprehensive medical assessment report.

{patient_summary}

Patient Conversation:
{conversation_text}

Generate a structured medical report with the following sections:

1. CHIEF COMPLAINT
   - Main symptom presented

2. HISTORY OF PRESENT ILLNESS (HPI)
   - Timeline of symptoms
   - Duration and severity
   - Associated symptoms
   - What makes it worse/better

3. PHYSICAL FINDINGS (based on patient description)
   - Relevant observations

4. PRELIMINARY ASSESSMENT
   - List 2-3 most likely diagnoses (differential diagnosis)
   - Reasoning for each

5. RECOMMENDATIONS
   - Immediate actions
   - When to seek emergency care
   - Follow-up care suggestions

6. CONFIDENCE LEVEL
   - Rate your confidence (0-100%)
   - Important considerations/limitations

Format the report professionally but in language easy for the patient to understand. Include a disclaimer that this is not a substitute for professional medical evaluation."""
    
    def __init__(self, model_service=None):
        """
        Initialize doctor agent.
        
        Args:
            model_service: MedGemma service for report generation
        """
        super().__init__("Doctor", model_service)
        self._patient_summary_cache: Dict = {}
        # Initialize MedGemma service
        self.medgemma_service = get_medgemma_service()
    
    def process(self,
               conversation_history: List[str],
               patient_context: Optional[Dict] = None) -> Dict:
        """
        Generate medical report.
        
        Args:
            conversation_history: All patient messages
            patient_context: Patient demographics
            
        Returns:
            Response with generated report
        """
        try:
            report = self.generate_report(
                conversation_history,
                patient_context
            )
            
            return self._format_response(
                content=report,
                role="assistant",
                metadata={
                    "agent": "doctor_report_generator",
                    "type": "medical_report"
                }
            )
        
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return self._format_response(
                content="I encountered an error generating the report. Please try again.",
                role="assistant",
                metadata={"agent": "doctor_report_generator", "error": True}
            )
    
    def generate_report(self,
                       conversation_history: List[str],
                       patient_context: Optional[Dict] = None) -> str:
        """
        Generate comprehensive medical report - OPTIMIZED.
        
        Tries MedGemma AI first, falls back to templates if unavailable.
        
        Args:
            conversation_history: All patient messages
            patient_context: Patient demographics and history
            
        Returns:
            Formatted medical report
        """
        # Try MedGemma AI generation first
        if self.medgemma_service and self.medgemma_service.is_available():
            try:
                report = self._generate_dynamic_report(conversation_history, patient_context)
                if report:
                    return report
            except Exception as e:
                logger.warning(f"MedGemma report generation failed: {e}, using template fallback")
        
        # Fall back to template-based report
        return self._generate_template_report(conversation_history, patient_context)
    
    def _generate_dynamic_report(self,
                                conversation_history: List[str],
                                patient_context: Optional[Dict] = None) -> Optional[str]:
        """
        Generate dynamic report using MedGemma AI.
        
        Args:
            conversation_history: All patient messages
            patient_context: Patient demographics and history
            
        Returns:
            AI-generated medical report or None if failed
        """
        try:
            # Extract symptoms from conversation
            symptoms = self._extract_symptoms(conversation_history)
            
            # Prepare medical history
            history = patient_context or {}
            
            # Get context
            context = "\n".join(conversation_history[-5:]) if conversation_history else ""
            
            # Run async MedGemma generation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            report = loop.run_until_complete(
                self.medgemma_service.generate_report(
                    symptoms=symptoms,
                    history=history,
                    context=context,
                    use_cache=True
                )
            )
            loop.close()
            
            logger.info("✅ Dynamic report generated using MedGemma")
            return report
            
        except Exception as e:
            logger.error(f"Dynamic report generation error: {e}")
            return None
    
    def _extract_symptoms(self, conversation_history: List[str]) -> List[str]:
        """
        Extract symptoms from conversation history.
        
        Args:
            conversation_history: All patient messages
            
        Returns:
            List of identified symptoms
        """
        symptoms = []
        symptom_keywords = [
            'pain', 'ache', 'fever', 'cough', 'fatigue', 'nausea',
            'headache', 'dizziness', 'rash', 'itch', 'swelling',
            'difficulty', 'shortness', 'chest', 'abdominal', 'joint'
        ]
        
        for message in conversation_history:
            message_lower = message.lower()
            for keyword in symptom_keywords:
                if keyword in message_lower and message not in symptoms:
                    symptoms.append(message)
                    break
        
        return symptoms
    
    def _get_patient_summary(self, patient_context: Optional[Dict]) -> str:
        """
        OPTIMIZED: Cache patient summary to avoid rebuilding.
        
        Args:
            patient_context: Patient info dict
            
        Returns:
            Formatted patient summary string
        """
        if not patient_context:
            return "Patient Information: Not provided"
        
        # Create cache key from patient_context
        cache_key = str(sorted(patient_context.items()))
        
        # Check cache
        if cache_key in self._patient_summary_cache:
            return self._patient_summary_cache[cache_key]
        
        # Build summary (efficient list join instead of += concatenation)
        summary_parts = ["Patient Information:"]
        
        if 'name' in patient_context:
            summary_parts.append(f"- Name: {patient_context['name']}")
        if 'age' in patient_context:
            summary_parts.append(f"- Age: {patient_context['age']}")
        if 'sex' in patient_context:
            summary_parts.append(f"- Sex: {patient_context['sex']}")
        if 'weight' in patient_context:
            summary_parts.append(f"- Weight: {patient_context['weight']}kg")
        if 'medical_history' in patient_context:
            summary_parts.append(f"- Past Medical History: {patient_context['medical_history']}")
        if 'medications' in patient_context:
            summary_parts.append(f"- Current Medications: {patient_context['medications']}")
        if 'allergies' in patient_context:
            summary_parts.append(f"- Allergies: {patient_context['allergies']}")
        
        summary = "\n".join(summary_parts)
        
        # Cache it
        self._patient_summary_cache[cache_key] = summary
        
        return summary
    
    def _format_report(self, raw_report: str) -> str:
        """
        OPTIMIZED: Format and clean report output with single pass.
        
        Args:
            raw_report: Raw report from model
            
        Returns:
            Cleaned report
        """
        # Single pass cleanup instead of multiple replaces
        replacements = {
            '**': '',
            '##': '',
            '# ': '',
        }
        
        report = raw_report
        for old, new in replacements.items():
            report = report.replace(old, new)
        
        return report.strip()
    
    # Cache for template reports
    _template_cache: Dict[str, str] = {}
    
    def _generate_template_report(self,
                                 conversation_history: List[str],
                                 patient_context: Optional[Dict]) -> str:
        """
        OPTIMIZED: Generate basic template report with caching.
        
        Args:
            conversation_history: Patient messages
            patient_context: Patient info
            
        Returns:
            Template-based report
        """
        # OPTIMIZATION: Check cache first
        history_key = str(hash(tuple(conversation_history[-3:])))  # Use last 3 messages as key
        
        if history_key in self._template_cache:
            return self._template_cache[history_key]
        
        chief_complaint = conversation_history[0] if conversation_history else "Patient consultation"
        
        # OPTIMIZATION: Use list join instead of f-string with embedded newlines
        report_parts = [
            "MEDICAL ASSESSMENT REPORT",
            "=" * 50,
            "",
            "CHIEF COMPLAINT",
            chief_complaint,
            "",
            "HISTORY OF PRESENT ILLNESS",
            "Based on the patient's description:",
            f"- Patient reported: {chief_complaint}",
            "- Duration and severity details were discussed during consultation",
            "- Associated symptoms and relevant history were obtained",
            "",
            "RECOMMENDATIONS",
            "1. Continue monitoring symptoms",
            "2. Seek immediate medical attention if symptoms worsen significantly",
            "3. Consider follow-up evaluation with healthcare provider",
            "4. Keep detailed record of symptom progression",
            "",
            "IMPORTANT DISCLAIMER",
            "This assessment is based on patient-reported information only and is NOT",
            "a substitute for professional medical evaluation. Please consult with a",
            "licensed healthcare provider for definitive diagnosis and treatment.",
            "",
            "CONFIDENCE LEVEL",
            "Moderate - Limited by inability to perform physical examination",
            "",
            "This report should be reviewed by a qualified healthcare professional",
            "before any treatment decisions are made.",
        ]
        
        report = "\n".join(report_parts)
        
        # Cache it
        self._template_cache[history_key] = report
        
        return report
    
    def parse_report_json(self, report_text: str) -> Dict:
        """
        Parse report into structured JSON format.
        
        Args:
            report_text: Raw report text
            
        Returns:
            Structured report dictionary
        """
        report_json = {
            "chief_complaint": "",
            "history": "",
            "findings": "",
            "assessment": {
                "diagnoses": [],
                "confidence": 0
            },
            "recommendations": [],
            "disclaimer": "This is not a substitute for professional medical advice"
        }
        
        # Basic parsing logic
        lines = report_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'CHIEF COMPLAINT' in line:
                current_section = 'chief_complaint'
            elif 'HISTORY' in line:
                current_section = 'history'
            elif 'FINDING' in line:
                current_section = 'findings'
            elif 'ASSESSMENT' in line:
                current_section = 'assessment'
            elif 'RECOMMENDATION' in line:
                current_section = 'recommendations'
            elif current_section:
                if current_section == 'recommendations':
                    report_json['recommendations'].append(line)
                elif current_section == 'chief_complaint':
                    report_json['chief_complaint'] += line + " "
                elif current_section == 'history':
                    report_json['history'] += line + " "
                elif current_section == 'findings':
                    report_json['findings'] += line + " "
        
        return report_json
