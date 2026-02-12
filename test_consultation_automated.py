#!/usr/bin/env python3
"""
Test script for medical consultation with automatic input
"""

import sys
import subprocess
from unittest.mock import patch

# Test inputs
test_inputs = [
    "I have a headache and fever",
    "Started 3 days ago",
    "9 out of 10, very severe",
    "Also have a cough",
    "No medications, no allergies",
    "No previous medical issues"
]

# Create input stream
input_stream = "\n".join(test_inputs) + "\n"

print("=" * 80)
print("AUTOMATED MEDICAL CONSULTATION TEST")
print("=" * 80)
print()
print("Running test with inputs:")
for i, inp in enumerate(test_inputs, 1):
    print(f"  {i}. {inp}")
print()

# Run the consultation with piped input
process = subprocess.Popen(
    [sys.executable, "/home/cvl/Virtual Assistant For Medicine/ClinicalCamel-7B.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="/home/cvl/Virtual Assistant For Medicine"
)

stdout, stderr = process.communicate(input=input_stream, timeout=300)

print("=" * 80)
print("OUTPUT")
print("=" * 80)
print(stdout)

if stderr:
    print("\n" + "=" * 80)
    print("STDERR (Warnings/Errors)")
    print("=" * 80)
    # Filter out only important errors
    important_errors = [line for line in stderr.split('\n') 
                       if 'error' in line.lower() and 'Generate' not in line and 'temperature' not in line]
    if important_errors:
        print("\n".join(important_errors[:10]))
    else:
        print("(No critical errors - only non-critical warnings)")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
