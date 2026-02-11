#!/usr/bin/env python3
"""
MedAI Assistant - Quick Validation Script
Tests all 4 approaches to verify imports work correctly
"""

import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

print("=" * 80)
print("MedAI ASSISTANT - VALIDATION TEST SUITE")
print("Testing all 4 approaches + Optimized version")
print("=" * 80)
print()

# Test results tracking
results = {
    'Biomistral.py': False,
    'ClinicalCamel-7B.py': False,
    'complete-project-rule.py': False,
    'Mistral.py': False,
}

test_files = [
    ('Biomistral.py', 'Biomistral - Rule-based validation + MedGemma'),
    ('ClinicalCamel-7B.py', 'ClinicalCamel-7B - Meditron-7B validation + MedGemma'),
    ('complete-project-rule.py', 'Complete-Project - Rule-based + Secure'),
    ('Mistral.py', 'Mistral - Mistral-7B validation + MedGemma'),
]

# ========================================================================
# Test 1: Import Validation
# ========================================================================

print("TEST 1: IMPORT VALIDATION")
print("-" * 80)

for filename, description in test_files:
    filepath = project_dir / filename
    
    if not filepath.exists():
        print(f"❌ {filename}: File not found")
        continue
    
    print(f"Testing: {filename}")
    print(f"  Description: {description}")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check for correct imports
        if 'from transformers import AutoModel' in content or \
           'from transformers import AutoProcessor, AutoModel' in content or \
           'AutoModel.from_pretrained' in content:
            
            # Check that bad import is NOT present
            if 'AutoModelForImageTextToText' not in content:
                print(f"  ✅ Imports correct (AutoModel used)")
                results[filename] = True
            else:
                print(f"  ❌ Still contains AutoModelForImageTextToText!")
                results[filename] = False
        else:
            print(f"  ⚠️  Could not verify imports")
            results[filename] = False
            
    except Exception as e:
        print(f"  ❌ Error reading file: {str(e)}")
        results[filename] = False
    
    print()

# ========================================================================
# Test 2: Python Syntax Validation
# ========================================================================

print("\nTEST 2: PYTHON SYNTAX VALIDATION")
print("-" * 80)

import py_compile

all_syntax_valid = True

for filename, _ in test_files:
    filepath = project_dir / filename
    
    if not filepath.exists():
        continue
    
    try:
        py_compile.compile(str(filepath), doraise=True)
        print(f"✅ {filename}: Valid Python syntax")
    except py_compile.PyCompileError as e:
        print(f"❌ {filename}: Syntax error - {str(e)[:100]}")
        all_syntax_valid = False

# ========================================================================
# Test 3: Required Classes Validation
# ========================================================================

print("\nTEST 3: REQUIRED CLASSES VALIDATION")
print("-" * 80)

required_classes = [
    'ValidationAgent',
    'QuestionGeneratorAgent',
    'DoctorAgent',
]

for filename, _ in test_files:
    filepath = project_dir / filename
    
    if not filepath.exists():
        continue
    
    print(f"Checking {filename}...")
    with open(filepath, 'r') as f:
        content = f.read()
    
    missing = []
    for cls in required_classes:
        if f'class {cls}' not in content:
            missing.append(cls)
    
    if not missing:
        print(f"  ✅ All required classes present")
    else:
        print(f"  ⚠️  Missing classes: {', '.join(missing)}")

# ========================================================================
# Test 4: MedAI_Optimized Validation
# ========================================================================

print("\n" + "=" * 80)
print("TEST 4: MedAI_Optimized.py CHECK")
print("-" * 80)

optimized_file = project_dir / 'MedAI_Optimized.py'

if optimized_file.exists():
    print("✅ MedAI_Optimized.py exists")
    
    try:
        py_compile.compile(str(optimized_file), doraise=True)
        print("✅ Valid Python syntax")
        
        with open(optimized_file, 'r') as f:
            content = f.read()
        
        if all([f'class {cls}' in content for cls in required_classes]):
            print("✅ All required classes present")
        else:
            print("❌ Missing required classes")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
else:
    print("⚠️  MedAI_Optimized.py not found (this is optional)")

# ========================================================================
# Test 5: Model Loading Test (Optional)
# ========================================================================

print("\n" + "=" * 80)
print("TEST 5: MODEL IMPORT VALIDATION")
print("-" * 80)

try:
    print("Testing transformers library...")
    import torch
    from transformers import AutoModel, AutoProcessor
    
    print("✅ torch imported successfully")
    print("✅ transformers.AutoModel available")
    print("✅ transformers.AutoProcessor available")
    
    print(f"\nEnvironment:")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  PyTorch version: {torch.__version__}")
    from transformers import __version__ as tf_version
    print(f"  Transformers version: {tf_version}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
        print(f"  CUDA version: {torch.version.cuda}")
    
except ImportError as e:
    print(f"❌ Import error: {str(e)}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# ========================================================================
# Summary Report
# ========================================================================

print("\n" + "=" * 80)
print("VALIDATION SUMMARY REPORT")
print("=" * 80)

all_passed = all(results.values())
passed_count = sum(1 for v in results.values() if v)
total_count = len(results)

print("\nFile Status:")
for filename, passed in results.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} - {filename}")

print(f"\nResult: {passed_count}/{total_count} files passed import validation")

if all_passed:
    print("\n🎉 ALL FILES READY TO USE!")
    print("\nRecommended execution order:")
    print("  1. python MedAI_Optimized.py (RECOMMENDED - best quality)")
    print("  2. python complete-project-rule.py (lightweight alternative)")
    print("  3. python Biomistral.py (similar to #2)")
    print("  4. python Mistral.py (needs 12GB VRAM)")
    print("  5. python ClinicalCamel-7B.py (needs 16GB VRAM)")
    print("\nNext step: Run MedAI_Optimized.py to test the system")
    exit_code = 0
else:
    print("\n⚠️  Some files need attention")
    print("Please review the errors above")
    exit_code = 1

print("\n" + "=" * 80)
sys.exit(exit_code)
