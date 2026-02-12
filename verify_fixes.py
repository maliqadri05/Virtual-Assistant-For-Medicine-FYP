#!/usr/bin/env python3
"""Quick verification script to check all fixes are in place"""

import os
import re
import sys

def check_file(filepath, checks):
    """Check if file contains expected patterns"""
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print('='*60)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    all_passed = True
    for check_name, pattern in checks:
        if re.search(pattern, content):
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    return all_passed

# Checks for ClinicalCamel-7B.py
clinical_checks = [
    ("Warning suppression imported", r"import warnings"),
    ("OS module imported", r"import os"),
    ("Logging module imported", r"import logging"),
    ("TRANSFORMERS_VERBOSITY set to error", r"os\.environ\['TRANSFORMERS_VERBOSITY'\]\s*=\s*'error'"),
    ("Logging configured for transformers", r"logging\.getLogger\('transformers'\)"),
    ("DoctorAgent uses val_model", r"def __init__\(self, val_model, val_tokenizer\):"),
    ("DoctorAgent initialization with Meditron", r"doctor_agent = DoctorAgent\(val_model, val_tokenizer\)"),
    ("Improved heuristic report with condition_keywords", r"condition_keywords = \{"),
    ("Comprehensive symptom mapping", r"indigestion\|stomach\|gastric"),
    ("No temperature in do_sample=False calls", r"do_sample=False[^t]*?pad_token_id"),
]

# Checks for Mistral.py
mistral_checks = [
    ("Warning suppression imported", r"import warnings"),
    ("OS module imported", r"import os"),
    ("Logging module imported", r"import logging"),
    ("TRANSFORMERS_VERBOSITY set to error", r"os\.environ\['TRANSFORMERS_VERBOSITY'\]\s*=\s*'error'"),
    ("Logging configured for transformers", r"logging\.getLogger\('transformers'\)"),
    ("DoctorAgent uses val_model", r"def __init__\(self, val_model, val_tokenizer\):"),
    ("DoctorAgent initialization with Meditron", r"doctor_agent = DoctorAgent\(val_model, val_tokenizer\)"),
    ("Improved heuristic report with condition_keywords", r"condition_keywords = \{"),
    ("No temperature in do_sample=False calls", r"do_sample=False[^t]*?pad_token_id"),
]

print("\n" + "="*60)
print("VERIFICATION OF FIXES")
print("="*60)

result1 = check_file('/home/cvl/Virtual Assistant For Medicine/ClinicalCamel-7B.py', clinical_checks)
result2 = check_file('/home/cvl/Virtual Assistant For Medicine/Mistral.py', mistral_checks)

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"ClinicalCamel-7B.py:  {'PASS ✅' if result1 else 'FAIL ❌'}")
print(f"Mistral.py:           {'PASS ✅' if result2 else 'FAIL ❌'}")
print("\n" + "="*60)

if result1 and result2:
    print("✅ ALL FIXES VERIFIED!")
    sys.exit(0)
else:
    print("❌ Some fixes are missing")
    sys.exit(1)
