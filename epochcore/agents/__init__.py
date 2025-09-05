"""
EpochCore Agents package initialization.
"""

from .agent_registry import track_agent_evolution
from .audit_evolution_manager import recursive_audit_evolution, record_metrics

__all__ = ['track_agent_evolution', 'recursive_audit_evolution', 'record_metrics']
