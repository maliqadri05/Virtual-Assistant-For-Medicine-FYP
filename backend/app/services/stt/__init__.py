"""STT service public interface"""
from .speech_to_text import STTService, STTProvider, get_stt_service

__all__ = ["STTService", "STTProvider", "get_stt_service"]
