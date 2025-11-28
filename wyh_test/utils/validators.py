"""
Validation utilities for Spec and Test outputs.

These validators ensure that generated artifacts meet quality standards
before being passed to the next stage of the pipeline.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def validate_spec_format(spec_content: str) -> Tuple[bool, List[str]]:
    """
    Validate that a technical specification has all required sections.
    
    Args:
        spec_content: The markdown content of the tech spec
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Required sections based on the template
    required_sections = [
        r"#+ Executive Summary",
        r"#+ System Architecture",
        r"#+ File Structure",
        r"#+ API Specifications",
        r"#+ Dependencies",
        r"#+ Testing Considerations"
    ]
    
    for section_pattern in required_sections:
        if not re.search(section_pattern, spec_content, re.IGNORECASE):
            section_name = section_pattern.replace(r"#+ ", "")
            issues.append(f"Missing required section: {section_name}")
    
    # Check for code blocks (should have at least file structure)
    if "```" not in spec_content:
        issues.append("No code blocks found - spec should include file structure and examples")
    
    # Check minimum length (too short likely incomplete)
    if len(spec_content) < 1000:
        issues.append(f"Spec too short ({len(spec_content)} chars) - likely incomplete")
    
    # Check for placeholder text that wasn't filled
    placeholder_patterns = [
        r"\[.*?\](?!\()",  # [Something] not followed by ( (not a link)
        r"TODO",
        r"FIXME",
        r"\.\.\."
    ]
    
    for pattern in placeholder_patterns:
        matches = re.findall(pattern, spec_content)
        if matches:
            issues.append(f"Found placeholder text that should be filled: {matches[:3]}")
            break
    
    return (len(issues) == 0, issues)


def validate_test_format(test_content: str, test_file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate that generated test code follows pytest conventions.
    
    Args:
        test_content: The Python test code
        test_file_path: Path to the test file
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check file naming convention
    if not test_file_path.name.startswith("test_"):
        issues.append(f"Test file should start with 'test_': {test_file_path.name}")
    
    if not test_file_path.name.endswith(".py"):
        issues.append(f"Test file should be a .py file: {test_file_path.name}")
    
    # Required imports
    if "import pytest" not in test_content:
        issues.append("Missing 'import pytest' - required for pytest tests")
    
    # Check for test functions/classes
    test_function_pattern = r"def test_\w+\("
    test_class_pattern = r"class Test\w+:"
    
    has_test_functions = bool(re.search(test_function_pattern, test_content))
    has_test_classes = bool(re.search(test_class_pattern, test_content))
    
    if not (has_test_functions or has_test_classes):
        issues.append("No test functions (test_*) or test classes (Test*) found")
    
    # Check for docstrings
    if '"""' not in test_content and "'''" not in test_content:
        issues.append("Tests should have docstrings explaining what they test")
    
    # Check minimum content length
    if len(test_content) < 200:
        issues.append(f"Test file too short ({len(test_content)} chars) - likely incomplete")
    
    # Check for proper AAA structure hints (comments or clear sections)
    # This is a soft check
    if test_content.count("# Given") + test_content.count("# When") + test_content.count("# Then") < 3:
        # Not necessarily an error, but good practice
        pass  # Could add a warning system
    
    # Check for assertions or pytest.skip (TDD style)
    has_assertions = "assert " in test_content
    has_skip = "pytest.skip" in test_content
    
    if not (has_assertions or has_skip):
        issues.append("Tests should contain assertions or pytest.skip() for TDD")
    
    return (len(issues) == 0, issues)


def validate_project_structure(workspace_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate that the generated project has expected structure.
    
    Args:
        workspace_path: Path to the workspace/run_xxx directory
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check for required files
    required_files = [
        "tech_spec.md",
        "tests"  # Directory
    ]
    
    for required in required_files:
        path = workspace_path / required
        if not path.exists():
            issues.append(f"Missing required file/directory: {required}")
    
    # Check tests directory structure
    tests_dir = workspace_path / "tests"
    if tests_dir.exists() and tests_dir.is_dir():
        test_files = list(tests_dir.glob("test_*.py"))
        if not test_files:
            issues.append("tests/ directory exists but contains no test_*.py files")
    
    return (len(issues) == 0, issues)


def extract_project_name(report_content: str) -> str:
    """
    Extract a project name from the research report.
    
    Args:
        report_content: Content of report.md
        
    Returns:
        Project name string
    """
    # Try to find title in markdown
    title_match = re.search(r"^#\s+(.+)$", report_content, re.MULTILINE)
    if title_match:
        return title_match.group(1).replace("Research Report:", "").strip()
    
    # Fallback: first non-empty line
    lines = report_content.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            return line[:50]  # First 50 chars
    
    return "Unnamed Project"


def extract_code_blocks(markdown_content: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown content.
    
    Args:
        markdown_content: Markdown text with code blocks
        
    Returns:
        List of dicts with 'language' and 'code' keys
    """
    pattern = r"```(\w*)\n(.*?)```"
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    
    return [
        {"language": lang or "text", "code": code.strip()}
        for lang, code in matches
    ]


def sanitize_filename(name: str) -> str:
    """
    Convert a name into a valid filename.
    
    Args:
        name: Original name (potentially with spaces, special chars)
        
    Returns:
        Sanitized filename
    """
    # Replace spaces and special chars with underscores
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    return name.lower()
