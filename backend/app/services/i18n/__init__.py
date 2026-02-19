"""
Multi-language internationalization (i18n) service

Provides language support for 10+ languages with fallback to English.
"""

from .translator import TranslationService
from .language_manager import LanguageManager

__all__ = ["TranslationService", "LanguageManager"]
