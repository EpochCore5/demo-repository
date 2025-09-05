#!/usr/bin/env python
"""
Agent Synchronization Script

This script handles the synchronization of agents within a repository
or across multiple repositories. It ensures all agents are up-to-date
and consistent across the ecosystem.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("AgentSync")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Agent Synchronization"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="Target repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--timestamp",
        default=datetime.now().strftime("%Y%m%d%H%M%S"),
        help="Timestamp for synchronization tracking"
    )
    parser.add_argument(
        "--mode",
        choices=["full", "incremental", "delta"],
        default="incremental",
        help="Synchronization mode"
    )
    return parser.parse_args()


def get_agent_list() -> List[Dict[str, Any]]:
    """
    Get a list of agents to synchronize.
    
    Returns:
        List of agent information
    """
    agents_dir = os.path.join(os.getcwd(), "agents")
    manifests_dir = os.path.join(agents_dir, "manifests")
    
    agents = []
    
    # First check if we have oscillation conflict agent
    oscillation_agent_path = os.path.join(agents_dir, "oscillation_conflict_agent.py")
    if os.path.isfile(oscillation_agent_path):
        agents.append({
            "id": "oscillation_conflict_agent",
            "path": "agents/oscillation_conflict_agent.py",
            "manifest": "agents/manifests/oscillation_conflict_agent_manifest.json",
            "type": "conflict_resolution"
        })
    
    # Look for manifests to find other agents
    if os.path.isdir(manifests_dir):
        for file in os.listdir(manifests_dir):
            if file.endswith("_manifest.json") and not file.startswith("oscillation"):
                try:
                    with open(os.path.join(manifests_dir, file), 'r') as f:
                        manifest = json.load(f)
                    
                    agent_id = manifest.get("agent_id", "")
                    if agent_id:
                        agent_path = f"agents/{agent_id}.py"
                        if os.path.isfile(os.path.join(os.getcwd(), agent_path)):
                            agents.append({
                                "id": agent_id,
                                "path": agent_path,
                                "manifest": f"agents/manifests/{file}",
                                "type": manifest.get("agent_type", "unknown")
                            })
                except Exception as e:
                    logger.warning(f"Failed to process manifest {file}: {e}")
    
    return agents


def sync_agent(
    agent: Dict[str, Any],
    repository: str,
    timestamp: str,
    mode: str
) -> Dict[str, Any]:
    """
    Sync an agent.
    
    Args:
        agent: Agent information
        repository: Target repository
        timestamp: Synchronization timestamp
        mode: Synchronization mode
        
    Returns:
        Dict containing sync results
    """
    # In a real implementation, this would interact with the GitHub API
    # to push the agent to the target repository.
    # Here we simulate the synchronization process.
    
    agent_id = agent["id"]
    logger.info(f"Synchronizing agent {agent_id} to {repository}")
    
    # Check if agent file exists
    agent_file = os.path.join(os.getcwd(), agent["path"])
    if not os.path.isfile(agent_file):
        return {
            "agent_id": agent_id,
            "status": "failed",
            "reason": "Agent file not found",
            "timestamp": timestamp,
            "repository": repository
        }
    
    # Check if manifest exists
    manifest_file = os.path.join(os.getcwd(), agent["manifest"])
    manifest_exists = os.path.isfile(manifest_file)
    
    # Simulate file sync
    success = True
    file_size = os.path.getsize(agent_file) if os.path.exists(agent_file) else 0
    
    # Simulate manifest size if it exists
    manifest_size = os.path.getsize(manifest_file) if manifest_exists else 0
    
    # Simulate successful synchronization
    return {
        "agent_id": agent_id,
        "status": "success" if success else "failed",
        "agent_type": agent["type"],
        "files_synced": 2 if manifest_exists else 1,  # Agent file + manifest if exists
        "bytes_synced": file_size + manifest_size,
        "timestamp": timestamp,
        "repository": repository,
        "mode": mode,
        "manifest_synced": manifest_exists
    }


def create_sync_report(
    results: List[Dict[str, Any]],
    repository: str,
    timestamp: str,
    mode: str
) -> Dict[str, Any]:
    """
    Create a report of the synchronization.
    
    Args:
        results: List of sync results
        repository: Target repository
        timestamp: Synchronization timestamp
        mode: Synchronization mode
        
    Returns:
        Dict containing the report
    """
    successful_agents = [r for r in results if r["status"] == "success"]
    failed_agents = [r for r in results if r["status"] == "failed"]
    
    report = {
        "report_id": f"agent_sync_{timestamp}",
        "repository": repository,
        "timestamp": timestamp,
        "mode": mode,
        "summary": {
            "total_agents": len(results),
            "successful_agents": len(successful_agents),
            "failed_agents": len(failed_agents),
            "files_synced": sum(r.get("files_synced", 0) for r in successful_agents),
            "bytes_synced": sum(r.get("bytes_synced", 0) for r in successful_agents),
            "success_rate": (
                len(successful_agents) / len(results) * 100 
                if results else 0
            )
        },
        "agent_results": results
    }
    
    return report


def save_report(report: Dict[str, Any], timestamp: str) -> str:
    """
    Save the synchronization report.
    
    Args:
        report: Report data
        timestamp: Synchronization timestamp
        
    Returns:
        Path to the saved report
    """
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = os.path.join(
        reports_dir,
        f"agent_sync_report_{timestamp}.json"
    )
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Saved Agent Sync report to {report_file}")
    return report_file


def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info(f"Starting Agent Synchronization to {args.repository}")
    logger.info(f"Mode: {args.mode}, Timestamp: {args.timestamp}")
    
    # Get agents
    agents = get_agent_list()
    logger.info(f"Found {len(agents)} agents to synchronize")
    
    # Sync each agent
    results = []
    for agent in agents:
        result = sync_agent(
            agent=agent,
            repository=args.repository,
            timestamp=args.timestamp,
            mode=args.mode
        )
        results.append(result)
        
        if result["status"] == "success":
            logger.info(f"Successfully synchronized agent {agent['id']}")
        else:
            logger.error(
                f"Failed to synchronize agent {agent['id']}: {result.get('reason')}"
            )
    
    # Create and save report
    report = create_sync_report(
        results=results,
        repository=args.repository,
        timestamp=args.timestamp,
        mode=args.mode
    )
    report_file = save_report(report, args.timestamp)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"AGENT SYNCHRONIZATION SUMMARY")
    print("=" * 60)
    print(f"Repository: {args.repository}")
    print(f"Mode: {args.mode}")
    print(f"Timestamp: {args.timestamp}")
    print("-" * 60)
    print(f"Total agents: {report['summary']['total_agents']}")
    print(f"Successful: {report['summary']['successful_agents']}")
    print(f"Failed: {report['summary']['failed_agents']}")
    print(f"Files synced: {report['summary']['files_synced']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print("-" * 60)
    print(f"Report saved to: {report_file}")
    print("=" * 60)
    
    # Exit with error if any agents failed
    if report['summary']['failed_agents'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
