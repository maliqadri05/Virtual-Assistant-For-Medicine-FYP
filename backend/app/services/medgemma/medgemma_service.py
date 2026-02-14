"""
MedGemma AI Service for Dynamic Medical Report Generation

This service integrates the MedGemma model for:
- Dynamic, personalized medical report generation
- Contextual follow-up question generation
- Medical text analysis and insights
"""

import logging
import asyncio
from typing import Optional, Dict, List, Any
from functools import lru_cache
import json

try:
    from langchain.llms import LlamaCpp
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

logger = logging.getLogger(__name__)


class MedGemmaService:
    """
    Service for MedGemma AI model integration
    
    Features:
    - Dynamic report generation
    - Contextual question generation
    - Caching for performance
    - Fallback mechanisms
    - Safety filters
    """
    
    _instance = None
    _model = None
    _model_path = None
    
    def __new__(cls, model_path: Optional[str] = None):
        """Singleton pattern for model loading"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize MedGemma Service
        
        Args:
            model_path: Path to MedGemma model file (GGUF format)
        """
        if self._initialized:
            return
        
        self.model_path = model_path
        self.model = None
        self.prompt_cache = {}
        self.report_cache = {}
        self.response_cache = {}
        self._initialized = True
        
        # Load model if path provided
        if model_path:
            self._load_model(model_path)
    
    def _load_model(self, model_path: str) -> None:
        """
        Load MedGemma model
        
        Args:
            model_path: Path to GGUF model file
        """
        try:
            logger.info(f"Loading MedGemma model from {model_path}")
            
            if not LANGCHAIN_AVAILABLE:
                logger.warning("LangChain not available, using fallback")
                return
            
            # Load with GPU acceleration if available
            self.model = LlamaCpp(
                model_path=model_path,
                n_gpu_layers=-1,  # Use GPU for all layers
                n_ctx=4096,  # Context window
                n_batch=512,  # Batch size
                f16_kv=True,  # Use float16 for KV cache
                verbose=False,
                temperature=0.7,
                top_p=0.9,
                top_k=40
            )
            
            logger.info("✅ MedGemma model loaded successfully")
            MedGemmaService._model = self.model
            
        except Exception as e:
            logger.error(f"❌ Failed to load MedGemma model: {e}")
            self.model = None
    
    @staticmethod
    def is_available() -> bool:
        """Check if MedGemma model is available"""
        return MedGemmaService._model is not None
    
    def _create_report_prompt(
        self,
        symptoms: List[str],
        history: Dict[str, Any],
        context: str = ""
    ) -> str:
        """
        Create a medical report prompt for MedGemma
        
        Args:
            symptoms: List of reported symptoms
            history: Patient medical history
            context: Additional context
            
        Returns:
            Formatted prompt for the model
        """
        symptoms_text = "\n".join([f"- {s}" for s in symptoms])
        history_text = json.dumps(history, indent=2)
        
        prompt = f"""You are an experienced medical assistant. Based on the following patient information, 
generate a comprehensive medical assessment report in SOAP format.

SYMPTOMS REPORTED:
{symptoms_text}

MEDICAL HISTORY:
{history_text}

ADDITIONAL CONTEXT:
{context}

Generate a professional medical report with the following REQUIRED sections:
1. CHIEF COMPLAINT - Brief summary of main concern
2. HISTORY OF PRESENT ILLNESS - Detailed timeline of symptoms
3. RELEVANT MEDICAL HISTORY - Applicable past conditions
4. RECOMMENDATIONS - Suggested next steps and when to seek emergency care
5. IMPORTANT DISCLAIMER - Medical liability and professional advice disclaimer

Report:"""
        return prompt
    
    def _create_question_prompt(
        self,
        symptoms: List[str],
        conversation_history: List[Dict[str, str]],
        missing_info: str = ""
    ) -> str:
        """
        Create a follow-up question prompt for MedGemma
        
        Args:
            symptoms: Current reported symptoms
            conversation_history: Previous conversation turns
            missing_info: What information is still needed
            
        Returns:
            Formatted prompt for question generation
        """
        history_text = "\n".join([
            f"- Patient: {turn['patient']}\n- Assistant: {turn['assistant']}"
            for turn in conversation_history[-3:]  # Last 3 turns
        ])
        
        symptoms_text = ", ".join(symptoms)
        
        prompt = f"""You are a medical assistant conducting a patient consultation. 
Based on the conversation history and current symptoms, generate ONE relevant follow-up question.

CURRENT SYMPTOMS: {symptoms_text}

MISSING INFORMATION TO GATHER: {missing_info}

CONVERSATION HISTORY:
{history_text}

REQUIREMENTS:
1. Generate exactly ONE question
2. Question should advance the medical assessment
3. Use patient-friendly language
4. Ask about relevant clinical details
5. Be specific and focused

Follow-up question:"""
        return prompt
    
    @staticmethod
    def _sanitize_response(response: str) -> str:
        """
        Sanitize model response for safety
        
        Args:
            response: Raw model response
            
        Returns:
            Cleaned and safe response
        """
        # Remove any medication recommendations without proper context
        if "prescribe" in response.lower() or "dosage" in response.lower():
            response += "\n\n**NOTE: Medication recommendations require physician consultation.**"
        
        # Remove any absolute diagnoses
        response = response.replace("diagnosis is", "may be related to")
        response = response.replace("diagnosed with", "symptoms consistent with")
        
        # Ensure disclaimer is present
        if "disclaimer" not in response.lower():
            response += "\n\n**IMPORTANT DISCLAIMER**: This assessment is for informational purposes only and is NOT a substitute for professional medical evaluation. Please consult with a licensed healthcare provider."
        
        return response
    
    async def generate_report(
        self,
        symptoms: List[str],
        history: Dict[str, Any],
        context: str = "",
        use_cache: bool = True,
        streaming: bool = False
    ) -> str:
        """
        Generate a dynamic medical report using MedGemma
        
        Args:
            symptoms: List of patient symptoms
            history: Medical history dictionary
            context: Additional context
            use_cache: Use cached results if available
            streaming: Stream response tokens (not yet implemented)
            
        Returns:
            Generated medical report
        """
        # Check cache first
        cache_key = f"report_{hash(str(symptoms))}"
        if use_cache and cache_key in self.report_cache:
            logger.info("✅ Using cached report")
            return self.report_cache[cache_key]
        
        # If model not available, return template fallback
        if not self.is_available():
            logger.warning("⚠️ MedGemma not available, using template fallback")
            return self._generate_template_report(symptoms, history)
        
        try:
            prompt = self._create_report_prompt(symptoms, history, context)
            
            # Generate report in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model(prompt, max_tokens=1500)
            )
            
            # Sanitize response
            sanitized = self._sanitize_response(response)
            
            # Cache result
            self.report_cache[cache_key] = sanitized
            
            logger.info("✅ Report generated successfully")
            return sanitized
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            return self._generate_template_report(symptoms, history)
    
    async def generate_question(
        self,
        symptoms: List[str],
        conversation_history: List[Dict[str, str]],
        missing_info: str = "additional clinical context"
    ) -> str:
        """
        Generate a contextual follow-up question using MedGemma
        
        Args:
            symptoms: Current symptoms
            conversation_history: Previous conversation turns
            missing_info: What information is missing
            
        Returns:
            Generated follow-up question
        """
        # Check cache
        cache_key = f"question_{hash(str(symptoms))}"
        if cache_key in self.response_cache:
            logger.info("✅ Using cached question")
            return self.response_cache[cache_key]
        
        # If model not available, return template fallback
        if not self.is_available():
            logger.warning("⚠️ MedGemma not available, using template fallback")
            return self._generate_template_question(symptoms, missing_info)
        
        try:
            prompt = self._create_question_prompt(symptoms, conversation_history, missing_info)
            
            # Generate question in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model(prompt, max_tokens=200)
            )
            
            # Clean up response
            question = response.strip().split("\n")[0]
            
            # Cache result
            self.response_cache[cache_key] = question
            
            logger.info("✅ Question generated successfully")
            return question
            
        except Exception as e:
            logger.error(f"❌ Error generating question: {e}")
            return self._generate_template_question(symptoms, missing_info)
    
    @staticmethod
    def _generate_template_report(symptoms: List[str], history: Dict[str, Any]) -> str:
        """Fallback template report generation"""
        symptom_list = ", ".join(symptoms)
        return f"""MEDICAL ASSESSMENT REPORT
==================================================

CHIEF COMPLAINT
{symptom_list}

HISTORY OF PRESENT ILLNESS
Based on the patient's description:
- Reported symptoms: {symptom_list}
- Medical history: {json.dumps(history, indent=2)}

RECOMMENDATIONS
1. Monitor symptoms for any changes
2. Seek medical attention if symptoms persist or worsen
3. Maintain detailed symptom records
4. Follow up with primary care physician

IMPORTANT DISCLAIMER
This assessment is for informational purposes only and is NOT a substitute 
for professional medical evaluation. Please consult with a licensed healthcare 
provider for definitive diagnosis and treatment recommendations."""
    
    @staticmethod
    def _generate_template_question(symptoms: List[str], missing_info: str) -> str:
        """Fallback template question generation"""
        if "severity" in missing_info.lower():
            return "On a scale of 1 to 10, how severe is your symptom?"
        elif "duration" in missing_info.lower():
            return "How long have you been experiencing these symptoms?"
        elif "history" in missing_info.lower():
            return "Do you have any existing medical conditions or allergies?"
        else:
            return "Can you provide more details about what you're experiencing?"
    
    def clear_cache(self) -> None:
        """Clear all caches"""
        self.report_cache.clear()
        self.response_cache.clear()
        self.prompt_cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "report_cache_size": len(self.report_cache),
            "response_cache_size": len(self.response_cache),
            "prompt_cache_size": len(self.prompt_cache),
        }


# Global service instance
_medgemma_service = None


def get_medgemma_service(model_path: Optional[str] = None) -> MedGemmaService:
    """Get or create MedGemmaService instance"""
    global _medgemma_service
    if _medgemma_service is None:
        _medgemma_service = MedGemmaService(model_path)
    return _medgemma_service
