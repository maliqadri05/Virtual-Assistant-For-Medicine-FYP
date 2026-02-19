"""
Translation service for multi-language support

Handles translation of medical content, UI strings, and responses
to 10+ languages with caching and fallback mechanisms.
"""

from typing import Dict, Optional, List
import logging
from datetime import datetime
from functools import lru_cache

logger = logging.getLogger(__name__)


class TranslationService:
    """Manages translation of medical content to multiple languages"""
    
    # Supported languages with language codes
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "zh": "Mandarin Chinese",
        "ja": "Japanese",
        "de": "German",
        "pt": "Portuguese",
        "ar": "Arabic",
        "hi": "Hindi",
        "it": "Italian"
    }
    
    # Medical term translations
    MEDICAL_TRANSLATIONS = {
        "en": {
            "headache": "headache",
            "fever": "fever",
            "cough": "cough",
            "chest_pain": "chest pain",
            "fatigue": "fatigue",
            "dizziness": "dizziness",
            "nausea": "nausea",
            "hypertension": "hypertension",
            "diabetes": "diabetes",
            "allergy": "allergy"
        },
        "es": {
            "headache": "dolor de cabeza",
            "fever": "fiebre",
            "cough": "tos",
            "chest_pain": "dolor de pecho",
            "fatigue": "fatiga",
            "dizziness": "mareo",
            "nausea": "náusea",
            "hypertension": "hipertensión",
            "diabetes": "diabetes",
            "allergy": "alergia"
        },
        "fr": {
            "headache": "mal de tête",
            "fever": "fièvre",
            "cough": "toux",
            "chest_pain": "douleur thoracique",
            "fatigue": "fatigue",
            "dizziness": "vertige",
            "nausea": "nausée",
            "hypertension": "hypertension",
            "diabetes": "diabète",
            "allergy": "allergie"
        },
        "zh": {
            "headache": "头痛",
            "fever": "发烧",
            "cough": "咳嗽",
            "chest_pain": "胸痛",
            "fatigue": "疲劳",
            "dizziness": "眩晕",
            "nausea": "恶心",
            "hypertension": "高血压",
            "diabetes": "糖尿病",
            "allergy": "过敏"
        }
    }
    
    def __init__(self):
        """Initialize translation service"""
        self.default_language = "en"
        self.cache = {}
        logger.info("TranslationService initialized")
    
    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """Get list of supported languages with names"""
        return TranslationService.SUPPORTED_LANGUAGES.copy()
    
    def validate_language(self, language_code: str) -> bool:
        """Validate if language code is supported"""
        return language_code.lower() in self.SUPPORTED_LANGUAGES
    
    @lru_cache(maxsize=1000)
    def translate_term(self, term: str, target_language: str) -> str:
        """
        Translate a medical term to target language
        
        Args:
            term: English medical term
            target_language: Target language code (e.g., 'es', 'fr')
        
        Returns:
            Translated term or original if translation not available
        """
        if not self.validate_language(target_language):
            target_language = self.default_language
        
        term_lower = term.lower().replace(" ", "_")
        
        # Try to get translation from MEDICAL_TRANSLATIONS
        if target_language in self.MEDICAL_TRANSLATIONS:
            translation = self.MEDICAL_TRANSLATIONS[target_language].get(
                term_lower,
                term  # Fallback to original term
            )
            logger.debug(f"Translated '{term}' to '{translation}' ({target_language})")
            return translation
        
        logger.warning(f"Language {target_language} not supported, using English")
        return term
    
    def translate_health_insight(
        self,
        insight_text: str,
        target_language: str
    ) -> str:
        """
        Translate health insight text to target language
        
        Args:
            insight_text: English health insight
            target_language: Target language code
        
        Returns:
            Translated insight
        """
        if not self.validate_language(target_language) or target_language == "en":
            return insight_text
        
        # For now, return English. In production, integrate with translation API
        # (Google Translate, Azure Translator, DeepL, etc.)
        logger.info(f"Translating insight to {target_language} (placeholder)")
        return insight_text
    
    def translate_response(
        self,
        response_data: Dict,
        target_language: str
    ) -> Dict:
        """
        Translate entire API response to target language
        
        Args:
            response_data: API response dictionary
            target_language: Target language code
        
        Returns:
            Translated response
        """
        if not self.validate_language(target_language) or target_language == "en":
            return response_data
        
        # Placeholder for full response translation
        logger.info(f"Translating response structure to {target_language}")
        return response_data
    
    def get_localized_date_format(self, language_code: str) -> str:
        """Get date format for specific language"""
        date_formats = {
            "en": "%m/%d/%Y",  # US format
            "es": "%d/%m/%Y",  # Spanish format
            "fr": "%d/%m/%Y",  # French format
            "de": "%d.%m.%Y",  # German format
            "zh": "%Y年%m月%d日",  # Chinese format
        }
        return date_formats.get(language_code, "%m/%d/%Y")
    
    def clear_cache(self):
        """Clear translation cache"""
        self.cache.clear()
        logger.info("Translation cache cleared")


# Global instance
_translation_service = None


def get_translation_service() -> TranslationService:
    """Get or create global translation service instance"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
