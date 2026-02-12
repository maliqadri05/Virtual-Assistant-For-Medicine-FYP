"""
Doctor Agent - Generates comprehensive medical reports

Uses MedGemma to create structured medical assessment reports
based on gathered patient information.
"""

from typing import Dict, List, Optional
import logging
import json

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DoctorAgent(BaseAgent):
    """
    Generates comprehensive medical reports using MedGemma.
    
    Responsible for:
    - Analyzing all gathered information
    - Identifying likely conditions
    - Providing clinical recommendations
    - Structuring findings in professional format
    """
    
    def __init__(self, model_service=None):
        """
        Initialize doctor agent.
        
        Args:
            model_service: MedGemma service for report generation
        """
        super().__init__("Doctor", model_service)
    
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
        Generate comprehensive medical report.
        
        Args:
            conversation_history: All patient messages
            patient_context: Patient demographics and history
            
        Returns:
            Formatted medical report
        """
        # Prepare context for prompt
        conversation_text = "\n".join([f"Patient: {msg}" for msg in conversation_history])
        
        # Build patient summary
        patient_summary = self._build_patient_summary(patient_context)
        
        # Generate report using MedGemma
        if self.model_service:
            prompt = f"""You are an experienced medical doctor. Based on the patient information provided, generate a comprehensive medical assessment report.

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

            try:
                report = self.model_service.generate(prompt, max_tokens=800)
                return self._format_report(report)
            except Exception as e:
                logger.warning(f"MedGemma report failed: {str(e)}")
                return self._generate_template_report(conversation_history, patient_context)
        
        # Fallback to template
        return self._generate_template_report(conversation_history, patient_context)
    
    def _build_patient_summary(self, patient_context: Optional[Dict]) -> str:
        """Build patient summary from context"""
        if not patient_context:
            return "Patient Information: Not provided"
        
        summary = "Patient Information:\n"
        
        if 'name' in patient_context:
            summary += f"- Name: {patient_context['name']}\n"
        if 'age' in patient_context:
            summary += f"- Age: {patient_context['age']}\n"
        if 'sex' in patient_context:
            summary += f"- Sex: {patient_context['sex']}\n"
        if 'weight' in patient_context:
            summary += f"- Weight: {patient_context['weight']}kg\n"
        if 'medical_history' in patient_context:
            summary += f"- Past Medical History: {patient_context['medical_history']}\n"
        if 'medications' in patient_context:
            summary += f"- Current Medications: {patient_context['medications']}\n"
        if 'allergies' in patient_context:
            summary += f"- Allergies: {patient_context['allergies']}\n"
        
        return summary
    
    def _format_report(self, raw_report: str) -> str:
        """Format and clean report output"""
        # Remove markdown formatting if present
        report = raw_report.replace('**', '')
        report = report.replace('##', '')
        report = report.replace('#', '')
        
        return report.strip()
    
    def _generate_template_report(self,
                                 conversation_history: List[str],
                                 patient_context: Optional[Dict]) -> str:
        """
        Generate basic template report if AI fails.
        
        Args:
            conversation_history: Patient messages
            patient_context: Patient info
            
        Returns:
            Template-based report
        """
        conversation_text = " ".join(conversation_history).lower()
        
        # Extract information
        chief_complaint = conversation_history[0] if conversation_history else "Patient consultation"
        
        report = f"""
MEDICAL ASSESSMENT REPORT
{'='*50}

CHIEF COMPLAINT
{chief_complaint}

HISTORY OF PRESENT ILLNESS
Based on the patient's description:
- Patient reported: {chief_complaint}
- Duration and severity details were discussed during consultation
- Associated symptoms and relevant history were obtained

RECOMMENDATIONS
1. Continue monitoring symptoms
2. Seek immediate medical attention if symptoms worsen significantly
3. Consider follow-up evaluation with healthcare provider
4. Keep detailed record of symptom progression

IMPORTANT DISCLAIMER
This assessment is based on patient-reported information only and is NOT 
a substitute for professional medical evaluation. Please consult with a 
licensed healthcare provider for definitive diagnosis and treatment.

CONFIDENCE LEVEL
Moderate - Limited by inability to perform physical examination

This report should be reviewed by a qualified healthcare professional 
before any treatment decisions are made.
"""
        
        return report.strip()
    
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
