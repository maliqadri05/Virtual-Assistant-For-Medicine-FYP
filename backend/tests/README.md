# 🧪 Testing Guide - Quick Start

This directory contains comprehensive tests for the MedAI Assistant agents and report generation system.

## 📁 Test Structure

```
tests/
├── unit/
│   └── agents/
│       ├── test_validation_agent.py    # Validation logic tests
│       └── test_doctor_agent.py        # Report generation tests
├── integration/
│   └── test_agent_manager_workflow.py  # End-to-end workflow tests
├── conftest.py                        # Shared fixtures & utilities
└── pytest.ini                         # Pytest configuration
```

---

## ⚡ Quick Start

### 1. Install Testing Dependencies

```bash
# From project root
pip install -r requirements-dev.txt
```

### 2. Run Tests

```bash
# Make script executable
chmod +x run_tests.sh

# Run all tests with coverage
./run_tests.sh

# Run specific test suite
./run_tests.sh doctor         # Report generation tests
./run_tests.sh validation     # Validation logic tests
./run_tests.sh manager        # Workflow tests
./run_tests.sh coverage       # Generate HTML coverage report
```

---

## 🎯 What Each Test Suite Tests

### ✅ Validation Agent Tests (`test_validation_agent.py`)

Tests the hybrid validation system that determines if enough information has been gathered:

- **Insufficient Information Detection**: Detects when user provides too little info
- **Information Gathering**: Recognizes when more info is still needed
- **Complete Information**: Identifies when ready for report generation
- **Edge Cases**: Handles duplicates, irrelevant info, medical jargon
- **Confidence Scoring**: Validates accuracy of confidence levels

**Run with:**
```bash
./run_tests.sh validation -v -s
```

### ✅ Doctor Agent Tests (`test_doctor_agent.py`)

Tests medical report generation quality and structure:

- **Report Structure**: Verifies proper formatting and sections
- **Content Quality**: Checks inclusion of patient info, symptoms, analysis
- **Clinical Recommendations**: Validates suggestions for follow-up
- **Context Integration**: Tests use of patient history, medications, allergies
- **Error Handling**: Tests graceful failure on edge cases
- **Consistency**: Verifies repeatable output quality

**Run with:**
```bash
./run_tests.sh doctor -v -s
```

### ✅ Agent Manager Tests (`test_agent_manager_workflow.py`)

Tests the complete multi-turn conversation workflow:

- **Single Turn**: First message handling
- **Multi-Turn Flows**: Complete conversations from symptom to report
- **Information Gathering**: Progressive conversation patterns
- **Context Awareness**: Patient context incorporation
- **Medical Scenarios**: Cardiac, respiratory, allergic reactions
- **Error Handling**: Invalid/empty/special character messages

**Run with:**
```bash
./run_tests.sh manager -v -s
```

---

## 📊 Understanding Test Output

### Successful Test Run
```
backend/tests/unit/agents/test_doctor_agent.py::TestDoctorAgentReportGeneration::test_report_generation_succeeds PASSED ✓
✓ Report generated: 1245 characters

===== 45 passed in 3.21s =====
```

### Test with Detailed Output
```
./run_tests.sh doctor -v -s

Turn 1 - Agent: validation_agent
  Response: Based on your symptoms, I need to gather more information...

Turn 2 - Agent: question_agent  
  Response: Can you tell me when the pain started?

Turn 3 - Agent: doctor_report_generator
  Response: ## Medical Assessment Report
  [Full report content]

✓ Report generated after 3 turns
```

---

## 🔍 Key Test Scenarios

### 1. Headache Case
- **Input**: User describes severe post-traumatic headache
- **Expected**: Report generated with neurological assessment
- **Validates**: Complete information detection + report quality

### 2. Chest Pain Case
- **Input**: User with cardiac risk factors describing chest pain
- **Expected**: Report with cardiac recommendations
- **Validates**: High-risk case handling

### 3. Respiratory Issues
- **Input**: Chronic smoker with breathing difficulty
- **Expected**: Report with pulmonary assessment
- **Validates**: Chronic condition handling

---

## 📈 Coverage Report

Generate detailed code coverage:

```bash
./run_tests.sh coverage
```

This will:
1. Run all tests
2. Generate HTML coverage report
3. Open report in browser

**View coverage for specific modules:**
```bash
pytest tests/ --cov=app.agents --cov-report=term-missing
```

---

## 🐛 Debugging Failed Tests

### Option 1: Run with Verbose Output
```bash
./run_tests.sh doctor -v -s
```

### Option 2: Run Specific Test
```bash
pytest tests/unit/agents/test_doctor_agent.py::TestDoctorAgentReportGeneration::test_report_generation_succeeds -v -s
```

### Option 3: Debug with Breakpoints
```bash
./run_tests.sh debug
# Drops into pdb debugger on failures
```

### Option 4: Show Print Statements
```bash
pytest tests/unit/agents/test_doctor_agent.py -s
# -s flag shows print() output
```

---

## ⚠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'app'"
**Solution:**
```bash
# Make sure you're in the backend directory
cd backend
pytest tests/

# Or run from project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest backend/tests/
```

### Issue: "No module named 'pytest'"
**Solution:**
```bash
pip install -r requirements-dev.txt
```

### Issue: Tests run but don't show output
**Solution:** Add `-s` flag:
```bash
pytest tests/unit/agents/test_doctor_agent.py -v -s
```

### Issue: Model service errors
**Tests mock the model service**, so no GPU required. If you see model service errors:
1. Check that `model_service=None` in test fixtures
2. Tests should use mock implementations

---

## 📝 Writing New Tests

### Template for New Test File

```python
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.your_agent import YourAgent

class TestYourAgent:
    @pytest.fixture
    def agent(self):
        return YourAgent(model_service=None)
    
    def test_basic_functionality(self, agent):
        """Test that agent does X"""
        result = agent.process(["input data"])
        
        assert "expected_field" in result
        assert len(result["content"]) > 0
        print(f"✓ Test passed")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

### Run Your New Tests
```bash
pytest backend/tests/unit/agents/test_your_agent.py -v -s
```

---

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements-dev.txt
      - run: cd backend && pytest tests/ --cov=app
```

---

## 📊 Test Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: >60% coverage  
- **Critical Paths**: 100% coverage
  - Validation logic
  - Report generation
  - Error handling

**Current Coverage:**
```bash
./run_tests.sh coverage
# View htmlcov/index.html
```

---

## 🎓 Best Practices

✅ **DO:**
- Write tests for new features
- Use fixtures for test data reusability
- Mock external services (AI models)
- Test edge cases and errors
- Use descriptive test names
- Add print() statements for debugging (with `-s` flag)

❌ **DON'T:**
- Test actual API calls without mocking
- Mix test concerns (unit vs integration)
- Make tests dependent on each other
- Skip error condition tests
- Leave failing tests unresolved

---

## 📞 Troubleshooting

For issues or questions:
1. Check test output with `-v -s` flags
2. Review test file comments and docstrings
3. Check [TESTING_GUIDE.md](../TESTING_GUIDE.md) for detailed guidance
4. Run `./run_tests.sh help` for script options

---

## 🎯 Next Steps

1. **Run tests locally**: `./run_tests.sh all`
2. **Check coverage**: `./run_tests.sh coverage`
3. **Fix any failures**: `./run_tests.sh doctor -v -s`
4. **Add new tests** for features you develop
5. **Monitor coverage** with each change

Happy testing! 🚀
