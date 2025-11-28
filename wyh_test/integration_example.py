#!/usr/bin/env python3
"""
Integration Example: Using Role B with Orchestrator

This script demonstrates how to integrate the Spec and Test generation
components (Role B) with the existing orchestrator framework.

Usage:
    python3 integration_example.py [--mode full|spec|test]
"""

import sys
from pathlib import Path
import argparse
from typing import Optional

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ms_agent.utils.logger import logger


def create_sample_report(workspace_dir: Path) -> Path:
    """Create a sample research report for testing."""
    report_content = """# Research Report: Simple Web API Server

## 1. Executive Summary

This project implements a RESTful API server for managing a todo list.
The server will support CRUD operations and be built with Flask.

## 2. Key Concepts & Technologies

* **Flask**: Lightweight web framework for Python
* **RESTful API**: Standard HTTP methods (GET, POST, PUT, DELETE)
* **JSON**: Data format for request/response bodies
* **SQLite**: Lightweight database for persistence

## 3. Implementation Details

### 3.1 API Endpoints

* `GET /todos`: List all todos
* `GET /todos/<id>`: Get a specific todo
* `POST /todos`: Create a new todo
* `PUT /todos/<id>`: Update a todo
* `DELETE /todos/<id>`: Delete a todo

### 3.2 Data Model

```json
{
  "id": "integer (auto-generated)",
  "title": "string (required)",
  "description": "string (optional)",
  "completed": "boolean (default: false)",
  "created_at": "datetime (auto-generated)"
}
```

### 3.3 Dependencies

* Flask>=2.0.0
* flask-cors>=3.0.0
* pytest>=7.0.0
* pytest-flask>=1.2.0

## 4. Reference Material

* [Flask Documentation](https://flask.palletsprojects.com/)
* [RESTful API Best Practices](https://restfulapi.net/)

## 5. Constraints & Risks

* **Performance**: SQLite may not scale for high concurrency
* **Security**: Need to implement proper input validation
* **Error Handling**: Must return appropriate HTTP status codes

## 6. Testing Considerations

* Test all CRUD operations
* Test invalid input handling
* Test database persistence
* Test CORS configuration
"""
    
    report_path = workspace_dir / "report.md"
    report_path.write_text(report_content)
    logger.info(f"Created sample report: {report_path}")
    return report_path


def run_full_pipeline(workspace_dir: Path):
    """Run the complete Spec + Test generation pipeline."""
    from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent
    from wyh_test.agents.test_generator_agent import TestGeneratorAgent
    
    logger.info("=" * 60)
    logger.info("ROLE B INTEGRATION EXAMPLE: Full Pipeline")
    logger.info("=" * 60)
    
    # Step 1: Create sample report
    logger.info("\n[Step 1] Creating sample research report...")
    report_path = create_sample_report(workspace_dir)
    
    # Step 2: Generate Spec
    logger.info("\n[Step 2] Generating technical specification...")
    spec_agent = SpecGeneratorAgent(model='gpt-4o-mini')  # Using mini for demo
    
    try:
        spec_result = spec_agent.generate_spec_sync(
            report_path=report_path,
            project_name="Todo API Server"
        )
        
        logger.info(f"✓ Spec generated: {spec_result['spec_path']}")
        logger.info(f"  - Valid: {spec_result['is_valid']}")
        logger.info(f"  - Attempts: {spec_result['attempts']}")
        
        if spec_result['validation_issues']:
            logger.warning(f"  - Issues: {spec_result['validation_issues']}")
        
        spec_path = spec_result['spec_path']
        
    except Exception as e:
        logger.error(f"✗ Spec generation failed: {e}")
        return
    
    # Step 3: Generate Tests
    logger.info("\n[Step 3] Generating pytest test suite...")
    test_agent = TestGeneratorAgent(model='gpt-4o-mini')
    
    try:
        test_result = test_agent.generate_tests_sync(
            spec_path=spec_path
        )
        
        logger.info(f"✓ Tests generated: {test_result['tests_dir']}")
        logger.info(f"  - Test files: {len(test_result['test_files'])}")
        
        for test_file in test_result['test_files']:
            logger.info(f"    • {test_file.name}")
        
        logger.info(f"  - Valid: {test_result['is_valid']}")
        
        if test_result['validation_issues']:
            logger.warning(f"  - Issues: {test_result['validation_issues']}")
    
    except Exception as e:
        logger.error(f"✗ Test generation failed: {e}")
        return
    
    # Step 4: Summary
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 60)
    logger.info(f"\nGenerated artifacts in: {workspace_dir}")
    logger.info(f"  1. Research Report:  report.md")
    logger.info(f"  2. Tech Spec:        tech_spec.md")
    logger.info(f"  3. Tests:            tests/")
    logger.info(f"\nNext steps:")
    logger.info(f"  - Review tech_spec.md for accuracy")
    logger.info(f"  - Run tests: pytest {workspace_dir}/tests/")
    logger.info(f"  - Proceed to coding phase (Role C)")


