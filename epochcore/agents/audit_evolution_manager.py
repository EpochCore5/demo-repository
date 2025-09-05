"""
Audit and Evolution Manager for EpochCore agents.

This module provides audit trail and evolution tracking capabilities for the 
agent ecosystem, ensuring governance compliance and proper record-keeping.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("audit_evolution_manager")

# Ensure audit directories exist
def ensure_audit_paths():
    """Create necessary audit directories if they don't exist."""
    base_path = Path("audits")
    base_path.mkdir(exist_ok=True)
    
    (base_path / "evolution").mkdir(exist_ok=True)
    (base_path / "governance").mkdir(exist_ok=True)
    (base_path / "metrics").mkdir(exist_ok=True)
    
    return base_path

def recursive_audit_evolution(agent_name: str, cycle: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record audit information for agent evolution.
    
    Creates a comprehensive audit trail for agent evolution events,
    ensuring governance compliance and proper tracking of changes.
    
    Args:
        agent_name: Name of the agent being audited
        cycle: Current evolution cycle number
        data: Data to be recorded in the audit
        
    Returns:
        Audit record with metadata
    """
    timestamp = datetime.utcnow()
    audit_path = ensure_audit_paths()
    
    # Add metadata to audit record
    audit_record = {
        "agent": agent_name,
        "timestamp": timestamp.isoformat(),
        "cycle": cycle,
        "governance_compliance": True,
        "audit_version": "1.0",
        "data": data
    }
    
    # Apply governance checks
    governance_checks = validate_governance_compliance(audit_record)
    audit_record["governance_validation"] = governance_checks
    
    # Save audit record
    try:
        file_path = audit_path / "evolution" / f"{agent_name}_cycle_{cycle}_{timestamp.strftime('%Y%m%d%H%M%S')}.json"
        with open(file_path, "w") as f:
            json.dump(audit_record, f, indent=2)
        logger.info(f"Audit record created for {agent_name} (cycle {cycle})")
    except Exception as e:
        logger.error(f"Failed to write audit record: {str(e)}")
    
    return audit_record

def validate_governance_compliance(record: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate that the audit record complies with governance requirements.
    
    Args:
        record: The audit record to validate
        
    Returns:
        Dictionary with validation results
    """
    checks = {
        "has_timestamp": "timestamp" in record,
        "has_agent_name": "agent" in record,
        "has_cycle": "cycle" in record,
        "has_data": "data" in record,
        "ethics_compliant": True,  # Placeholder for actual ethics check
        "policy_compliant": True,  # Placeholder for actual policy check
        "positivity_enforced": True  # Placeholder for positivity check
    }
    
    # Overall compliance requires all checks to pass
    checks["fully_compliant"] = all(checks.values())
    
    return checks

def record_metrics(agent_name: str, metrics: Dict[str, Union[float, int, str]]):
    """
    Record operational metrics for an agent.
    
    Args:
        agent_name: Name of the agent
        metrics: Dictionary of metrics to record
    """
    timestamp = datetime.utcnow()
    audit_path = ensure_audit_paths()
    
    metrics_record = {
        "agent": agent_name,
        "timestamp": timestamp.isoformat(),
        "metrics": metrics
    }
    
    try:
        file_path = audit_path / "metrics" / f"{agent_name}_{timestamp.strftime('%Y%m%d')}.json"
        
        # Append to existing file if it exists
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
                
                if isinstance(existing_data, list):
                    existing_data.append(metrics_record)
                else:
                    existing_data = [existing_data, metrics_record]
                
                with open(file_path, "w") as f:
                    json.dump(existing_data, f, indent=2)
            except Exception:
                # If reading/parsing fails, create a new file
                with open(file_path.with_name(f"{agent_name}_{timestamp.strftime('%Y%m%d%H%M%S')}.json"), "w") as f:
                    json.dump([metrics_record], f, indent=2)
        else:
            # Create new file
            with open(file_path, "w") as f:
                json.dump([metrics_record], f, indent=2)
                
        logger.info(f"Metrics recorded for {agent_name}")
    except Exception as e:
        logger.error(f"Failed to record metrics: {str(e)}")
