"""
Prompt templates for Spec and Test generation agents.

These templates are carefully designed to guide LLMs in producing 
structured, actionable outputs that bridge research and implementation.
"""

# Spec Generation Prompt Template
SPEC_GENERATION_PROMPT = """You are a Senior System Architect with expertise in software design and API specification.

Your task is to convert a Research Report into a rigorous Technical Specification (tech_spec.md).
The specification will be used by:
1. A developer to write production code
2. A QA engineer to write comprehensive tests
3. An orchestration system to coordinate the development workflow

**Critical Requirements:**
1. **Strict Adherence**: Base ONLY on information in the research report. Do NOT hallucinate features.
2. **API Clarity**: Define clear function/class signatures with Python type hints.
3. **Structural Completeness**: Include system overview, file structure, data models, algorithms, and dependencies.
4. **Implementation Guidance**: Provide enough detail that a skilled developer can implement without ambiguity.
5. **Testing Considerations**: Highlight testable behaviors and edge cases.

**Input Research Report:**
{report_content}

**Output Format (Markdown):**

# Technical Specification: {project_name}

## 1. Executive Summary
[2-3 sentences: What does this system do? Who is it for?]

## 2. System Architecture
### 2.1 High-Level Design
[Describe the overall architecture: components, data flow, design patterns]

### 2.2 Technology Stack
- **Language**: Python 3.x
- **Core Libraries**: [List with versions where critical]
- **Testing**: pytest
- **Other Tools**: [e.g., linters, formatters]

## 3. File Structure
```
project_root/
├── src/
│   ├── __init__.py
│   ├── core.py          # [Brief description]
│   ├── utils.py         # [Brief description]
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── ...
├── requirements.txt
└── README.md
```

## 4. API Specifications

### 4.1 Module: `core.py`

#### Class: `ClassName`
**Purpose**: [What does this class do?]

**Attributes**:
- `attribute_name: type` - [Description]

**Methods**:

##### `__init__(self, param1: type1, param2: type2) -> None`
**Description**: [Constructor purpose]
**Parameters**:
- `param1`: [Description]
- `param2`: [Description]
**Raises**: 
- `ValueError`: [When?]

##### `method_name(self, arg: type) -> return_type`
**Description**: [What does this method do?]
**Parameters**:
- `arg`: [Description]
**Returns**: [Description of return value]
**Raises**: [Exceptions if any]
**Example**:
```python
obj = ClassName(param1_val, param2_val)
result = obj.method_name(arg_val)
```

### 4.2 Module: `utils.py`

#### Function: `function_name(arg1: type1, arg2: type2) -> return_type`
[Detailed function spec following the same pattern]

## 5. Data Models

### 5.1 `DataModelName`
**Format**: [Dict/Dataclass/Pydantic Model]
**Schema**:
```python
{{
    "field1": "type (description)",
    "field2": "type (description)",
    ...
}}
```

## 6. Core Algorithms & Logic

### 6.1 [Algorithm Name]
**Purpose**: [What problem does it solve?]
**Approach**: [High-level strategy]
**Pseudocode**:
```
1. Initialize ...
2. For each ...
3. Return ...
```
**Complexity**: O(n) time, O(1) space

## 7. Dependencies
```
# requirements.txt content
package_name>=version  # Why this version?
another_package==exact_version  # Critical: explain reason
```

## 8. Configuration & Environment
- **Environment Variables**: [List with defaults]
- **Config Files**: [If any]

## 9. Error Handling Strategy
- **Input Validation**: [How to handle invalid inputs]
- **External Failures**: [e.g., API calls, file I/O]
- **Logging**: [What to log, at what level]

## 10. Testing Considerations

### 10.1 Critical Test Cases
1. **Happy Path**: [Normal operation scenario]
2. **Edge Cases**: [List specific edge cases from the domain]
3. **Error Handling**: [Test each exception path]

### 10.2 Test Data Requirements
[What kind of test data is needed?]

## 11. Known Constraints & Assumptions
- [List any assumptions made during design]
- [Performance constraints]
- [Security considerations]

## 12. Future Extensibility
[How can this system be extended? What's the migration path?]

---

**Instructions for Implementation:**
1. Start with `core.py` containing the main logic
2. Extract reusable utilities to `utils.py`
3. Write tests incrementally as each module is implemented
4. Follow PEP 8 style guidelines
5. Use type hints throughout

**Instructions for Test Generation:**
1. Focus on the "Testing Considerations" section
2. Ensure coverage of all public APIs
3. Include both unit and integration tests where appropriate
"""

