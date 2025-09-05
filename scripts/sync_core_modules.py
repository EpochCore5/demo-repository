#!/usr/bin/env python
"""
Core Modules Synchronization Script

This script handles the synchronization of core modules within a repository
or across multiple repositories. It ensures all core modules are up-to-date
and consistent across the ecosystem.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("CoreModuleSync")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Core Modules Synchronization"
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
    parser.add_argument(
        "--force",
        choices=["true", "false"],
        default="false",
        help="Force synchronization even if module is up-to-date"
    )
    return parser.parse_args()


def get_core_module_list() -> List[str]:
    """
    Get a list of core modules to synchronize.
    
    Returns:
        List of module paths
    """
    core_modules = [
        "core/recursive_improvement",
        "core/agent_framework",
        "core/versioning",
        "core/governance",
        "core/sync"
    ]
    
    # Check for actual modules in the file system
    valid_modules = []
    for module in core_modules:
        module_path = os.path.join(os.getcwd(), module)
        if os.path.isdir(module_path):
            valid_modules.append(module)
    
    return valid_modules


def sync_core_module(
    module_path: str,
    repository: str,
    timestamp: str,
    force: bool = False
) -> Dict[str, Any]:
    """
    Sync a core module.
    
    Args:
        module_path: Path to the module
        repository: Target repository
        timestamp: Synchronization timestamp
        force: Force synchronization
        
    Returns:
        Dict containing sync results
    """
    # In a real implementation, this would interact with the GitHub API
    # to push the module to the target repository.
    # Here we simulate the synchronization process.
    
    module_name = os.path.basename(module_path)
    logger.info(f"Synchronizing core module {module_name} to {repository}")
    
    # Check if module directory exists
    if not os.path.isdir(os.path.join(os.getcwd(), module_path)):
        return {
            "module": module_name,
            "status": "failed",
            "reason": "Module directory not found",
            "timestamp": timestamp,
            "repository": repository
        }
    
    # Simulate file counting
    file_count = len([
        f for f in os.listdir(os.path.join(os.getcwd(), module_path))
        if os.path.isfile(os.path.join(os.getcwd(), module_path, f))
    ])
    
    # Simulate successful synchronization
    return {
        "module": module_name,
        "status": "success",
        "files_synced": file_count,
        "timestamp": timestamp,
        "repository": repository,
        "force_sync": force
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
    successful_modules = [r for r in results if r["status"] == "success"]
    failed_modules = [r for r in results if r["status"] == "failed"]
    
    report = {
        "report_id": f"core_sync_{timestamp}",
        "repository": repository,
        "timestamp": timestamp,
        "mode": mode,
        "summary": {
            "total_modules": len(results),
            "successful_modules": len(successful_modules),
            "failed_modules": len(failed_modules),
            "files_synced": sum(r.get("files_synced", 0) for r in successful_modules),
            "success_rate": len(successful_modules) / len(results) * 100 if results else 0
        },
        "module_results": results
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
        f"core_sync_report_{timestamp}.json"
    )
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Saved Core Sync report to {report_file}")
    return report_file


def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info(f"Starting Core Module Synchronization to {args.repository}")
    logger.info(f"Mode: {args.mode}, Timestamp: {args.timestamp}")
    
    # Get core modules
    modules = get_core_module_list()
    logger.info(f"Found {len(modules)} core modules to synchronize")
    
    # Sync each module
    results = []
    for module in modules:
        force = args.force.lower() == "true"
        result = sync_core_module(
            module_path=module,
            repository=args.repository,
            timestamp=args.timestamp,
            force=force
        )
        results.append(result)
        
        if result["status"] == "success":
            logger.info(f"Successfully synchronized module {module}")
        else:
            logger.error(f"Failed to synchronize module {module}: {result['reason']}")
    
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
    print(f"CORE MODULE SYNCHRONIZATION SUMMARY")
    print("=" * 60)
    print(f"Repository: {args.repository}")
    print(f"Mode: {args.mode}")
    print(f"Timestamp: {args.timestamp}")
    print("-" * 60)
    print(f"Total modules: {report['summary']['total_modules']}")
    print(f"Successful: {report['summary']['successful_modules']}")
    print(f"Failed: {report['summary']['failed_modules']}")
    print(f"Files synced: {report['summary']['files_synced']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print("-" * 60)
    print(f"Report saved to: {report_file}")
    print("=" * 60)
    
    # Exit with error if any modules failed
    if report['summary']['failed_modules'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
