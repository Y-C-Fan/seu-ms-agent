"""
Spec Adapter - Integration with Orchestrator

This adapter bridges the SpecGeneratorAgent with the orchestrator framework.
It implements the BaseAdapter interface from orchestrator and provides
a clean integration point for the spec generation phase.
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
from orchestrator.core.const import FILE_REPORT, FILE_TECH_SPEC

from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent


class SpecAdapter(BaseAdapter):
    """
    Real implementation of Spec Adapter (replaces orchestrator's mock).
    
    Converts research reports into technical specifications using
    the SpecGeneratorAgent with high-quality LLM models.
    """
    
    def __init__(self, config, workspace_manager):
        """
        Initialize the Spec Adapter.
        
        Args:
            config: OrchestratorConfig object from orchestrator
            workspace_manager: WorkspaceManager instance
        """
        super().__init__(config, workspace_manager)
        
        # Initialize the spec generator agent
        # Use model from config if available
        model = getattr(config, 'spec_model', None) or 'gpt-4o'
        
        logger.info(f"Initializing SpecAdapter with model: {model}")
        
        self.spec_agent = SpecGeneratorAgent(
            model=model,
            # API key will be read from environment by the agent
        )
    
    def run(self, report_path: Path) -> Dict[str, Any]:
        """
        Execute Spec generation.
        
        This is the main entry point called by the orchestrator.
        
        Args:
            report_path: Path to report.md
            
        Returns:
            Dict with 'spec_path' key pointing to generated tech_spec.md
        """
        if not report_path.exists():
            raise FileNotFoundError(f'Report file not found: {report_path}')
        
        logger.info(f"[SpecAdapter] Starting spec generation from: {report_path}")
        
        # Determine output path within workspace
        spec_path = self.workspace.work_dir / FILE_TECH_SPEC
        
        try:
            # Call the agent (synchronous wrapper)
            result = self.spec_agent.generate_spec_sync(
                report_path=report_path,
                output_path=spec_path
            )
            
            logger.info(f"[SpecAdapter] Spec generation completed: {result['spec_path']}")
            logger.info(f"[SpecAdapter] Validation: {'✓ Passed' if result['is_valid'] else '✗ Failed'}")
            
            if result['validation_issues']:
                logger.warning(f"[SpecAdapter] Validation issues: {result['validation_issues']}")
            
            # Return in format expected by orchestrator
            return {
                'spec_path': result['spec_path'],
                'is_valid': result['is_valid'],
                'validation_issues': result['validation_issues'],
                'project_name': result.get('project_name', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"[SpecAdapter] Failed to generate spec: {e}")
            raise
