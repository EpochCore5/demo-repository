"""
EpochCore Agent System package initialization.

This package implements a recursive autonomous system (RAS) for agent management, 
governance, auditing, and compliance verification. It integrates with the agent 
management tools and provides a Python API for working with agents.
"""

# Version information
from .version import __version__

# Core components
from .audit_evolution_manager import recursive_audit_evolution, get_audit_summary
from .agent_registry import track_agent_evolution
from .compliance_auditor import audit_compliance

__all__ = [
    "recursive_audit_evolution", 
    "get_audit_summary",
    "track_agent_evolution", 
    "audit_compliance",
]
