"""
Spec Generator Agent

This agent converts research reports into structured technical specifications.
It acts as the crucial bridge between the Research phase (Role A) and 
the Coding phase (Role C).

Key Responsibilities:
- Parse and understand research reports
- Extract actionable technical requirements
- Design clear API specifications
- Define project structure and dependencies
- Highlight testable behaviors for QA
"""

import os
from pathlib import Path
from typing import Dict, Optional

from omegaconf import DictConfig, OmegaConf

from ms_agent.agent.llm_agent import LLMAgent
from ms_agent.llm.utils import Message
from ms_agent.utils.logger import logger

from wyh_test.utils.prompts import SPEC_GENERATION_PROMPT
from wyh_test.utils.validators import (
    validate_spec_format,
    extract_project_name,
    sanitize_filename
)


class SpecGeneratorAgent:
    """
    Agent for generating technical specifications from research reports.
    
    This agent wraps an LLMAgent and provides a high-level interface
    for spec generation with validation and retry logic.
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Spec Generator Agent.
        
        Args:
            config_path: Path to agent configuration YAML file
            model: Override model name (e.g., 'gpt-4o', 'claude-3-5-sonnet-20241022')
            api_key: Override API key
            **kwargs: Additional configuration overrides
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "spec_agent.yaml"
        
        self.config = self._load_config(config_path, model, api_key, **kwargs)
        
        # Initialize the underlying LLM agent
        self.agent = LLMAgent(
            config=self.config,
            tag="SpecGenerator",
            trust_remote_code=False
        )
        
        # Configuration parameters
        self.max_attempts = self.config.get('retry', {}).get('max_attempts', 3)
        self.validate_output = self.config.get('output', {}).get('validation', {}).get('enabled', True)
        
        logger.info(f"SpecGeneratorAgent initialized with model: {self.config.llm.model}")
    
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
    
    async def generate_spec(
        self,
        report_path: Path,
        output_path: Optional[Path] = None,
        project_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a technical specification from a research report.
        
        Args:
            report_path: Path to the research report (report.md)
            output_path: Path where tech_spec.md should be saved
            project_name: Optional project name (extracted from report if not provided)
            
        Returns:
            Dict containing:
                - spec_path: Path to generated spec
                - is_valid: Whether validation passed
                - validation_issues: List of issues found
                - attempts: Number of generation attempts made
        """
        if not report_path.exists():
            raise FileNotFoundError(f"Report file not found: {report_path}")
        
        # Read the research report
        report_content = report_path.read_text(encoding='utf-8')
        
        # Extract or use provided project name
        if project_name is None:
            project_name = extract_project_name(report_content)
        
        # Determine output path
        if output_path is None:
            output_path = report_path.parent / "tech_spec.md"
        
        logger.info(f"Generating spec for project: {project_name}")
        logger.info(f"Reading report from: {report_path}")
        logger.info(f"Output will be saved to: {output_path}")
        
        # Generate spec with retry logic
        for attempt in range(1, self.max_attempts + 1):
            logger.info(f"Generation attempt {attempt}/{self.max_attempts}")
            
            try:
                spec_content = await self._generate_spec_content(
                    report_content,
                    project_name,
                    attempt
                )
                
                # Validate if enabled
                if self.validate_output:
                    is_valid, issues = validate_spec_format(spec_content)
                    
                    if not is_valid:
                        logger.warning(f"Validation failed on attempt {attempt}: {issues}")
                        
                        if attempt < self.max_attempts:
                            # Prepare feedback for retry
                            logger.info("Retrying with validation feedback...")
                            continue
                        else:
                            logger.error("Max attempts reached. Saving potentially incomplete spec.")
                    else:
                        logger.info("Validation passed!")
                else:
                    is_valid = True
                    issues = []
                
                # Save the spec
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(spec_content, encoding='utf-8')
                logger.info(f"Spec saved to: {output_path}")
                
                return {
                    'spec_path': output_path,
                    'is_valid': is_valid,
                    'validation_issues': issues,
                    'attempts': attempt,
                    'project_name': project_name
                }
                
            except Exception as e:
                logger.error(f"Error during generation attempt {attempt}: {e}")
                
                if attempt == self.max_attempts:
                    raise
        
        raise RuntimeError("Failed to generate spec after maximum attempts")
    
    async def _generate_spec_content(
        self,
        report_content: str,
        project_name: str,
        attempt: int
    ) -> str:
        """
        Internal method to generate spec content using the LLM.
        
        Args:
            report_content: Content of the research report
            project_name: Name of the project
            attempt: Current attempt number
            
        Returns:
            Generated spec content as markdown string
        """
        # Construct the prompt
        prompt = SPEC_GENERATION_PROMPT.format(
            report_content=report_content,
            project_name=project_name
        )
        
        # Add retry context if not first attempt
        if attempt > 1:
            prompt += f"\n\n**Note**: This is attempt #{attempt}. "
            prompt += "Please ensure the output includes ALL required sections with complete details."
        
        # Create messages for the agent
        messages = [
            Message(role='user', content=prompt)
        ]
        
        # Run the agent
        logger.debug("Sending prompt to LLM...")
        response_messages = []
        
        # Use the agent's run method (await the coroutine first)
        generator = await self.agent.run(messages=messages)
        async for msg in generator:
            response_messages.append(msg)
        
        # Extract the generated spec from responses
        spec_content = ""
        for msg in response_messages:
            if hasattr(msg, 'content') and msg.content:
                spec_content += msg.content
        
        if not spec_content:
            raise ValueError("LLM returned empty response")
        
        return spec_content.strip()
    
    def generate_spec_sync(
        self,
        report_path: Path,
        output_path: Optional[Path] = None,
        project_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Synchronous wrapper for generate_spec.
        
        Args:
            report_path: Path to the research report
            output_path: Path where tech_spec.md should be saved
            project_name: Optional project name
            
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
            self.generate_spec(report_path, output_path, project_name)
        )


def main():
    """CLI entry point for standalone testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate technical specification from research report")
    parser.add_argument("report", type=Path, help="Path to report.md")
    parser.add_argument("--output", "-o", type=Path, help="Output path for tech_spec.md")
    parser.add_argument("--project-name", "-n", help="Project name")
    parser.add_argument("--model", "-m", help="Override model name")
    parser.add_argument("--config", "-c", type=Path, help="Config file path")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = SpecGeneratorAgent(
        config_path=args.config,
        model=args.model
    )
    
    # Generate spec
    result = agent.generate_spec_sync(
        report_path=args.report,
        output_path=args.output,
        project_name=args.project_name
    )
    
    print(f"\n✓ Spec generated: {result['spec_path']}")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Attempts: {result['attempts']}")
    
    if result['validation_issues']:
        print(f"  Issues: {result['validation_issues']}")


if __name__ == "__main__":
    main()