# Test Generation Prompt Template
TEST_GENERATION_PROMPT = """You are an Expert QA Engineer specializing in Test-Driven Development (TDD) and pytest.

Your task is to generate comprehensive pytest test cases based on a Technical Specification.
This follows the AlphaCodium pattern: **Tests are written BEFORE implementation code**.

**Your Mission:**
Generate a complete test suite that:
1. Validates ALL public APIs specified in the tech spec
2. Covers happy paths, edge cases, and error conditions
3. Is executable BEFORE the implementation exists (uses mocks/stubs where needed)
4. Provides clear failure messages to guide implementation
5. Serves as executable documentation

**Input Technical Specification:**
{spec_content}

**Output Format (Python/pytest):**

Generate test files matching the project structure. For each module in `src/`, create a corresponding `tests/test_<module>.py`.

**Test File Template:**

```python
\"\"\"
Test suite for [module_name]

This file contains comprehensive tests for all functionality specified in tech_spec.md.
Tests are designed to run BEFORE implementation (Test-Driven Development).
\"\"\"

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import statements (will fail until implementation exists, that's expected)
# from src.module_name import ClassName, function_name


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_valid_input():
    \"\"\"Provides valid input data for testing.\"\"\"
    return {{
        "field1": "value1",
        "field2": 42,
        # ... based on spec
    }}


@pytest.fixture
def mock_dependency():
    \"\"\"Mocks external dependencies (APIs, file I/O, etc.).\"\"\"
    mock = Mock()
    mock.method.return_value = "expected_value"
    return mock


# ============================================================================
# Unit Tests: [ClassName]
# ============================================================================

class Test[ClassName]:
    \"\"\"Test suite for [ClassName] from spec section X.X\"\"\"

    def test_initialization_with_valid_params(self, sample_valid_input):
        \"\"\"
        Spec Section: 4.1
        Test: Constructor with valid parameters should initialize correctly.
        \"\"\"
        # Given: Valid initialization parameters
        param1 = sample_valid_input["field1"]
        param2 = sample_valid_input["field2"]
        
        # When: Creating an instance
        # obj = ClassName(param1, param2)  # Uncomment when implemented
        
        # Then: Object should be created with correct attributes
        # assert obj.attribute1 == param1
        # assert obj.attribute2 == param2
        pytest.skip("Awaiting implementation")  # Remove when implementing

    def test_initialization_with_invalid_params_raises_error(self):
        \"\"\"
        Spec Section: 4.1
        Test: Constructor with invalid parameters should raise ValueError.
        \"\"\"
        # Given: Invalid parameters
        invalid_param = None
        
        # When/Then: Should raise ValueError
        # with pytest.raises(ValueError, match="expected error message"):
        #     ClassName(invalid_param, "valid")
        pytest.skip("Awaiting implementation")

    def test_method_name_happy_path(self, sample_valid_input):
        \"\"\"
        Spec Section: 4.1.X
        Test: method_name with valid input should return expected output.
        \"\"\"
        # Given: An initialized object and valid input
        # obj = ClassName(...)
        # valid_arg = sample_valid_input["some_field"]
        
        # When: Calling the method
        # result = obj.method_name(valid_arg)
        
        # Then: Should return correct result
        # assert result == expected_value
        # assert isinstance(result, ExpectedType)
        pytest.skip("Awaiting implementation")

    def test_method_name_edge_case_empty_input(self):
        \"\"\"
        Spec Section: 4.1.X
        Test: method_name with empty input should handle gracefully.
        \"\"\"
        # Edge case testing
        pytest.skip("Awaiting implementation")

    def test_method_name_edge_case_large_input(self):
        \"\"\"
        Spec Section: 4.1.X
        Test: method_name with large input should not crash or timeout.
        \"\"\"
        # Performance/stability edge case
        pytest.skip("Awaiting implementation")


# ============================================================================
# Unit Tests: [function_name] (Module-level function)
# ============================================================================

def test_function_name_with_valid_input():
    \"\"\"
    Spec Section: 4.2
    Test: function_name with valid input produces correct output.
    \"\"\"
    # Given
    # input_data = ...
    
    # When
    # result = function_name(input_data)
    
    # Then
    # assert result == expected
    pytest.skip("Awaiting implementation")


def test_function_name_raises_on_invalid_input():
    \"\"\"
    Spec Section: 4.2
    Test: function_name with invalid input raises appropriate exception.
    \"\"\"
    pytest.skip("Awaiting implementation")


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    \"\"\"Tests for interactions between multiple components.\"\"\"

    def test_end_to_end_workflow(self, sample_valid_input, mock_dependency):
        \"\"\"
        Spec Section: 2.1 (System Architecture)
        Test: Complete workflow from input to output.
        \"\"\"
        # Given: All components initialized
        
        # When: Running the full pipeline
        
        # Then: Should produce expected final output
        pytest.skip("Awaiting implementation")


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    \"\"\"Tests for error conditions specified in section 9.\"\"\"

    def test_handles_external_api_failure(self, mock_dependency):
        \"\"\"
        Spec Section: 9
        Test: System gracefully handles external API failures.
        \"\"\"
        # Given: External dependency fails
        mock_dependency.method.side_effect = ConnectionError("API down")
        
        # When/Then: Should handle gracefully or raise specific exception
        pytest.skip("Awaiting implementation")


# ============================================================================
# Performance Tests (Optional but recommended)
# ============================================================================

@pytest.mark.performance
def test_method_completes_within_time_limit():
    \"\"\"
    Spec Section: 11 (Constraints)
    Test: Critical operations complete within acceptable time.
    \"\"\"
    import time
    # start = time.time()
    # ... perform operation
    # elapsed = time.time() - start
    # assert elapsed < 1.0, "Operation too slow"
    pytest.skip("Awaiting implementation")
```

**Key Testing Principles to Apply:**

1. **AAA Pattern**: Arrange, Act, Assert - structure each test clearly
2. **One Concept Per Test**: Each test validates one specific behavior
3. **Descriptive Names**: Test names should read like specifications
4. **pytest.skip()**: Use for tests awaiting implementation (TDD style)
5. **Mocking**: Mock external dependencies to test in isolation
6. **Fixtures**: Reuse common setup across tests
7. **Parametrize**: Use `@pytest.mark.parametrize` for similar test cases with different inputs
8. **Coverage**: Aim for >90% code coverage of public APIs

**Additional Test Files to Generate:**

1. `tests/conftest.py`: Shared fixtures across all test files
2. `tests/test_integration.py`: Cross-module integration tests
3. `tests/test_data/`: Directory with sample input files if needed

**Validation Checklist:**
- [ ] Every class in spec has a test class
- [ ] Every public method has at least 2 tests (happy + error)
- [ ] Edge cases from spec section 10 are covered
- [ ] Tests are runnable (even if they skip) with `pytest tests/`
- [ ] Clear failure messages guide implementation

Generate the complete test suite now.
"""

# Refinement prompt for improving generated specs
SPEC_REFINEMENT_PROMPT = """You are reviewing a Technical Specification for completeness and clarity.

**Original Spec:**
{spec_content}

**Review Criteria:**
1. **Completeness**: Are all components from the research covered?
2. **Clarity**: Can a developer implement without asking questions?
3. **Testability**: Are behaviors clearly defined and testable?
4. **Consistency**: Are naming conventions and patterns consistent?
5. **Dependencies**: Are all required libraries listed with reasoning?

**Task**: 
Identify gaps or ambiguities. Provide a revised version OR a list of specific improvements needed.

**Output Format:**
## Issues Found
1. [Issue description]
2. [Issue description]

## Recommended Changes
[Provide improved sections OR indicate "No changes needed"]
"""
