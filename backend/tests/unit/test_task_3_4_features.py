"""
Unit tests for Task 3.4 Advanced Features (Multi-language, STT, PDF parsing, etc.)

Tests cover:
- Multi-language support
- Speech-to-Text service
- Medical record parsing
- Appointment scheduling
- Notifications
- Data export
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import services
from app.services.i18n.translator import TranslationService, get_translation_service
from app.services.i18n.language_manager import LanguageManager
from app.services.stt.speech_to_text import STTService, STTProvider, get_stt_service
from app.services.dicom.medical_record_parser import MedicalRecordParser, get_medical_record_parser
from app.services.appointments import AppointmentService, get_appointment_service
from app.services.notifications import NotificationService, get_notification_service
from app.services.data_export import DataExportService, get_data_export_service


# ==================== MULTI-LANGUAGE TESTS ====================

class TestTranslationService:
    """Test translation service functionality"""
    
    def test_translation_service_initialization(self):
        """Test translation service initializes correctly"""
        service = get_translation_service()
        assert service is not None
        assert service.default_language == "en"
    
    def test_supported_languages(self):
        """Test get supported languages"""
        languages = TranslationService.get_supported_languages()
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "zh" in languages
        assert len(languages) >= 10
    
    def test_validate_language(self):
        """Test language validation"""
        service = get_translation_service()
        assert service.validate_language("en") == True
        assert service.validate_language("es") == True
        assert service.validate_language("invalid") == False
    
    def test_translate_medical_term(self):
        """Test translating medical terms"""
        service = get_translation_service()
        
        # Test English (identity translation)
        assert service.translate_term("headache", "en") == "headache"
        
        # Test Spanish translation
        spanish_headache = service.translate_term("headache", "es")
        assert spanish_headache == "dolor de cabeza"
        
        # Test French translation
        french_fever = service.translate_term("fever", "fr")
        assert french_fever == "fièvre"
        
        # Test Chinese translation
        chinese_cough = service.translate_term("cough", "zh")
        assert chinese_cough == "咳嗽"
    
    def test_translate_unknown_term_fallback(self):
        """Test fallback for unknown terms"""
        service = get_translation_service()
        unknown_term = service.translate_term("unknown_condition", "es")
        assert unknown_term == "unknown_condition"  # Fallback to original
    
    def test_translate_unsupported_language_fallback(self):
        """Test fallback for unsupported language"""
        service = get_translation_service()
        result = service.translate_term("headache", "invalid_lang")
        assert result == "headache"
    
    def test_localized_date_format(self):
        """Test date format localization"""
        service = get_translation_service()
        
        en_format = service.get_localized_date_format("en")
        assert en_format == "%m/%d/%Y"
        
        es_format = service.get_localized_date_format("es")
        assert es_format == "%d/%m/%Y"
        
        zh_format = service.get_localized_date_format("zh")
        assert "%Y" in zh_format and "%m" in zh_format


class TestLanguageManager:
    """Test language manager functionality"""
    
    def test_validate_language_code(self):
        """Test language code validation"""
        assert LanguageManager.validate_language_code("en") == True
        assert LanguageManager.validate_language_code("es") == True
        assert LanguageManager.validate_language_code("invalid") == False
    
    def test_detect_browser_language_from_header(self):
        """Test browser language detection from Accept-Language header"""
        # Test Spanish browser
        lang = LanguageManager.get_browser_language("es-ES,es;q=0.9,en;q=0.8")
        assert lang == "es"
        
        # Test English browser
        lang = LanguageManager.get_browser_language("en-US,en;q=0.9")
        assert lang == "en"
        
        # Test default when no header
        lang = LanguageManager.get_browser_language(None)
        assert lang == LanguageManager.DEFAULT_LANGUAGE


# ==================== STT TESTS ====================

class TestSpeechToTextService:
    """Test Speech-to-Text service"""
    
    def test_stt_service_initialization(self):
        """Test STT service initializes correctly"""
        service = get_stt_service()
        assert service is not None
        assert service.provider == STTProvider.WHISPER
    
    def test_supported_audio_formats(self):
        """Test supported audio formats"""
        service = get_stt_service()
        assert "wav" in service.SUPPORTED_FORMATS
        assert "mp3" in service.SUPPORTED_FORMATS
        assert "m4a" in service.SUPPORTED_FORMATS
        assert "ogg" in service.SUPPORTED_FORMATS
    
    def test_max_file_size(self):
        """Test maximum file size"""
        service = get_stt_service()
        assert service.MAX_FILE_SIZE == 25 * 1024 * 1024  # 25MB
    
    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self):
        """Test successful audio transcription"""
        service = get_stt_service()
        result = await service.transcribe_audio("test.wav", "en")
        
        assert result["success"] == True
        assert "text" in result
        assert result["provider"] == "whisper"
        assert result["language"] == "en"
    
    def test_validate_audio_file_success(self):
        """Test audio file validation"""
        service = get_stt_service()
        assert service._validate_audio_file("audio.wav") == True
        assert service._validate_audio_file("audio.mp3") == True
        assert service._validate_audio_file("audio.m4a") == True
    
    def test_validate_audio_file_invalid_format(self):
        """Test validation fails for unsupported format"""
        service = get_stt_service()
        assert service._validate_audio_file("document.txt") == False
        assert service._validate_audio_file("image.jpg") == False
    
    def test_supported_languages_for_transcription(self):
        """Test supported languages for transcription"""
        service = get_stt_service()
        languages = service.get_supported_languages()
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) >= 10


# ==================== MEDICAL RECORD PARSING TESTS ====================

class TestMedicalRecordParser:
    """Test medical record parsing"""
    
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        parser = get_medical_record_parser()
        assert parser is not None
    
    def test_supported_formats(self):
        """Test supported file formats"""
        parser = get_medical_record_parser()
        assert ".pdf" in parser.SUPPORTED_FORMATS
        assert ".txt" in parser.SUPPORTED_FORMATS
        assert ".json" in parser.SUPPORTED_FORMATS
    
    def test_parse_json_record(self):
        """Test parsing JSON medical record"""
        parser = get_medical_record_parser()
        
        # Create test JSON file
        test_data = {
            "patient_name": "John Doe",
            "date_of_birth": "1990-01-15",
            "medical_conditions": ["Hypertension"]
        }
        
        result = parser.parse_medical_record(
            "test_record.json",
            file_format="json"
        )
        
        assert result["success"] == True
        assert result["format"] == "json"
    
    def test_parse_pdf_record(self):
        """Test parsing PDF medical record (placeholder)"""
        parser = get_medical_record_parser()
        
        result = parser.parse_medical_record(
            "test_record.pdf",
            file_format="pdf"
        )
        
        assert result["success"] == True
        assert "patient_name" in result["data"]
        assert "medical_conditions" in result["data"]
    
    def test_extract_key_information(self):
        """Test extracting key information from parsed record"""
        parser = get_medical_record_parser()
        
        parsed_data = {
            "data": {
                "patient_name": "Jane Doe",
                "date_of_birth": "1985-05-20",
                "medical_conditions": ["Diabetes", "Asthma"],
                "medications": [
                    {"name": "Metformin", "dosage": "500mg"}
                ]
            }
        }
        
        extracted = parser.extract_key_information(parsed_data)
        
        assert extracted["patient_name"] == "Jane Doe"
        assert "Diabetes" in extracted["medical_conditions"]
        assert len(extracted["medications"]) == 1
    
    def test_validate_extraction(self):
        """Test validating extracted data"""
        parser = get_medical_record_parser()
        
        # Valid extraction
        valid_data = {
            "patient_name": "John Doe",
            "medical_conditions": ["Hypertension"]
        }
        assert parser.validate_extraction(valid_data) == True
        
        # Invalid extraction (missing patient_name)
        invalid_data = {
            "medical_conditions": ["Hypertension"]
        }
        assert parser.validate_extraction(invalid_data) == False


# ==================== APPOINTMENT TESTS ====================

class TestAppointmentService:
    """Test appointment scheduling service"""
    
    def test_appointment_service_initialization(self):
        """Test appointment service initializes correctly"""
        service = get_appointment_service()
        assert service is not None
    
    def test_schedule_appointment_success(self):
        """Test successful appointment scheduling"""
        service = get_appointment_service()
        
        tomorrow = datetime.utcnow() + timedelta(days=1)
        result = service.schedule_appointment(
            user_id="user_123",
            provider_name="Dr. Smith",
            appointment_date=tomorrow,
            appointment_type="telehealth"
        )
        
        assert result["success"] == True
        assert "appointment" in result
        assert "confirmation_code" in result["appointment"]
    
    def test_schedule_appointment_past_date_fails(self):
        """Test appointment in past fails"""
        service = get_appointment_service()
        
        past_date = datetime.utcnow() - timedelta(days=1)
        result = service.schedule_appointment(
            user_id="user_123",
            provider_name="Dr. Smith",
            appointment_date=past_date
        )
        
        assert result["success"] == False
        assert "must be in the future" in result["error"]
    
    def test_reschedule_appointment(self):
        """Test rescheduling appointment"""
        service = get_appointment_service()
        
        new_date = datetime.utcnow() + timedelta(days=2)
        result = service.reschedule_appointment(
            appointment_id="APT_123",
            new_date=new_date
        )
        
        assert result["success"] == True
        assert result["status"] == "rescheduled"
    
    def test_cancel_appointment(self):
        """Test cancelling appointment"""
        service = get_appointment_service()
        
        result = service.cancel_appointment(
            appointment_id="APT_123",
            reason="Patient requested cancellation"
        )
        
        assert result["success"] == True
        assert result["status"] == "cancelled"
    
    def test_get_available_slots(self):
        """Test getting available appointment slots"""
        service = get_appointment_service()
        
        start = datetime.utcnow().replace(hour=9, minute=0)
        end = datetime.utcnow().replace(hour=17, minute=0)
        
        slots = service.get_available_slots("Dr. Smith", start, end)
        
        assert len(slots) > 0
        assert all(slot["available"] for slot in slots)


# ==================== NOTIFICATION TESTS ====================

class TestNotificationService:
    """Test notification service"""
    
    def test_notification_service_initialization(self):
        """Test notification service initializes correctly"""
        service = get_notification_service()
        assert service is not None
    
    def test_send_notification_success(self):
        """Test sending notification successfully"""
        service = get_notification_service()
        
        result = service.send_notification(
            user_id="user_123",
            notification_type="appointment_reminder",
            message="Your appointment is tomorrow",
            channels=["email", "sms"]
        )
        
        assert result["success"] == True
        assert "notification_id" in result
        assert "email" in result["channels_used"]
    
    def test_send_appointment_reminder(self):
        """Test sending appointment reminder"""
        service = get_notification_service()
        
        appointment_date = datetime.utcnow() + timedelta(days=1)
        result = service.send_appointment_reminder(
            user_id="user_123",
            appointment_date=appointment_date,
            provider_name="Dr. Smith"
        )
        
        assert result["success"] == True
    
    def test_send_health_alert(self):
        """Test sending health alert"""
        service = get_notification_service()
        
        result = service.send_health_alert(
            user_id="user_123",
            alert_title="High Blood Pressure",
            alert_message="Your BP reading is elevated"
        )
        
        assert result["success"] == True
    
    def test_send_follow_up_reminder(self):
        """Test sending follow-up reminder"""
        service = get_notification_service()
        
        due_date = datetime.utcnow() + timedelta(days=3)
        result = service.send_follow_up_reminder(
            user_id="user_123",
            follow_up_task="Schedule lab work",
            due_date=due_date
        )
        
        assert result["success"] == True


# ==================== DATA EXPORT TESTS ====================

class TestDataExportService:
    """Test data export service"""
    
    def test_export_service_initialization(self):
        """Test export service initializes correctly"""
        service = get_data_export_service()
        assert service is not None
    
    def test_export_json_format(self):
        """Test exporting as JSON"""
        service = get_data_export_service()
        
        test_data = {
            "patient_name": "John Doe",
            "age": 35,
            "conditions": ["Hypertension"]
        }
        
        result = service.export_patient_data(
            user_id="user_123",
            export_data=test_data,
            format="json"
        )
        
        assert result["success"] == True
        assert result["format"] == "json"
        assert "data" in result
        assert ".json" in result["filename"]
    
    def test_export_csv_format(self):
        """Test exporting as CSV"""
        service = get_data_export_service()
        
        test_data = {
            "conversations": [
                {"id": "1", "title": "Check-up", "status": "completed"},
                {"id": "2", "title": "Follow-up", "status": "active"}
            ]
        }
        
        result = service.export_patient_data(
            user_id="user_123",
            export_data=test_data,
            format="csv"
        )
        
        assert result["success"] == True
        assert result["format"] == "csv"
        assert ".csv" in result["filename"]
    
    def test_export_xml_format(self):
        """Test exporting as XML"""
        service = get_data_export_service()
        
        test_data = {
            "patient_name": "John Doe",
            "age": 35
        }
        
        result = service.export_patient_data(
            user_id="user_123",
            export_data=test_data,
            format="xml"
        )
        
        assert result["success"] == True
        assert result["format"] == "xml"
        assert "<?xml" in result.get("data", "")
    
    def test_export_conversation_history(self):
        """Test exporting conversation history"""
        service = get_data_export_service()
        
        conversations = [
            {"id": "1", "title": "Headache", "status": "completed"},
            {"id": "2", "title": "Fever", "status": "active"}
        ]
        
        result = service.export_conversation_history(
            user_id="user_123",
            conversations=conversations,
            format="json"
        )
        
        assert result["success"] == True
        assert "conversations_user_123" in result["filename"]
    
    def test_export_medical_record(self):
        """Test exporting medical record"""
        service = get_data_export_service()
        
        medical_data = {
            "conditions": ["Hypertension", "Diabetes"],
            "medications": ["Lisinopril", "Metformin"],
            "allergies": ["Penicillin"]
        }
        
        result = service.export_patient_data(
            user_id="user_123",
            export_data=medical_data,
            format="json"
        )
        
        assert result["success"] == True
    
    def test_unsupported_export_format(self):
        """Test unsupported export format"""
        service = get_data_export_service()
        
        result = service.export_patient_data(
            user_id="user_123",
            export_data={"test": "data"},
            format="invalid"
        )
        
        assert result["success"] == False
        assert "Unsupported" in result["error"]
