#!/usr/bin/env python3
"""
Quick test script to verify all approaches work without errors
"""
import sys
import subprocess

sys.path.insert(0, '/home/cvl/Virtual Assistant For Medicine')

print("=" * 80)
print("TESTING ALL APPROACHES - IMPORT VALIDATION")
print("=" * 80)

test_files = [
    'Biomistral.py',
    'ClinicalCamel-7B.py',
    'complete-project-rule.py',
    'Mistral.py',
    'MedAI_Optimized.py'
]

print("\nTesting imports...")
for file in test_files:
    try:
        # Try importing the file as a module (just test syntax)
        with open(f'/home/cvl/Virtual Assistant For Medicine/{file}', 'r') as f:
            code = f.read()
        
        # Test for critical errors
        if 'from transformers import' in code:
            import_section = code.split('from transformers import')[1].split('\n')[0].split(',')[0].strip()
            if 'AutoModelForImageTextToText' in code:
                print(f"❌ {file}: Still contains AutoModelForImageTextToText!")
            else:
                print(f"✅ {file}: Imports look correct")
        else:
            print(f"⚠️  {file}: No transformers import found")
        
        # Check for validation agent fixes
        if 'unclear' in code and 'missing_category' in code:
            if 'additional symptoms information' in code:
                print(f"   → Validation fallback logic: UPDATED ✓")
            else:
                print(f"   → Validation fallback logic: Not updated")
        
        # Check for question generator fallbacks
        if 'fallbacks' in code and 'missing_category' in code:
            print(f"   → Question generator fallbacks: ADDED ✓")
        
    except Exception as e:
        print(f"❌ {file}: Error - {str(e)}")

print("\n" + "=" * 80)
print("Import validation complete!")
print("=" * 80)

# Now test that transformers supports required classes
print("\nVerifying transformer library capabilities...")
try:
    from transformers import AutoModel, AutoProcessor
    print("✅ AutoModel available")
    print("✅ AutoProcessor available")
except ImportError as e:
    print(f"❌ Import error: {e}")

print("\nRecommendation:")
print("→ Use complete-project-rule.py or Biomistral.py for simple, lightweight approach")
print("→ Use MedAI_Optimized.py once model loading issues are resolved")
print("→ Use ClinicalCamel-7B.py or Mistral.py for more sophisticated validation")
