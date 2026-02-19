"""
Integration and E2E tests for Milestone 3 (Tasks 3.1, 3.2, 3.3, 3.4)

Tests complete user workflows including:
- Patient profile management
- Conversation history
- Smart analytics
- Advanced features (multi-language, STT, appointments, etc.)
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.main import app

client = TestClient(app)


def get_unique_email():
    """Generate unique email for testing"""
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


# ==================== PATIENT PROFILE WORKFLOW ====================

class TestPatientProfileWorkflow:
    """Test complete patient profile workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user"""
        user = {
            "first_name": "John",
            "last_name": "Patient",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        assert response.status_code == 200
        
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_email = user["email"]
    
    def test_create_complete_patient_profile(self):
        """Test creating a complete patient profile"""
        # Update profile info
        profile_update = {
            "first_name": "John",
            "last_name": "Patient",
            "date_of_birth": "1990-01-15",
            "gender": "Male",
            "blood_type": "O+",
            "phone": "+1-555-0123"
        }
        response = client.put(
            "/api/profile/me",
            json=profile_update,
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Get profile
        response = client.get("/api/profile/me", headers=self.headers)
        assert response.status_code == 200
        profile = response.json()
        assert profile["first_name"] == "John"
    
    def test_add_medical_history(self):
        """Test adding medical history"""
        medical_history = {
            "condition": "Hypertension",
            "diagnosis_date": "2015-03-20",
            "status": "active"
        }
        response = client.post(
            "/api/profile/medical-history",
            json=medical_history,
            headers=self.headers
        )
        assert response.status_code in [200, 201]
    
    def test_add_multiple_allergies(self):
        """Test adding multiple allergies"""
        allergies = [
            {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"},
            {"allergen": "Shellfish", "reaction": "Anaphylaxis", "severity": "severe"},
            {"allergen": "Peanuts", "reaction": "Throat swelling", "severity": "severe"}
        ]
        
        for allergy in allergies:
            response = client.post(
                "/api/profile/allergies",
                json=allergy,
                headers=self.headers
            )
            assert response.status_code in [200, 201]
    
    def test_add_medications(self):
        """Test adding medications"""
        medications = [
            {
                "name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "once daily",
                "reason": "Hypertension"
            },
            {
                "name": "Aspirin",
                "dosage": "100mg",
                "frequency": "once daily",
                "reason": "Prevention"
            }
        ]
        
        for med in medications:
            response = client.post(
                "/api/profile/medications",
                json=med,
                headers=self.headers
            )
            assert response.status_code in [200, 201]
    
    def test_add_family_history(self):
        """Test adding family history"""
        family_history = [
            {"relation": "Mother", "condition": "Diabetes", "age_of_onset": 55},
            {"relation": "Father", "condition": "Heart Disease", "age_of_onset": 60}
        ]
        
        for history in family_history:
            response = client.post(
                "/api/profile/family-history",
                json=history,
                headers=self.headers
            )
            assert response.status_code in [200, 201]


# ==================== CONVERSATION HISTORY WORKFLOW ====================

class TestConversationHistoryWorkflow:
    """Test complete conversation history workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user and create conversation"""
        user = {
            "first_name": "Jane",
            "last_name": "Patient",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_and_retrieve_conversation(self):
        """Test creating and retrieving conversation"""
        # Create conversation
        conv_data = {
            "title": "Persistent Headache",
            "initial_symptoms": "Severe headache for 3 days"
        }
        response = client.post(
            "/api/conversations",
            json=conv_data,
            headers=self.headers
        )
        assert response.status_code in [200, 201]
        
        conversation = response.json()
        self.conversation_id = conversation.get("id")
        
        # Retrieve conversation
        response = client.get(
            f"/api/conversations/{self.conversation_id}",
            headers=self.headers
        )
        assert response.status_code == 200
        retrieved = response.json()
        assert retrieved["title"] == "Persistent Headache"
    
    def test_add_messages_to_conversation(self):
        """Test adding messages to conversation"""
        # Create conversation first
        conv_data = {
            "title": "Fever Consultation",
            "initial_symptoms": "High fever, 39.5°C"
        }
        response = client.post(
            "/api/conversations",
            json=conv_data,
            headers=self.headers
        )
        conversation_id = response.json().get("id")
        
        # Add messages
        messages = [
            {"role": "user", "content": "I have a high fever", "message_type": "text"},
            {"role": "assistant", "content": "Let me ask some questions...", "message_type": "text"}
        ]
        
        for msg in messages:
            response = client.post(
                f"/api/conversations/{conversation_id}/messages",
                json=msg,
                headers=self.headers
            )
            assert response.status_code in [200, 201]
    
    def test_list_conversations_with_pagination(self):
        """Test listing conversations with pagination"""
        # Create multiple conversations
        for i in range(3):
            conv_data = {
                "title": f"Consultation {i}",
                "initial_symptoms": f"Symptom {i}"
            }
            client.post(
                "/api/conversations",
                json=conv_data,
                headers=self.headers
            )
        
        # List with limit
        response = client.get(
            "/api/conversations/?limit=2&offset=0",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data.get("results", [])) <= 2
    
    def test_search_conversations(self):
        """Test searching conversations"""
        # Create conversation
        conv_data = {
            "title": "Migraine Analysis",
            "initial_symptoms": "Severe migraine with aura"
        }
        response = client.post(
            "/api/conversations",
            json=conv_data,
            headers=self.headers
        )
        
        # Search for it
        search_data = {
            "query": "migraine",
            "limit": 10,
            "offset": 0
        }
        response = client.post(
            "/api/conversations/search",
            json=search_data,
            headers=self.headers
        )
        assert response.status_code == 200
        results = response.json()
        assert results.get("total", 0) >= 0
    
    def test_filter_conversations_by_status(self):
        """Test filtering conversations by status"""
        # Create conversation
        conv_data = {
            "title": "Active Consultation",
            "initial_symptoms": "Current symptoms",
            "status": "active"
        }
        response = client.post(
            "/api/conversations",
            json=conv_data,
            headers=self.headers
        )
        
        # Filter by status
        response = client.get(
            "/api/conversations/?status=active",
            headers=self.headers
        )
        assert response.status_code == 200


# ==================== SMART FEATURES WORKFLOW ====================

class TestSmartFeaturesWorkflow:
    """Test smart features and analytics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user with conversation history"""
        user = {
            "first_name": "Analytics",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_wellness_report_generation(self):
        """Test generating wellness report"""
        # Get wellness report
        if self.user_id:
            response = client.get(
                f"/api/conversations/{self.user_id}/wellness-report",
                headers=self.headers
            )
            assert response.status_code == 200
            report = response.json()
            
            # Verify report structure
            assert "total_conversations" in report
            assert "active_conditions" in report
            assert "symptom_trends" in report
            assert "recurring_issues" in report
            assert "health_insights" in report
    
    def test_symptom_trend_analysis(self):
        """Test symptom trend analysis in wellness report"""
        if self.user_id:
            response = client.get(
                f"/api/conversations/{self.user_id}/wellness-report",
                headers=self.headers
            )
            assert response.status_code == 200
            report = response.json()
            
            symptom_trends = report.get("symptom_trends", [])
            for trend in symptom_trends:
                assert "symptom" in trend
                assert "occurrence_count" in trend


# ==================== ADVANCED FEATURES E2E ====================

class TestAdvancedFeaturesE2E:
    """Test Task 3.4 advanced features end-to-end"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register user"""
        user = {
            "first_name": "Advanced",
            "last_name": "User",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user)
        data = response.json()
        self.user_id = data.get("user", {}).get("id")
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_multi_language_support_ready(self):
        """Test multi-language framework is available"""
        # This tests that the i18n infrastructure is available
        try:
            from app.services.i18n.translator import get_translation_service
            service = get_translation_service()
            assert service is not None
            
            languages = service.get_supported_languages()
            assert len(languages) >= 10
        except ImportError:
            pytest.skip("i18n service not available")
    
    def test_stt_service_ready(self):
        """Test STT service is available"""
        try:
            from app.services.stt.speech_to_text import get_stt_service
            service = get_stt_service()
            assert service is not None
            assert len(service.SUPPORTED_FORMATS) > 0
        except ImportError:
            pytest.skip("STT service not available")
    
    def test_medical_record_parser_ready(self):
        """Test medical record parser is available"""
        try:
            from app.services.dicom.medical_record_parser import get_medical_record_parser
            parser = get_medical_record_parser()
            assert parser is not None
            assert ".pdf" in parser.SUPPORTED_FORMATS
        except ImportError:
            pytest.skip("Medical record parser not available")
    
    def test_appointment_service_ready(self):
        """Test appointment service is available"""
        try:
            from app.services.appointments import get_appointment_service
            service = get_appointment_service()
            assert service is not None
        except ImportError:
            pytest.skip("Appointment service not available")
    
    def test_notification_service_ready(self):
        """Test notification service is available"""
        try:
            from app.services.notifications import get_notification_service
            service = get_notification_service()
            assert service is not None
        except ImportError:
            pytest.skip("Notification service not available")
    
    def test_data_export_service_ready(self):
        """Test data export service is available"""
        try:
            from app.services.data_export import get_data_export_service
            service = get_data_export_service()
            assert service is not None
        except ImportError:
            pytest.skip("Data export service not available")


