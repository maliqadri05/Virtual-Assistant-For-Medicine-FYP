#!/usr/bin/env python3
"""
Simple unit test for validation agent logic
Tests the rule-based progression without model inference
"""

print("=" * 70)
print("VALIDATION AGENT LOGIC TEST (NO MODEL INFERENCE)")
print("=" * 70)
print()

# Simulate the validation logic
class MockValidationAgent:
    def __init__(self):
        self.last_category = None
    
    def evaluate_completeness_logic(self, num_exchanges):
        """Test the rule-based progression logic"""
        
        # Rule-based progression
        progression = {
            1: "symptom details", 
            2: "symptom details",
            3: "duration and severity", 
            4: "duration and severity",
            5: "medical history", 
            6: "medical history", 
            7: "none"
        }
        missing = progression.get(num_exchanges, "none")
        
        # Force progression if stuck
        if missing == self.last_category and num_exchanges > 2:
            categories = ["symptom details", "duration and severity", "medical history", "none"]
            idx = categories.index(missing) if missing in categories else 0
            missing = categories[min(idx + 1, len(categories) - 1)]
        
        self.last_category = missing
        
        return {
            "should_continue_asking": missing != "none",
            "missing_category": missing,
            "reasoning": "Using rule-based progression logic."
        }

# Create agent
agent = MockValidationAgent()

print("Testing category progression:")
print("-" * 70)

# Simulate 8 exchanges
test_exchanges = [
    "I have a severe headache",
    "It started 2 days ago",
    "It's an 8 out of 10 severity",
    "No other specific symptoms",
    "I don't currently take any medications",
    "No previous history of migraines",
    "I've been stressed at work",
    "That's all I can describe"
]

results = []
for i, exchange in enumerate(test_exchanges, 1):
    val_result = agent.evaluate_completeness_logic(i)
    results.append(val_result)
    
    print(f"\nExchange {i}: {exchange[:50]}...")
    print(f"  Missing category: {val_result['missing_category']}")
    print(f"  Should continue: {val_result['should_continue_asking']}")

# Analysis
print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

categories = [r['missing_category'] for r in results]
print(f"\nProgression: {' → '.join(categories)}")

# Check progression quality
progression_changes = sum(1 for i in range(len(categories)-1) if categories[i] != categories[i+1])
print(f"Number of category changes: {progression_changes}")

# Validate expected progression
expected_progression = [
    "symptom details",      # 1
    "symptom details",      # 2
    "duration and severity", # 3
    "duration and severity", # 4
    "medical history",       # 5
    "medical history",       # 6
    "none",                  # 7
    "none"                   # 8
]

matches = sum(1 for i, (got, exp) in enumerate(zip(categories, expected_progression)) if got == exp)
print(f"Matches expected progression: {matches}/{len(expected_progression)}")

if matches == len(expected_progression):
    print("\n✓ PASS: Categories progress correctly through conversation")
else:
    print("\n✗ FAIL: Categories don't match expected progression")
    print("\nExpected:", expected_progression)
    print("Got:     ", categories)

# Check completion
if results[-1]['should_continue_asking'] == False:
    print("✓ PASS: Conversation marked as complete after sufficient exchanges")
else:
    print("✗ FAIL: Conversation should be marked complete")

print("\n" + "=" * 70)
print("Test completed!")
print("=" * 70)
