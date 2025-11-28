"""
Role B Implementation: Spec & Test Generation Module

This module implements the crucial "glue layer" between Research (Role A) 
and Coding (Role C) phases in the Research-to-Code pipeline.

Components:
- SpecGeneratorAgent: Converts research reports into technical specifications
- TestGeneratorAgent: Generates pytest test cases from specifications
- Adapters: Integration layer with the orchestrator framework
"""

__version__ = "0.1.0"
