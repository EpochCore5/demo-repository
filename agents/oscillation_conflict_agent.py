"""
Oscillation Conflict Agent

This module provides a governance-compliant agent interface for the 100x Oscillation 
Conflict Resolution System. It handles conflict detection and resolution across multiple 
domains while maintaining full audit trails and governance compliance.
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional

from core.recursive_improvement.engines.oscillation_conflict_engine import (
    OscillationConflictEngine, ConflictType
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("OscillationAgent")

# Agent configuration
AGENT_ID = "oscillation_conflict_agent"
AGENT_VERSION = "1.0.0"
GOVERNANCE_COMPLIANT = True
ETHICAL_STANDARDS = ["transparency", "accountability", "safety", "fairness"]


def resolve_conflicts_100x(
    target: str = "system",
    generate_report: bool = True,
    report_path: Optional[str] = None,
    update_manifest: bool = True
) -> Dict[str, Any]:
    """
    Execute 100x conflict resolution with full governance compliance and audit trail.
    
    Args:
        target: Target to resolve conflicts in (default: "system")
        generate_report: Whether to generate a comprehensive report (default: True)
        report_path: Custom path for the report (default: None, uses standard location)
        update_manifest: Whether to update the agent manifest (default: True)
        
    Returns:
        Dict containing resolution results and governance information
    """
    # Create execution ID for tracking
    execution_id = f"exec_{hashlib.md5(f'{datetime.now().isoformat()}_{target}'.encode()).hexdigest()[:12]}"
    
    logger.info(f"Starting 100x conflict resolution for target '{target}' [ID: {execution_id}]")
    
    # Initialize the oscillation engine
    engine = OscillationConflictEngine(
        base_frequency=100.0,
        max_frequency=10000.0,
        max_cycles=1000,
        convergence_threshold=0.001,
        enable_audit_trail=True
    )
    
    # Record governance start
    governance_log = _initialize_governance_log(execution_id, target)
    
    try:
        # Execute conflict detection and resolution
        results = engine.detect_and_resolve_conflicts(target)
        
        # Add governance data to results
        results["agent_id"] = AGENT_ID
        results["agent_version"] = AGENT_VERSION
        results["execution_id"] = execution_id
        results["governance_compliant"] = GOVERNANCE_COMPLIANT
        results["ethical_standards"] = ETHICAL_STANDARDS
        
        # Generate comprehensive report if requested
        if generate_report:
            report_file = _generate_report(engine, results, target, execution_id, report_path)
            results["report_file"] = report_file
        
        # Export audit trail
        audit_file = engine.export_audit_trail()
        results["audit_file"] = audit_file
        
        # Update agent manifest if requested
        if update_manifest:
            manifest_file = _update_agent_manifest(results)
            results["manifest_file"] = manifest_file
        
        # Finalize governance log
        _finalize_governance_log(governance_log, results, success=True)
        
        logger.info(f"Completed 100x conflict resolution with {results['efficiency_multiplier']:.1f}x efficiency")
        
        return results
        
    except Exception as e:
        logger.error(f"Error during conflict resolution: {str(e)}")
        
        # Record failure in governance log
        _finalize_governance_log(governance_log, {"error": str(e)}, success=False)
        
        # Reraise the exception
        raise


def get_agent_status() -> Dict[str, Any]:
    """
    Get the current status of the oscillation conflict agent.
    
    Returns:
        Dict containing agent status information
    """
    # Get the agent manifest
    manifest_path = _get_agent_manifest_path()
    
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "agent_id": AGENT_ID,
            "agent_version": AGENT_VERSION,
            "executions": 0,
            "last_execution": None
        }
    
    # Get report count
    reports_dir = _get_reports_directory()
    if os.path.exists(reports_dir):
        report_count = len([f for f in os.listdir(reports_dir) 
                          if f.startswith("oscillation_report_") and f.endswith(".json")])
    else:
        report_count = 0
    
    return {
        "agent_id": AGENT_ID,
        "agent_version": AGENT_VERSION,
        "governance_compliant": GOVERNANCE_COMPLIANT,
        "ethical_standards": ETHICAL_STANDARDS,
        "executions": manifest.get("executions", 0),
        "last_execution": manifest.get("last_execution"),
        "reports_generated": report_count
    }


def _initialize_governance_log(execution_id: str, target: str) -> Dict[str, Any]:
    """
    Initialize the governance log for this execution.
    
    Args:
        execution_id: Execution ID
        target: Target being processed
        
    Returns:
        Dict containing the governance log
    """
    governance_log = {
        "execution_id": execution_id,
        "agent_id": AGENT_ID,
        "agent_version": AGENT_VERSION,
        "target": target,
        "start_time": datetime.now().isoformat(),
        "governance_compliant": GOVERNANCE_COMPLIANT,
        "ethical_standards": ETHICAL_STANDARDS,
        "events": [],
        "status": "in_progress"
    }
    
    # Record the start event
    governance_log["events"].append({
        "timestamp": datetime.now().isoformat(),
        "type": "execution_start",
        "details": {
            "target": target,
            "initiated_by": os.environ.get("USER", "unknown")
        }
    })
    
    # Save the governance log
    _save_governance_log(governance_log)
    
    return governance_log


def _finalize_governance_log(governance_log: Dict[str, Any], 
                           results: Dict[str, Any], 
                           success: bool) -> None:
    """
    Finalize the governance log with execution results.
    
    Args:
        governance_log: The governance log to update
        results: Execution results
        success: Whether the execution was successful
    """
    # Update the governance log
    governance_log["end_time"] = datetime.now().isoformat()
    governance_log["status"] = "completed" if success else "failed"
    
    # Add completion event
    governance_log["events"].append({
        "timestamp": datetime.now().isoformat(),
        "type": "execution_end",
        "details": {
            "success": success,
            "results_summary": {
                "conflicts_detected": results.get("conflicts_detected", 0),
                "conflicts_resolved": results.get("conflicts_resolved", 0),
                "efficiency_multiplier": results.get("efficiency_multiplier", 0)
            } if success else {"error": results.get("error", "Unknown error")}
        }
    })
    
    # Save the updated governance log
    _save_governance_log(governance_log)


def _save_governance_log(governance_log: Dict[str, Any]) -> None:
    """
    Save the governance log to the appropriate location.
    
    Args:
        governance_log: The governance log to save
    """
    # Create the governance log directory if it doesn't exist
    governance_dir = os.path.join(os.getcwd(), "ledger", "governance")
    os.makedirs(governance_dir, exist_ok=True)
    
    # Save the governance log
    log_file = os.path.join(
        governance_dir, 
        f"governance_{governance_log['execution_id']}.json"
    )
    
    with open(log_file, 'w') as f:
        json.dump(governance_log, f, indent=2)


def _generate_report(engine: OscillationConflictEngine, 
                   results: Dict[str, Any],
                   target: str,
                   execution_id: str,
                   custom_path: Optional[str] = None) -> str:
    """
    Generate a comprehensive report of the conflict resolution.
    
    Args:
        engine: The oscillation engine instance
        results: Execution results
        target: Target that was processed
        execution_id: Execution ID
        custom_path: Custom path for the report
        
    Returns:
        Path to the generated report file
    """
    # Prepare report data
    report = {
        "report_id": f"report_{execution_id}",
        "report_type": "oscillation_conflict_resolution",
        "report_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "agent_info": {
            "agent_id": AGENT_ID,
            "agent_version": AGENT_VERSION,
            "governance_compliant": GOVERNANCE_COMPLIANT,
            "ethical_standards": ETHICAL_STANDARDS
        },
        "execution_info": {
            "execution_id": execution_id,
            "target": target,
            "start_time": results.get("start_time", datetime.now().isoformat()),
            "end_time": results.get("end_time", datetime.now().isoformat()),
            "execution_time": results.get("execution_time", 0)
        },
        "results_summary": {
            "conflicts_detected": results.get("conflicts_detected", 0),
            "conflicts_resolved": results.get("conflicts_resolved", 0),
            "resolution_rate": results.get("resolution_rate", 0),
            "traditional_resolution_rate": results.get("traditional_resolution_rate", 0),
            "resolution_rate_improvement": results.get("resolution_rate_improvement", 0),
            "efficiency_multiplier": results.get("efficiency_multiplier", 0)
        },
        "performance_metrics": {
            "execution_time": results.get("execution_time", 0),
            "traditional_time": results.get("traditional_time", 0),
            "time_saved": results.get("time_saved", 0),
            "speed_improvement": results.get("speed_improvement", 0),
            "cycles_completed": results.get("cycles_completed", 0)
        },
        "strategies_applied": results.get("strategies_applied", {})
    }
    
    # Determine report path
    if custom_path is not None:
        report_file = custom_path
    else:
        reports_dir = _get_reports_directory()
        os.makedirs(reports_dir, exist_ok=True)
        report_file = os.path.join(
            reports_dir, 
            f"oscillation_report_{execution_id}.json"
        )
    
    # Save the report
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Generated comprehensive report: {report_file}")
    
    return report_file


def _update_agent_manifest(results: Dict[str, Any]) -> str:
    """
    Update the agent manifest with the latest execution results.
    
    Args:
        results: Execution results
        
    Returns:
        Path to the updated manifest file
    """
    manifest_path = _get_agent_manifest_path()
    
    # Load existing manifest if it exists
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    else:
        manifest = {
            "agent_id": AGENT_ID,
            "agent_version": AGENT_VERSION,
            "agent_type": "conflict_resolution",
            "governance_compliant": GOVERNANCE_COMPLIANT,
            "ethical_standards": ETHICAL_STANDARDS,
            "capabilities": [
                "dependency_conflict_resolution",
                "merge_conflict_resolution",
                "resource_conflict_resolution",
                "logic_conflict_resolution",
                "temporal_conflict_resolution"
            ],
            "executions": 0,
            "conflicts_resolved": 0,
            "execution_history": []
        }
    
    # Update the manifest
    manifest["executions"] = manifest.get("executions", 0) + 1
    manifest["conflicts_resolved"] = (
        manifest.get("conflicts_resolved", 0) + results.get("conflicts_resolved", 0)
    )
    manifest["last_execution"] = {
        "execution_id": results.get("execution_id"),
        "timestamp": datetime.now().isoformat(),
        "target": results.get("target", "unknown"),
        "conflicts_detected": results.get("conflicts_detected", 0),
        "conflicts_resolved": results.get("conflicts_resolved", 0),
        "efficiency_multiplier": results.get("efficiency_multiplier", 0)
    }
    
    # Add to execution history (keep last 10)
    manifest["execution_history"].append(manifest["last_execution"])
    manifest["execution_history"] = manifest["execution_history"][-10:]
    
    # Create manifests directory if it doesn't exist
    manifests_dir = os.path.join(os.getcwd(), "agents", "manifests")
    os.makedirs(manifests_dir, exist_ok=True)
    
    # Save the manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"Updated agent manifest: {manifest_path}")
    
    return manifest_path


def _get_agent_manifest_path() -> str:
    """
    Get the path to the agent manifest file.
    
    Returns:
        Path to the agent manifest file
    """
    return os.path.join(os.getcwd(), "agents", "manifests", f"{AGENT_ID}_manifest.json")


def _get_reports_directory() -> str:
    """
    Get the path to the reports directory.
    
    Returns:
        Path to the reports directory
    """
    return os.path.join(os.getcwd(), "reports", "oscillation")


if __name__ == "__main__":
    # Simple demonstration
    print("=== 100x Oscillation Conflict Resolution Agent ===")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Version: {AGENT_VERSION}")
    print(f"Governance Compliant: {GOVERNANCE_COMPLIANT}")
    print(f"Ethical Standards: {', '.join(ETHICAL_STANDARDS)}")
    print("\nExecuting conflict resolution with 100x efficiency...\n")
    
    results = resolve_conflicts_100x(target="system")
    
    print("\n=== Resolution Results ===")
    print(f"Conflicts detected: {results['conflicts_detected']}")
    print(f"Conflicts resolved: {results['conflicts_resolved']} ({results['resolution_rate']:.1f}%)")
    print(f"Efficiency multiplier: {results['efficiency_multiplier']:.1f}x")
    print(f"Speed improvement: {results['speed_improvement']:.1f}x")
    print(f"\nReport generated: {results.get('report_file', 'None')}")
    print(f"Audit trail: {results.get('audit_file', 'None')}")
    print(f"Manifest updated: {results.get('manifest_file', 'None')}")
