"""
Test Generator Adapter - Integration with Orchestrator

This adapter bridges the TestGeneratorAgent with the orchestrator framework.
It implements the BaseAdapter interface and manages the test generation phase.
"""

from pathlib import Path
from typing import Any, Dict

from ms_agent.utils.logger import logger

# Import the base adapter from orchestrator
import sys
orchestrator_path = Path(__file__).parent.parent.parent / "orchestrator"
if str(orchestrator_path) not in sys.path:
    sys.path.insert(0, str(orchestrator_path))

from orchestrator.adapters.base import BaseAdapter
from orchestrator.core.const import FILE_TECH_SPEC, DIR_TESTS

from wyh_test.agents.test_generator_agent import TestGeneratorAgent


class TestGenAdapter(BaseAdapter):
    """
    Real implementation of Test Generator Adapter (replaces orchestrator's mock).
    
    Generates comprehensive pytest test suites from technical specifications
    using the TestGeneratorAgent following TDD principles.
    """
    
    def __init__(self, config, workspace_manager):
        """
        Initialize the Test Generator Adapter.
        
        Args:
            config: OrchestratorConfig object from orchestrator
            workspace_manager: WorkspaceManager instance
        """
        super().__init__(config, workspace_manager)
        
        # Initialize the test generator agent
        # Use model from config if available
        model = getattr(config, 'test_model', None) or 'gpt-4o'
        
        logger.info(f"Initializing TestGenAdapter with model: {model}")
        
        self.test_agent = TestGeneratorAgent(
            model=model,
            # API key will be read from environment by the agent
        )
    
    def run(self, spec_path: Path) -> Dict[str, Any]:
        """
        Execute Test generation.
        
        This is the main entry point called by the orchestrator.
        
        Args:
            spec_path: Path to tech_spec.md
            
        Returns:
            Dict with 'tests_dir' key pointing to generated tests directory
        """
        if not spec_path.exists():
            raise FileNotFoundError(f'Spec file not found: {spec_path}')
        
        logger.info(f"[TestGenAdapter] Starting test generation from: {spec_path}")
        
        # Determine output directory within workspace
        tests_dir = self.workspace.work_dir / DIR_TESTS
        
        try:
            # Call the agent (synchronous wrapper)
            result = self.test_agent.generate_tests_sync(
                spec_path=spec_path,
                output_dir=tests_dir
            )
            
            logger.info(f"[TestGenAdapter] Test generation completed: {result['tests_dir']}")
            logger.info(f"[TestGenAdapter] Generated {len(result['test_files'])} test files")
            
            for test_file in result['test_files']:
                logger.info(f"[TestGenAdapter]   - {test_file.name}")
            
            logger.info(f"[TestGenAdapter] Validation: {'✓ Passed' if result['is_valid'] else '✗ Failed'}")
            
            if result['validation_issues']:
                logger.warning(f"[TestGenAdapter] Validation issues: {result['validation_issues']}")
            
            # Return in format expected by orchestrator
            return {
                'tests_dir': result['tests_dir'],
                'test_files': result['test_files'],
                'is_valid': result['is_valid'],
                'validation_issues': result['validation_issues']
            }
            
        except Exception as e:
            logger.error(f"[TestGenAdapter] Failed to generate tests: {e}")
            raise
