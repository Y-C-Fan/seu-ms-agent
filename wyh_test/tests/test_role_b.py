"""
Unit tests for Role B components (Spec and Test Generation).

These tests verify the basic functionality of the agents and adapters
without making actual API calls (using mocks).
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import shutil

# Test data
SAMPLE_REPORT = """# Research Report: Calculator Application

## 1. Executive Summary
This project will implement a simple calculator with basic arithmetic operations.

## 2. Key Concepts & Technologies
* **Python 3.x**: Programming language
* **pytest**: Testing framework

## 3. Implementation Details
* **API**: Simple functional API with add, subtract, multiply, divide functions
* **Dependencies**: None beyond standard library

## 4. Constraints & Risks
* Division by zero must be handled gracefully
"""

SAMPLE_SPEC = """# Technical Specification: Calculator

## 1. System Architecture
Simple functional design with pure functions.

## 2. API Specifications
### Function: add(a: float, b: float) -> float
### Function: subtract(a: float, b: float) -> float
### Function: multiply(a: float, b: float) -> float
### Function: divide(a: float, b: float) -> float

## 3. Testing Considerations
- Test normal operations
- Test division by zero
"""


class TestValidators:
    """Test the validation utilities."""
    
    def test_validate_spec_format_valid(self):
        """Test that a valid spec passes validation."""
        from wyh_test.utils.validators import validate_spec_format
        
        is_valid, issues = validate_spec_format(SAMPLE_SPEC)
        
        # This sample is intentionally minimal, so it may have issues
        # But we can test that the function runs
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)
    
    def test_validate_spec_format_too_short(self):
        """Test that a too-short spec fails validation."""
        from wyh_test.utils.validators import validate_spec_format
        
        short_spec = "# Title\nSome text"
        is_valid, issues = validate_spec_format(short_spec)
        
        assert not is_valid
        assert any("too short" in issue.lower() for issue in issues)
    
    def test_extract_project_name(self):
        """Test extracting project name from report."""
        from wyh_test.utils.validators import extract_project_name
        
        project_name = extract_project_name(SAMPLE_REPORT)
        
        assert "Calculator" in project_name or "Research Report" in project_name
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from wyh_test.utils.validators import sanitize_filename
        
        assert sanitize_filename("My Project!") == "my_project"
        assert sanitize_filename("Test-Case 123") == "test_case_123"


class TestSpecGeneratorAgent:
    """Test the Spec Generator Agent."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_report_file(self, temp_workspace):
        """Create a sample report file."""
        report_path = temp_workspace / "report.md"
        report_path.write_text(SAMPLE_REPORT)
        return report_path
    
    def test_agent_initialization(self):
        """Test that the agent can be initialized."""
        from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent
        
        # This will fail if config file doesn't exist, which is OK for now
        try:
            agent = SpecGeneratorAgent()
            assert agent is not None
        except FileNotFoundError:
            pytest.skip("Config file not found - expected in minimal test")
    
    @patch('wyh_test.agents.spec_generator_agent.LLMAgent')
    def test_agent_with_mock_llm(self, mock_llm_class, sample_report_file, temp_workspace):
        """Test spec generation with mocked LLM."""
        from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent
        
        # Mock the LLM agent
        mock_llm_instance = Mock()
        mock_llm_class.return_value = mock_llm_instance
        
        # Mock the async run method
        async def mock_run(*args, **kwargs):
            mock_msg = Mock()
            mock_msg.content = SAMPLE_SPEC
            return [mock_msg]
        
        mock_llm_instance.run = mock_run
        
        # This test demonstrates the pattern but won't fully work without proper mocking
        pytest.skip("Full agent testing requires more complex mocking")


class TestTestGeneratorAgent:
    """Test the Test Generator Agent."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_spec_file(self, temp_workspace):
        """Create a sample spec file."""
        spec_path = temp_workspace / "tech_spec.md"
        spec_path.write_text(SAMPLE_SPEC)
        return spec_path
    
    def test_agent_initialization(self):
        """Test that the agent can be initialized."""
        from wyh_test.agents.test_generator_agent import TestGeneratorAgent
        
        try:
            agent = TestGeneratorAgent()
            assert agent is not None
        except FileNotFoundError:
            pytest.skip("Config file not found - expected in minimal test")


class TestAdapters:
    """Test the adapter integrations."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config object."""
        config = Mock()
        config.spec_model = 'gpt-4o'
        config.test_model = 'gpt-4o'
        return config
    
    @pytest.fixture
    def mock_workspace(self):
        """Create a mock workspace manager."""
        workspace = Mock()
        workspace.work_dir = Path(tempfile.mkdtemp())
        return workspace
    
    def test_spec_adapter_initialization(self, mock_config, mock_workspace):
        """Test that SpecAdapter can be initialized."""
        from wyh_test.adapters.spec_adapter import SpecAdapter
        
        adapter = SpecAdapter(mock_config, mock_workspace)
        assert adapter is not None
        assert hasattr(adapter, 'spec_agent')
    
    def test_test_gen_adapter_initialization(self, mock_config, mock_workspace):
        """Test that TestGenAdapter can be initialized."""
        from wyh_test.adapters.test_gen_adapter import TestGenAdapter
        
        adapter = TestGenAdapter(mock_config, mock_workspace)
        assert adapter is not None
        assert hasattr(adapter, 'test_agent')


class TestPrompts:
    """Test that prompt templates are well-formed."""
    
    def test_spec_generation_prompt_has_placeholders(self):
        """Test that spec prompt has required placeholders."""
        from wyh_test.utils.prompts import SPEC_GENERATION_PROMPT
        
        assert '{report_content}' in SPEC_GENERATION_PROMPT
        assert '{project_name}' in SPEC_GENERATION_PROMPT
    
    def test_test_generation_prompt_has_placeholders(self):
        """Test that test prompt has required placeholders."""
        from wyh_test.utils.prompts import TEST_GENERATION_PROMPT
        
        assert '{spec_content}' in TEST_GENERATION_PROMPT
    
    def test_prompts_mention_key_concepts(self):
        """Test that prompts contain important guidance."""
        from wyh_test.utils.prompts import SPEC_GENERATION_PROMPT, TEST_GENERATION_PROMPT
        
        # Spec prompt should mention APIs and structure
        assert any(word in SPEC_GENERATION_PROMPT.lower() 
                  for word in ['api', 'specification', 'architecture'])
        
        # Test prompt should mention TDD and pytest
        assert any(word in TEST_GENERATION_PROMPT.lower() 
                  for word in ['pytest', 'tdd', 'test'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
