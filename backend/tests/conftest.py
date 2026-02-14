"""
Pytest Configuration and Shared Fixtures
Provides reusable test data and fixtures for all tests
"""

import pytest
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# ===== MEDICAL DATA FIXTURES =====

@pytest.fixture
def headache_conversation() -> List[str]:
    """Complete headache case conversation"""
    return [
        "I have a severe headache",
        "It started 3 days ago after a fall",
        "I'm 35 years old",
        "Female",
        "Weight 65kg",
        "The pain is sharp, located at the temple",
        "I'm experiencing dizziness and nausea",
        "I'm sensitive to bright light",
        "I tried ibuprofen but it didn't help",
        "No previous head injuries",
        "Not taking any regular medications",
        "Allergic to Penicillin",
        "I work at a computer 8 hours daily"
    ]


@pytest.fixture
def chest_pain_conversation() -> List[str]:
    """Complete chest pain case conversation"""
    return [
        "I'm experiencing chest pain",
        "Sharp pain on the left side",
        "Started 2 hours ago after climbing stairs",
        "I'm 52 years old",
        "Male",
        "Weigh 85kg",
        "I have high blood pressure",
        "Taking Lisinopril 10mg daily",
        "No other medications",
        "Allergic to Penicillin",
        "Pain is 7/10 severity",
        "Gets worse with deep breathing",
        "Haven't had this before",
        "I'm overweight",
        "Smoke occasionally"
    ]


@pytest.fixture
def fever_conversation() -> List[str]:
    """Complete fever case conversation"""
    return [
        "I have a high fever",
        "Temperature is 39.5°C",
        "Started yesterday morning",
        "Also have body aches",
        "I'm 28 years old",
        "Female",
        "Weight 62kg",
        "Started with a sore throat",
        "I have a persistent cough",
        "I'm fatigued",
        "Not taking any medications",
        "No known drug allergies",
        "No chronic conditions",
        "This is my first time having such a high fever"
    ]


@pytest.fixture
def respiratory_symptoms_conversation() -> List[str]:
    """Complete respiratory case conversation"""
    return [
        "I'm having difficulty breathing",
        "Shortness of breath for 3 days",
        "I'm 45 years old",
        "Male",
        "Weight 78kg",
        "Chronic smoker, 20+ years",
        "I have a chronic cough",
        "Producing yellowish phlegm",
        "No previous lung disease diagnosis",
        "Not taking any medications",
        "No allergies",
        "Symptoms worse when lying down",
        "I get tired climbing stairs"
    ]


@pytest.fixture
def patient_context_1() -> Dict[str, Any]:
    """Sample patient context 1"""
    return {
        "name": "Jane Doe",
        "age": 35,
        "sex": "Female",
        "weight": 65.0,
        "medical_history": "None significant",
        "medications": None,
        "allergies": "Penicillin"
    }


@pytest.fixture
def patient_context_2() -> Dict[str, Any]:
    """Sample patient context 2 - high risk"""
    return {
        "name": "John Smith",
        "age": 62,
        "sex": "Male",
        "weight": 95.0,
        "medical_history": "Hypertension, Type 2 Diabetes, Obesity",
        "medications": "Lisinopril 10mg, Metformin 1000mg",
        "allergies": "Penicillin, ACE Inhibitors"
    }


@pytest.fixture
def patient_context_3() -> Dict[str, Any]:
    """Sample patient context 3 - young"""
    return {
        "name": "Emily Wilson",
        "age": 24,
        "sex": "Female",
        "weight": 58.0,
        "medical_history": "Asthma",
        "medications": "Albuterol inhaler as needed",
        "allergies": "Sulfamethoxazole"
    }


# ===== CONVERSATION SCENARIOS =====

@dataclass
class ConversationScenario:
    """Complete test scenario"""
    name: str
    conversation: List[str]
    patient_context: Dict[str, Any]
    expected_keywords: List[str]
    requires_specialist: bool = False


@pytest.fixture
def headache_scenario(headache_conversation, patient_context_1) -> ConversationScenario:
    """Headache scenario"""
    return ConversationScenario(
        name="Post-traumatic Headache",
        conversation=headache_conversation,
        patient_context=patient_context_1,
        expected_keywords=["headache", "dizziness", "nausea", "trauma", "neuro"],
        requires_specialist=False
    )


@pytest.fixture
def cardiac_scenario(chest_pain_conversation, patient_context_2) -> ConversationScenario:
    """Cardiac scenario"""
    return ConversationScenario(
        name="Chest Pain - Cardiac Risk",
        conversation=chest_pain_conversation,
        patient_context=patient_context_2,
        expected_keywords=["chest", "pain", "cardiac", "heart", "cardiologist"],
        requires_specialist=True
    )


@pytest.fixture
def respiratory_scenario(respiratory_symptoms_conversation, patient_context_3) -> ConversationScenario:
    """Respiratory scenario"""
    return ConversationScenario(
        name="Respiratory Distress",
        conversation=respiratory_symptoms_conversation,
        patient_context=patient_context_3,
        expected_keywords=["breathing", "respiratory", "lung", "pulmonary"],
        requires_specialist=True
    )


# ===== MOCK AGENTS/SERVICES =====

class MockModelService:
    """Mock AI model service for testing without actual models"""
    
    def __init__(self):
        self.call_count = 0
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate mock response"""
        self.call_count += 1
        return f"Mock response to prompt (call #{self.call_count})"
    
    def validate(self, text: str) -> Dict[str, Any]:
        """Mock validation"""
        return {
            "is_valid": True,
            "confidence": 0.95,
            "reasoning": "Mock validation passed"
        }


@pytest.fixture
def mock_model_service() -> MockModelService:
    """Provide mock model service"""
    return MockModelService()


# ===== PYTEST CONFIGURATION =====

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", 
        "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )


# ===== TEST REPORTING =====

@pytest.fixture(autouse=True)
def test_summary(request):
    """Print test summary"""
    yield
    # Print after each test
    print(f"\n{'='*60}")
    print(f"Test: {request.node.name}")
    print(f"{'='*60}")


# ===== PARAMETRIZED FIXTURES =====

@pytest.fixture(params=[
    ("John", 45, "Male"),
    ("Jane", 35, "Female"),
    ("Bob", 72, "Male")
])
def different_patients(request):
    """Parametrized patient demographics"""
    name, age, sex = request.param
    return {
        "name": name,
        "age": age,
        "sex": sex,
        "weight": 70,
        "medical_history": None,
        "medications": None,
        "allergies": None
    }


# ===== UTILITY FUNCTIONS =====

def get_test_data_dir() -> Path:
    """Get path to test data directory"""
    return Path(__file__).parent / "data"


def create_mock_conversation(symptoms: List[str], duration: str = "3 days") -> List[str]:
    """Create mock conversation from symptoms"""
    conversation = []
    
    # Add main symptom
    if symptoms:
        conversation.append(f"I have {symptoms[0]}")
        conversation.append(f"It's been going on for {duration}")
    
    # Add secondary symptoms
    for symptom in symptoms[1:]:
        conversation.append(f"I also have {symptom}")
    
    # Add basic demographics
    conversation.extend([
        "I'm 40 years old",
        "Male",
        "Weight 75kg",
        "No medications",
        "No allergies"
    ])
    
    return conversation