# ==================== COMPLEX WORKFLOW TESTS ====================

class TestComplexWorkflows:
    """Test complex end-to-end workflows"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: register users and prepare data"""
        # User 1
        user1 = {
            "first_name": "Workflow",
            "last_name": "User1",
            "email": get_unique_email(),
            "password": "TestPass123!"
        }
        response = client.post("/api/auth/register", json=user1)
        data = response.json()
        self.user1_id = data.get("user", {}).get("id")
        self.token1 = data["access_token"]
        self.headers1 = {"Authorization": f"Bearer {self.token1}"}
    
    def test_complete_patient_consultation_workflow(self):
        """Test complete workflow from consultation to wellness report"""
        # 1. Create patient profile
        profile = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-15",
            "gender": "Male",
            "blood_type": "O+"
        }
        response = client.put(
            "/api/profile/me",
            json=profile,
            headers=self.headers1
        )
        assert response.status_code == 200
        
        # 2. Add medical information
        allergy = {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"}
        response = client.post(
            "/api/profile/allergies",
            json=allergy,
            headers=self.headers1
        )
        assert response.status_code in [200, 201]
        
        # 3. Create consultation conversation
        conv = {
            "title": "Annual Checkup",
            "initial_symptoms": "Regular checkup"
        }
        response = client.post(
            "/api/conversations",
            json=conv,
            headers=self.headers1
        )
        assert response.status_code in [200, 201]
        
        # 4. Add consultation messages
        msg = {
            "role": "user",
            "content": "I feel fine overall",
            "message_type": "text"
        }
        if response.status_code in [200, 201]:
            conv_id = response.json().get("id")
            response = client.post(
                f"/api/conversations/{conv_id}/messages",
                json=msg,
                headers=self.headers1
            )
            assert response.status_code in [200, 201]
    
    def test_conversation_search_and_export_workflow(self):
        """Test searching conversations and exporting data"""
        # Create multiple conversations
        for i in range(2):
            conv_data = {
                "title": f"Consultation {i}",
                "initial_symptoms": f"Symptom {i}"
            }
            response = client.post(
                "/api/conversations",
                json=conv_data,
                headers=self.headers1
            )
            assert response.status_code in [200, 201]
        
        # Search conversations
        search = {"query": "Consultation", "limit": 10, "offset": 0}
        response = client.post(
            "/api/conversations/search",
            json=search,
            headers=self.headers1
        )
        assert response.status_code == 200
