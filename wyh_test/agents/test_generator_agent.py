"""
Test Generator Agent

This agent generates comprehensive pytest test suites from technical specifications.
It follows the AlphaCodium pattern: tests are written BEFORE implementation code.

Key Responsibilities:
- Parse technical specifications
- Identify all testable components (classes, functions, APIs)
- Generate comprehensive test cases (happy path, edge cases, errors)
- Create test fixtures and conftest.py
- Ensure tests are TDD-ready (can run before implementation)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from omegaconf import DictConfig, OmegaConf

from ms_agent.agent.llm_agent import LLMAgent
from ms_agent.llm.utils import Message
from ms_agent.utils.logger import logger

from wyh_test.utils.prompts import TEST_GENERATION_PROMPT
from wyh_test.utils.validators import (
    validate_test_format,
    extract_code_blocks
)


class TestGeneratorAgent:
    """
    Agent for generating pytest test suites from technical specifications.
    
    This agent wraps an LLMAgent and provides a high-level interface
    for test generation following TDD best practices.
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Test Generator Agent.
        
        Args:
            config_path: Path to agent configuration YAML file
            model: Override model name (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')
            api_key: Override API key
            **kwargs: Additional configuration overrides
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "test_agent.yaml"
        
        self.config = self._load_config(config_path, model, api_key, **kwargs)
        
        # Initialize the underlying LLM agent
        self.agent = LLMAgent(
            config=self.config,
            tag="TestGenerator",
            trust_remote_code=False
        )
        
        # Configuration parameters
        self.max_attempts = self.config.get('retry', {}).get('max_attempts', 3)
        self.validate_output = self.config.get('output', {}).get('validation', {}).get('enabled', True)
        
        logger.info(f"TestGeneratorAgent initialized with model: {self.config.llm.model}")
    
    def _load_config(
        self,
        config_path: Path,
        model: Optional[str],
        api_key: Optional[str],
        **kwargs
    ) -> DictConfig:
        """Load and merge configuration from file and overrides."""
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        config = OmegaConf.load(config_path)
        
        # Apply overrides
        if model:
            config.llm.model = model
        
        if api_key:
            config.llm.api_key = api_key
        elif 'OPENAI_API_KEY' in os.environ:
            config.llm.api_key = os.environ['OPENAI_API_KEY']
        
        # Apply any additional kwargs
        for key, value in kwargs.items():
            OmegaConf.update(config, key, value, merge=True)
        
        return config
    
    async def generate_tests(
        self,
        spec_path: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, any]:
        """
        Generate pytest test suite from a technical specification.
        
        Args:
            spec_path: Path to the technical specification (tech_spec.md)
            output_dir: Directory where tests should be saved (default: spec_path.parent / "tests")
            
        Returns:
            Dict containing:
                - tests_dir: Path to tests directory
                - test_files: List of generated test file paths
                - is_valid: Whether validation passed
                - validation_issues: Dict mapping file to issues
                - attempts: Number of generation attempts made
        """
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        
        # Read the spec
        spec_content = spec_path.read_text(encoding='utf-8')
        
        # Determine output directory
        if output_dir is None:
            output_dir = spec_path.parent / "tests"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating tests from spec: {spec_path}")
        logger.info(f"Tests will be saved to: {output_dir}")
        
        # Generate tests with retry logic
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"Generation attempt {attempt}/{self.max_attempts}")
            
            try:
                test_content = await self._generate_test_content(
                    spec_content,
                    attempt
                )
                
                # Extract and save test files
                test_files = self._extract_and_save_tests(
                    test_content,
                    output_dir
                )
                
                # Validate if enabled
                if self.validate_output:
                    all_valid = True
                    validation_issues = {}
                    
                    for test_file in test_files:
                        is_valid, issues = validate_test_format(
                            test_file.read_text(encoding='utf-8'),
                            test_file
                        )
                        
                        if not is_valid:
                            all_valid = False
                            validation_issues[test_file.name] = issues
                    
                    if not all_valid:
                        logger.warning(f"Validation failed on attempt {attempt}: {validation_issues}")
                        
                        if attempt < self.max_attempts:
                            logger.info("Retrying with validation feedback...")
                            continue
                        else:
                            logger.error("Max attempts reached. Saving potentially incomplete tests.")
                    else:
                        logger.info("All tests passed validation!")
                else:
                    all_valid = True
                    validation_issues = {}
                
                # Create conftest.py if it doesn't exist
                self._create_conftest(output_dir)
                
                # Create __init__.py
                (output_dir / "__init__.py").touch()
                
                return {
                    'tests_dir': output_dir,
                    'test_files': test_files,
                    'is_valid': all_valid,
                    'validation_issues': validation_issues,
                    'attempts': attempt
                }
                
            except Exception as e:
                logger.error(f"Error during generation attempt {attempt}: {e}")
                
                if attempt == self.max_attempts:
                    raise
        
        raise RuntimeError("Failed to generate tests after maximum attempts")
    
    async def _generate_test_content(
        self,
        spec_content: str,
        attempt: int
    ) -> str:
        """
        Internal method to generate test content using the LLM.
        
        Args:
            spec_content: Content of the technical specification
            attempt: Current attempt number
            
        Returns:
            Generated test content as string
        """
        # Construct the prompt
        prompt = TEST_GENERATION_PROMPT.format(
            spec_content=spec_content
        )
        
        # Add retry context if not first attempt
        if attempt > 1:
            prompt += f"\n\n**Note**: This is attempt #{attempt}. "
            prompt += "Please ensure ALL test files are complete with proper structure and validation."
        
        # Create messages for the agent
        messages = [
            Message(role='user', content=prompt)
        ]
        
        # Run the agent
        logger.debug("Sending prompt to LLM...")
        response_messages = []
        
        async for msg in self.agent.run(messages=messages):
            response_messages.append(msg)
        
        # Extract the generated tests from responses
        test_content = ""
        for msg in response_messages:
            if hasattr(msg, 'content') and msg.content:
                test_content += msg.content
        
        if not test_content:
            raise ValueError("LLM returned empty response")
        
        return test_content.strip()
    
    def _extract_and_save_tests(
        self,
        test_content: str,
        output_dir: Path
    ) -> List[Path]:
        """
        Extract test code blocks and save to appropriate files.
        
        Args:
            test_content: Generated content containing test code
            output_dir: Directory to save test files
            
        Returns:
            List of created test file paths
        """
        test_files = []
        
        # Extract Python code blocks
        code_blocks = extract_code_blocks(test_content)
        
        # Pattern to detect file hints in markdown (e.g., "### test_core.py")
        file_pattern = re.compile(r'###?\s+(?:File:\s*)?(?:tests/)?([test_\w]+\.py)', re.IGNORECASE)
        
        # Try to match code blocks with file names
        current_file = None
        block_index = 0
        
        # Split content into sections
        sections = re.split(r'(###?\s+.*?\.py)', test_content, flags=re.IGNORECASE)
        
        for i, section in enumerate(sections):
            # Check if this is a file header
            match = file_pattern.search(section)
            if match:
                current_file = match.group(1)
                continue
            
            # Check if this section has code
            if '```python' in section and block_index < len(code_blocks):
                code = code_blocks[block_index]['code']
                
                if code and len(code) > 50:  # Skip very short snippets
                    # Determine filename
                    if current_file and current_file.startswith('test_'):
                        filename = current_file
                    else:
                        filename = f"test_module_{block_index}.py"
                    
                    # Save the test file
                    test_path = output_dir / filename
                    test_path.write_text(code, encoding='utf-8')
                    test_files.append(test_path)
                    logger.info(f"Created test file: {filename}")
                    
                    block_index += 1
        
        # If no files were created, save the entire content as a single test file
        if not test_files:
            logger.warning("Could not extract individual test files, saving as test_generated.py")
            
            # Try to extract Python code
            python_code = ""
            for block in code_blocks:
                if block['language'] == 'python':
                    python_code += block['code'] + "\n\n"
            
            if python_code:
                test_path = output_dir / "test_generated.py"
                test_path.write_text(python_code, encoding='utf-8')
                test_files.append(test_path)
        
        return test_files
    
    def _create_conftest(self, output_dir: Path):
        """Create a basic conftest.py with common fixtures."""
        conftest_path = output_dir / "conftest.py"
        
        if not conftest_path.exists():
            conftest_content = '''"""
Shared pytest fixtures for all tests.

This file is automatically loaded by pytest and makes fixtures
available to all test modules.
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir(tmp_path):
    """Provides a temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def mock_config():
    """Provides a mock configuration object."""
    return {
        "setting1": "value1",
        "setting2": 42,
        "debug": True
    }
'''
            conftest_path.write_text(conftest_content, encoding='utf-8')
            logger.info("Created conftest.py with shared fixtures")
    
    def generate_tests_sync(
        self,
        spec_path: Path,
        output_dir: Optional[Path] = None
    ) -> Dict[str, any]:
        """
        Synchronous wrapper for generate_tests.
        
        Args:
            spec_path: Path to the technical specification
            output_dir: Directory where tests should be saved
            
        Returns:
            Generation result dict
        """
        import asyncio
        
        # Run the async method in an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_tests(spec_path, output_dir)
        )


def main():
    """CLI entry point for standalone testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate pytest tests from technical specification")
    parser.add_argument("spec", type=Path, help="Path to tech_spec.md")
    parser.add_argument("--output", "-o", type=Path, help="Output directory for tests")
    parser.add_argument("--model", "-m", help="Override model name")
    parser.add_argument("--config", "-c", type=Path, help="Config file path")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = TestGeneratorAgent(
        config_path=args.config,
        model=args.model
    )
    
    # Generate tests
    result = agent.generate_tests_sync(
        spec_path=args.spec,
        output_dir=args.output
    )
    
    print(f"\n✓ Tests generated in: {result['tests_dir']}")
    print(f"  Test files: {len(result['test_files'])}")
    for tf in result['test_files']:
        print(f"    - {tf.name}")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Attempts: {result['attempts']}")
    
    if result['validation_issues']:
        print(f"  Issues: {result['validation_issues']}")


if __name__ == "__main__":
    main()
