"""
Language manager for handling user language preferences

Stores and retrieves user language preferences from database.
"""

from typing import Optional
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LanguageManager:
    """Manages user language preferences"""
    
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = {"en", "es", "fr", "zh", "ja", "de", "pt", "ar", "hi", "it"}
    
    @staticmethod
    def get_user_language(user_id: str, db: Session) -> str:
        """
        Get user's preferred language
        
        Args:
            user_id: User ID
            db: Database session
        
        Returns:
            Language code (default: 'en')
        """
        try:
            # Import here to avoid circular dependency
            from app.models.patient import User
            
            user = db.query(User).filter(User.id == user_id).first()
            if user and hasattr(user, 'preferred_language'):
                language = user.preferred_language
                if language in LanguageManager.SUPPORTED_LANGUAGES:
                    return language
            
            return LanguageManager.DEFAULT_LANGUAGE
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return LanguageManager.DEFAULT_LANGUAGE
    
    @staticmethod
    def set_user_language(user_id: str, language_code: str, db: Session) -> bool:
        """
        Set user's preferred language
        
        Args:
            user_id: User ID
            language_code: Language code (e.g., 'es', 'fr')
            db: Database session
        
        Returns:
            True if successful
        """
        try:
            if language_code not in LanguageManager.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language: {language_code}")
                return False
            
            # Import here to avoid circular dependency
            from app.models.patient import User
            
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if hasattr(user, 'preferred_language'):
                    user.preferred_language = language_code
                    db.commit()
                    logger.info(f"Set language for user {user_id} to {language_code}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    @staticmethod
    def validate_language_code(language_code: str) -> bool:
        """Validate language code"""
        return language_code in LanguageManager.SUPPORTED_LANGUAGES
    
    @staticmethod
    def get_browser_language(accept_language_header: Optional[str]) -> str:
        """
        Detect language from Accept-Language header
        
        Args:
            accept_language_header: HTTP Accept-Language header value
        
        Returns:
            Language code or default
        """
        if not accept_language_header:
            return LanguageManager.DEFAULT_LANGUAGE
        
        try:
            # Parse Accept-Language header: "es-ES,es;q=0.9,en;q=0.8"
            languages = accept_language_header.split(',')[0].split('-')[0].lower()
            if languages in LanguageManager.SUPPORTED_LANGUAGES:
                return languages
        except Exception as e:
            logger.debug(f"Error parsing Accept-Language header: {e}")
        
        return LanguageManager.DEFAULT_LANGUAGE
