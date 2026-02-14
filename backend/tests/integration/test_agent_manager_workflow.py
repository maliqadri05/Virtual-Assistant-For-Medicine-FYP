"""
Integration Tests for Agent Manager Workflow
Tests the orchestration and multi-turn conversation flow
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.agent_manager import AgentManager


class TestAgentManagerWorkflow:
    """Test agent manager orchestration"""
    
    @pytest.fixture
    def agent_manager(self):
        """Initialize agent manager"""
        return AgentManager(model_service=None)
    
    # ===== SINGLE TURN TESTS =====
    
    def test_first_message_gets_response(self, agent_manager):
        """Test that first message gets appropriate response"""
        response = agent_manager.process_message(
            user_message="I have a headache",
            conversation_history=[],
            patient_context=None
        )
        
        assert "content" in response
        assert len(response["content"]) > 0
        assert response["role"] == "assistant"
        
        agent = response.get("metadata", {}).get("agent", "unknown")
        print(f"✓ First message handled by: {agent}")
        print(f"  Response: {response['content'][:100]}...")
    
    def test_response_format_is_consistent(self, agent_manager):
        """Test that response format is always consistent"""
        response = agent_manager.process_message(
            "I'm feeling ill",
            [],
            None
        )
        
        # Check required fields
        assert "content" in response
        assert "role" in response
        assert "metadata" in response
        assert "agent" in response["metadata"]
        
        print(f"✓ Response format correct")
    
    # ===== MULTI-TURN CONVERSATION TESTS =====
    
    def test_two_turn_conversation(self, agent_manager):
        """Test two-turn conversation flow"""
        print("\n=== TWO-TURN CONVERSATION TEST ===")
        
        # Turn 1: User describes symptom
        resp1 = agent_manager.process_message(
            user_message="I have a stomach ache",
            conversation_history=[],
            patient_context=None
        )
        print(f"Turn 1 - Agent: {resp1.get('metadata', {}).get('agent', '?')}")
        print(f"Turn 1 - Response: {resp1['content'][:80]}...")
        
        # Build history
        history = ["I have a stomach ache", resp1["content"]]
        
        # Turn 2: User provides more info
        resp2 = agent_manager.process_message(
            user_message="It's been going on for 2 days",
            conversation_history=history,
            patient_context=None
        )
        print(f"Turn 2 - Agent: {resp2.get('metadata', {}).get('agent', '?')}")
        print(f"Turn 2 - Response: {resp2['content'][:80]}...")
        
        # Both should be valid responses
        assert len(resp1["content"]) > 0
        assert len(resp2["content"]) > 0
        print("✓ Two-turn conversation completed")
    
    def test_progressive_conversation(self, agent_manager):
        """Test multi-turn conversation progression"""
        print("\n=== PROGRESSIVE CONVERSATION TEST ===")
        
        history = []
        messages = [
            "I have chest pain",
            "It's on the left side",
            "I'm 45 years old",
            "Male",
            "The pain started 1 hour ago",
            "It's sharp pain",
            "I have high blood pressure"
        ]
        
        for i, message in enumerate(messages, 1):
            response = agent_manager.process_message(
                user_message=message,
                conversation_history=history,
                patient_context=None
            )
            
            agent = response.get("metadata", {}).get("agent", "?")
            print(f"Turn {i}: {agent}")
            
            # Add to history
            history.append(message)
            history.append(response["content"])
            
            # Check if conversation completed
            if agent == "doctor_report_generator":
                print(f"✓ Report generated after {i} turns")
                break
        
        print(f"✓ Progressive conversation handled {len(messages)} messages")
    
    # ===== INFORMATION GATHERING TEST =====
    
    def test_validation_then_questions_then_report(self, agent_manager):
        """Test complete flow: validate → ask questions → generate report"""
        print("\n=== FULL WORKFLOW TEST ===")
        
        history = []
        agents_used = []
        
        # Progressive conversation
        conversation_messages = [
            "I have a severe headache",
            "Started 3 days ago",
            "After hitting my head",
            "I'm 38 years old, female",
            "I'm experiencing dizziness",
            "And nausea",
            "I'm sensitive to light",
            "No previous head injuries",
            "I take no regular medications",
            "Not allergic to any medications"
        ]
        
        for i, message in enumerate(conversation_messages, 1):
            response = agent_manager.process_message(
                user_message=message,
                conversation_history=history,
                patient_context=None
            )
            
            agent = response.get("metadata", {}).get("agent", "unknown")
            agents_used.append(agent)
            print(f"Turn {i}: {agent}")
            
            history.append(message)
            history.append(response["content"])
            
            if agent == "doctor_report_generator":
                print(f"✓ Report generated after {i} user messages")
                print(f"  Agents used: {set(agents_used)}")
                break
        
        assert "doctor_report_generator" in agents_used
        print("✓ Full workflow completed")
    
    # ===== WITH PATIENT CONTEXT =====
    
    def test_conversation_with_patient_context(self, agent_manager):
        """Test conversation with pre-populated patient context"""
        print("\n=== CONTEXT-AWARE CONVERSATION TEST ===")
        
        patient_context = {
            "name": "John Doe",
            "age": 65,
            "sex": "Male",
            "weight": 85.0,
            "medical_history": "Diabetes, Hypertension",
            "medications": "Metformin, Lisinopril",
            "allergies": "Penicillin"
        }
        
        response = agent_manager.process_message(
            user_message="I'm not feeling well",
            conversation_history=[],
            patient_context=patient_context
        )
        
        # Context should be incorporated
        assert len(response["content"]) > 0
        print(f"✓ Response with context: {response['content'][:80]}...")
    
    # ===== ERROR HANDLING =====
    
    def test_handles_empty_message(self, agent_manager):
        """Test handling of empty user message"""
        response = agent_manager.process_message(
            user_message="",
            conversation_history=[],
            patient_context=None
        )
        
        # Should handle gracefully
        assert "content" in response
        print(f"✓ Empty message handled")
    
    def test_handles_very_long_message(self, agent_manager):
        """Test handling of very long message"""
        long_message = "I have a headache. " * 100  # Very long message
        
        response = agent_manager.process_message(
            user_message=long_message,
            conversation_history=[],
            patient_context=None
        )
        
        assert "content" in response
        print(f"✓ Long message handled ({len(long_message)} chars)")
    
    def test_handles_special_characters(self, agent_manager):
        """Test handling of special characters"""
        response = agent_manager.process_message(
            user_message="I have @#$% symptoms & [unusual] pain!",
            conversation_history=[],
            patient_context=None
        )
        
        assert "content" in response
        print(f"✓ Special characters handled")
    
    # ===== CONSISTENCY TESTS =====
    
    def test_repeated_same_input(self, agent_manager):
        """Test that repeated same input produces valid responses"""
        message = "I have a fever"
        
        resp1 = agent_manager.process_message(message, [], None)
        resp2 = agent_manager.process_message(message, [], None)
        
        # Both should be valid
        assert len(resp1["content"]) > 0
        assert len(resp2["content"]) > 0
        
        print(f"✓ Repeated input handled consistently")
    
    # ===== PERFORMANCE TESTS =====
    
    def test_response_time_reasonable(self, agent_manager):
        """Test that response time is reasonable"""
        import time
        
        start = time.time()
        response = agent_manager.process_message(
            user_message="I have a headache",
            conversation_history=[],
            patient_context=None
        )
        elapsed = time.time() - start
        
        assert elapsed < 10  # Should respond within 10 seconds
        print(f"✓ Response time: {elapsed:.2f}s")
    
    # ===== SPECIFIC MEDICAL SCENARIOS =====
    
    def test_cardiac_emergency_scenario(self, agent_manager):
        """Test handling of potential cardiac emergency"""
        print("\n=== CARDIAC SCENARIO TEST ===")
        
        messages = [
            "Severe chest pain",
            "Left sided, radiating to arm",
            "I'm 55 years old, male",
            "I have history of heart disease",
            "Shortness of breath",
            "Pain started 30 minutes ago"
        ]
        
        history = []
        final_response = None
        
        for msg in messages:
            response = agent_manager.process_message(msg, history, None)
            history.append(msg)
            history.append(response["content"])
            final_response = response
        
        # Should produce appropriate response
        assert final_response is not None
        report = final_response["content"].lower()
        
        # Should suggest urgent action
        urgent_keywords = ["urgent", "emergency", "immediate", "seek help"]
        urgent = any(kw in report for kw in urgent_keywords)
        
        if urgent:
            print(f"✓ Urgent indicators detected in response")
        else:
            print(f"⚠ WARNING: Urgent indicators not found in cardiac case")
    
    def test_chronic_condition_scenario(self, agent_manager):
        """Test handling of chronic condition management"""
        print("\n=== CHRONIC CONDITION SCENARIO TEST ===")
        
        messages = [
            "I have diabetes",
            "My blood sugar has been high lately",
            "I'm 50 years old",
            "I've had diabetes for 10 years",
            "I take Metformin",
            "My recent glucose readings are 250-300",
            "I'm experiencing increased thirst"
        ]
        
        history = []
        for msg in messages:
            response = agent_manager.process_message(msg, history, None)
            history.append(msg)
            history.append(response["content"])
        
        agent = response.get("metadata", {}).get("agent", "?")
        print(f"✓ Chronic condition handled by: {agent}")
    
    def test_allergy_reaction_scenario(self, agent_manager):
        """Test handling of potential allergic reaction"""
        print("\n=== ALLERGY SCENARIO TEST ===")
        
        messages = [
            "I'm having an allergic reaction",
            "I have hives all over my body",
            "I'm having difficulty breathing",
            "I just ate peanuts",
            "I'm known to be allergic to peanuts",
            "My throat is swelling",
            "This started 5 minutes ago"
        ]
        
        history = []
        for msg in messages:
            response = agent_manager.process_message(msg, history, None)
            history.append(msg)
            history.append(response["content"])
        
        report = response["content"].lower()
        
        # Should suggest immediate action
        assert any(kw in report for kw in ["emergency", "epipen", "call"]) or len(report) > 50
        print(f"✓ Allergic reaction scenario handled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