def run_spec_only(workspace_dir: Path, report_path: Optional[Path] = None):
    """Run only the Spec generation phase."""
    from wyh_test.agents.spec_generator_agent import SpecGeneratorAgent
    
    logger.info("=" * 60)
    logger.info("ROLE B INTEGRATION EXAMPLE: Spec Generation Only")
    logger.info("=" * 60)
    
    if report_path is None:
        report_path = create_sample_report(workspace_dir)
    
    logger.info(f"\nGenerating spec from: {report_path}")
    
    spec_agent = SpecGeneratorAgent(model='gpt-4o-mini')
    
    try:
        result = spec_agent.generate_spec_sync(
            report_path=report_path
        )
        
        logger.info(f"\n✓ Spec generated: {result['spec_path']}")
        logger.info(f"  - Project: {result['project_name']}")
        logger.info(f"  - Valid: {result['is_valid']}")
        
        # Show a preview
        spec_content = result['spec_path'].read_text()
        preview = spec_content[:500] + "..." if len(spec_content) > 500 else spec_content
        logger.info(f"\nPreview:\n{preview}")
        
    except Exception as e:
        logger.error(f"✗ Failed: {e}")


def run_test_only(workspace_dir: Path, spec_path: Optional[Path] = None):
    """Run only the Test generation phase."""
    from wyh_test.agents.test_generator_agent import TestGeneratorAgent
    
    logger.info("=" * 60)
    logger.info("ROLE B INTEGRATION EXAMPLE: Test Generation Only")
    logger.info("=" * 60)
    
    if spec_path is None:
        # Need a spec file, create sample or error
        spec_path = workspace_dir / "tech_spec.md"
        if not spec_path.exists():
            logger.error(f"No spec file found at {spec_path}")
            logger.info("Run with --mode full or --mode spec first")
            return
    
    logger.info(f"\nGenerating tests from: {spec_path}")
    
    test_agent = TestGeneratorAgent(model='gpt-4o-mini')
    
    try:
        result = test_agent.generate_tests_sync(
            spec_path=spec_path
        )
        
        logger.info(f"\n✓ Tests generated: {result['tests_dir']}")
        logger.info(f"  - Files: {len(result['test_files'])}")
        
        for test_file in result['test_files']:
            logger.info(f"    • {test_file.name} ({test_file.stat().st_size} bytes)")
        
    except Exception as e:
        logger.error(f"✗ Failed: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Role B Integration Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline (Report -> Spec -> Tests)
  python3 integration_example.py --mode full
  
  # Generate spec only
  python3 integration_example.py --mode spec --report path/to/report.md
  
  # Generate tests only
  python3 integration_example.py --mode test --spec path/to/tech_spec.md
"""
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'spec', 'test'],
        default='full',
        help='Execution mode'
    )
    
    parser.add_argument(
        '--workspace',
        type=Path,
        help='Workspace directory (default: ./workspace_example)'
    )
    
    parser.add_argument(
        '--report',
        type=Path,
        help='Path to existing report.md (for spec mode)'
    )
    
    parser.add_argument(
        '--spec',
        type=Path,
        help='Path to existing tech_spec.md (for test mode)'
    )
    
    args = parser.parse_args()
    
    # Setup workspace
    if args.workspace:
        workspace_dir = args.workspace
    else:
        workspace_dir = Path.cwd() / "workspace_example"
    
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Run selected mode
    if args.mode == 'full':
        run_full_pipeline(workspace_dir)
    elif args.mode == 'spec':
        run_spec_only(workspace_dir, args.report)
    elif args.mode == 'test':
        run_test_only(workspace_dir, args.spec)


if __name__ == '__main__':
    main()
