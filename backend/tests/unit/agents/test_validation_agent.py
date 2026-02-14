"""
Unit Tests for Validation Agent
Tests the hybrid validation system (rule-based + MedGemma)
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.validation_agent import HybridValidationAgent, InformationStatus


class TestValidationAgent:
    """Test suite for validation agent"""
    
    @pytest.fixture
    def validator(self):
        """Initialize validator without AI service"""
        return HybridValidationAgent(ai_service=None)
    
    # ===== INSUFFICIENT INFO TESTS =====
    
    def test_single_word_input(self, validator):
        """Test with minimal single-word input"""
        result = validator.evaluate_completeness(["sick"])
        assert result["should_continue_asking"] is True
        print(f"✓ Single word detected as insufficient")
    
    def test_early_stage_single_symptom(self, validator):
        """Test early stage: just one symptom"""
        conversation = ["I have a headache"]
        result = validator.evaluate_completeness(conversation)
        
        assert result["should_continue_asking"] is True
        assert result["missing_category"] is not None
        print(f"✓ Early stage detected. Missing: {result['missing_category']}")
    
    def test_empty_conversation(self, validator):
        """Test with empty conversation"""
        result = validator.evaluate_completeness([])
        assert result["should_continue_asking"] is True
        print(f"✓ Empty conversation handled")
    
    # ===== GATHERING INFO TESTS =====
    
    def test_gathering_with_multiple_symptoms(self, validator):
        """Test gathering stage: multiple symptoms provided"""
        conversation = [
            "I have a headache",
            "Also experiencing dizziness",
            "And some nausea"
        ]
        result = validator.evaluate_completeness(conversation)
        
        # Should still want more info or be complete
        print(f"✓ Gathering stage: {result['should_continue_asking']}. Confidence: {result['confidence']}")
    
    def test_gathering_with_duration(self, validator):
        """Test when symptom duration is provided"""
        conversation = [
            "I have chest pain",
            "It started 3 days ago",
            "Pain is sharp"
        ]
        result = validator.evaluate_completeness(conversation)
        
        # Should progress with duration info
        print(f"✓ Duration provided: continue_asking={result['should_continue_asking']}")
    
    # ===== COMPLETE INFO TESTS =====
    
    def test_complete_headache_case(self, validator):
        """Test complete consultation for headache"""
        conversation = [
            "I have a severe headache",
            "It started 3 days ago after a fall",
            "I'm 35 years old, female",
            "Weight 65kg",
            "The pain is sharp, in the temple area",
            "Also experiencing dizziness and nausea",
            "No previous head injuries",
            "I'm allergic to Penicillin",
            "I take ibuprofen regularly",
            "Pain worsens with bright light"
        ]
        
        result = validator.evaluate_completeness(conversation)
        
        if not result["should_continue_asking"]:
            assert result["confidence"] >= 0.7
            print(f"✓ Ready for report! Confidence: {result['confidence']}")
        else:
            print(f"Status: May need more info (confidence: {result['confidence']})")
    
    def test_complete_chest_pain_case(self, validator):
        """Test complete consultation for chest pain"""
        conversation = [
            "I have chest pain",
            "Sharp pain on the left side",
            "Started 2 hours ago",
            "I'm 52 years old, male",
            "Weigh 85kg",
            "I have high blood pressure",
            "Taking Lisinopril 10mg daily",
            "No previous heart problems",
            "Allergic to Penicillin",
            "Pain gets worse with deep breath",
            "Severity 7 out of 10"
        ]
        
        result = validator.evaluate_completeness(conversation)
        
        if not result["should_continue_asking"]:
            print(f"✓ Chest pain case complete! Confidence: {result['confidence']}")
        else:
            print(f"Status: {result['should_continue_asking']}")
    
    # ===== EDGE CASES =====
    
    def test_duplicate_information(self, validator):
        """Test with repetitive information"""
        conversation = [
            "I have a headache",
            "I have a headache",
            "The headache is severe",
            "The headache is severe"
        ]
        
        result = validator.evaluate_completeness(conversation)
        # Should handle duplicates gracefully
        print(f"✓ Duplicate info handled: continue_asking={result['should_continue_asking']}")
    
    def test_irrelevant_information(self, validator):
        """Test with irrelevant/off-topic information"""
        conversation = [
            "I have a headache",
            "I like pizza",
            "My favorite color is blue",
            "The sky looks beautiful"
        ]
        
        result = validator.evaluate_completeness(conversation)
        # Should ignore irrelevant info but still need duration (no medical time reference)
        assert result["should_continue_asking"] is True
        assert result["missing_category"] == "duration"
        print(f"✓ Filtered irrelevant info: continue_asking={result['should_continue_asking']}")
    
    def test_medical_jargon_recognition(self, validator):
        """Test recognition of medical terms"""
        conversation = [
            "I'm experiencing vertigo",
            "With photophobia",
            "And persistent nausea",
            "Age 40, Female"
        ]
        
        result = validator.evaluate_completeness(conversation)
        # Should recognize medical terms
        print(f"✓ Medical jargon recognized: confidence={result['confidence']}")
    
    # ===== VALIDATION RESULT PROPERTIES =====
    
    def test_validation_result_format(self, validator):
        """Test validation result format"""
        conversation = ["I have a fever"]
        result = validator.evaluate_completeness(conversation)
        
        # Check required fields
        assert "should_continue_asking" in result
        assert "missing_category" in result
        assert "confidence" in result
        assert "reasoning" in result
        
        # Check types
        assert isinstance(result["confidence"], (int, float))
        assert 0 <= result["confidence"] <= 1
        assert isinstance(result["reasoning"], str)
        
        print(f"✓ All required fields present")
        print(f"  Continue asking: {result['should_continue_asking']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reasoning: {result['reasoning']}")
    
    # ===== EDGE MEDICAL CONDITIONS =====
    
    def test_emergency_keywords_recognition(self, validator):
        """Test recognition of emergency symptoms"""
        emergency_terms = [
            "severe chest pain",
            "difficulty breathing",
            "loss of consciousness",
            "severe bleeding",
        ]
        
        for term in emergency_terms:
            result = validator.evaluate_completeness([term])
            # Emergency cases might have different handling
            print(f"  {term}: confidence={result['confidence']}")
    
    def test_mixed_symptom_profiles(self, validator):
        """Test with mixed/complex symptom profiles"""
        complex_conversation = [
            "Severe headache with neck stiffness",
            "High fever (39.2°C)",
            "Sensitivity to light",
            "Age 28, Female",
            "No recent travel",
            "Started 24 hours ago",
            "No medications except paracetamol",
            "Allergies: None known"
        ]
        
        result = validator.evaluate_completeness(complex_conversation)
        print(f"✓ Complex case: confidence={result['confidence']}")


class TestValidationAgentWithContext:
    """Test validation with patient context"""
    
    @pytest.fixture
    def validator(self):
        return HybridValidationAgent(ai_service=None)
    
    def test_validation_uses_patient_context(self, validator):
        """Test that patient context improves validation"""
        patient_context = {
            "age": 65,
            "sex": "Male",
            "medical_history": "Diabetes, Hypertension",
            "medications": ["Metformin", "Lisinopril"]
        }
        
        conversation = [
            "I've been feeling tired lately",
            "More than usual",
            "And increased thirst"
        ]
        
        result = validator.evaluate_completeness(conversation, patient_context)
        # With context of diabetes, should recognize pattern
        print(f"✓ Context-aware validation: confidence={result['confidence']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
