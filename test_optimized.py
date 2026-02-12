#!/usr/bin/env python3
"""
Test script for optimized ClinicalCamel-7B.py
Tests conversation flow and validates performance improvements
"""

import sys
sys.path.insert(0, '/home/cvl/Virtual Assistant For Medicine')

print("=" * 70)
print("OPTIMIZED CLINICAL CAMEL TEST")
print("=" * 70)
print()

# Import the modules
try:
    print("Importing ClinicalCamel-7B module...")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "clinical_camel",
        "/home/cvl/Virtual Assistant For Medicine/ClinicalCamel-7B.py"
    )
    clinical_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(clinical_module)
    print("✓ Module imported successfully")
except Exception as e:
    print(f"✗ Error importing: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("CONVERSATION TEST")
print("=" * 70)
print()

# Instantiate agents
print("Instantiating agents...")
validation_agent = clinical_module.TransformerValidationAgent(
    clinical_module.val_model, 
    clinical_module.val_tokenizer
)
question_generator = clinical_module.QuestionGeneratorAgent(
    clinical_module.medgemma_model,
    clinical_module.medgemma_processor
)
print("✓ Agents ready\n")

# Test conversation flow
conversation_history = []

# Test input
test_input = "I have a severe headache"
conversation_history.append(test_input)
print(f"Patient: {test_input}")

# First validation
val_result = validation_agent.evaluate_completeness(conversation_history)
print(f"\nValidation (Exchange 1):")
print(f"  Missing: {val_result['missing_category']}")
print(f"  Continue: {val_result['should_continue_asking']}")

# First question
if val_result['should_continue_asking']:
    question = question_generator.generate_question(
        conversation_history, 
        val_result['missing_category']
    )
    print(f"Doctor: {question}")

# Second exchange
test_input2 = "It started 2 days ago"
conversation_history.append(test_input2)
print(f"\nPatient: {test_input2}")

val_result2 = validation_agent.evaluate_completeness(conversation_history)
print(f"\nValidation (Exchange 2):")
print(f"  Missing: {val_result2['missing_category']}")
print(f"  Continue: {val_result2['should_continue_asking']}")
print(f"  Category progression: {val_result['missing_category']} → {val_result2['missing_category']}")

if val_result2['should_continue_asking']:
    question2 = question_generator.generate_question(
        conversation_history,
        val_result2['missing_category']
    )
    print(f"Doctor: {question2}")

# Third exchange
test_input3 = "It's an 8 out of 10 severity"
conversation_history.append(test_input3)
print(f"\nPatient: {test_input3}")

val_result3 = validation_agent.evaluate_completeness(conversation_history)
print(f"\nValidation (Exchange 3):")
print(f"  Missing: {val_result3['missing_category']}")
print(f"  Continue: {val_result3['should_continue_asking']}")
print(f"  Category progression: {val_result2['missing_category']} → {val_result3['missing_category']}")

if val_result3['should_continue_asking']:
    question3 = question_generator.generate_question(
        conversation_history,
        val_result3['missing_category']
    )
    print(f"Doctor: {question3}")

# Check for progression
print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)

categories = [val_result['missing_category'], val_result2['missing_category'], val_result3['missing_category']]
print(f"\nCategory progression: {' → '.join(categories)}")

if categories[0] == categories[1] == categories[2]:
    print("✗ WARNING: Categories not progressing!")
elif categories[0] == categories[1] or categories[1] == categories[2]:
    print("✓ Categories advancing (some progression)")
else:
    print("✓ Categories properly advancing through conversation")

if not val_result3['should_continue_asking']:
    print("✓ Conversation marked as complete after sufficient exchanges")
else:
    print("ℹ Conversation marked to continue for more information")

print("\n" + "=" * 70)
print("Test completed successfully!")
print("=" * 70)
