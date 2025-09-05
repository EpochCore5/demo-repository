#!/usr/bin/env python3
"""
Governance Sync Script
Part of the EpochCoreMASTER Ultra-Mega-Alpha-Tier Agent Flash Sync Automation system

This script performs governance compliance auditing and synchronization for the
EpochCore Flash Sync system. It validates repository structure, header compliance,
and generates governance reports for audit purposes.

Usage:
    python governance_sync.py [--strict] [--fix] [--report-file REPORT_FILE]

Requirements:
    - Python 3.8+
"""

import os
import sys
import re
import json
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("governance-sync")

# Governance configuration
GOVERNANCE_HEADER = """
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# {filename} — {description}
# Usage: {usage}
# ----------------------------------------------------------------------------
"""

# Required directory structure
REQUIRED_DIRECTORIES = [
    "agents",
    "agents/manifests",
    "assets",
    "assets/glyphs",
    "core",
    "core/recursive_improvement",
    "core/recursive_improvement/engines",
    "docs",
    "epochcore",
    "ledger",
    "reports",
    "scripts",
]

# Files that require governance headers
HEADER_REQUIRED_PATTERNS = [
    "*.sh",
    "*.py",
    "Dockerfile*",
    "*.yml",
    "*.yaml",
]

# Files excluded from governance header requirements
HEADER_EXCLUDED_FILES = [
    "__init__.py",
    "setup.py",
    "conftest.py",
]

# Standard header descriptions for common files
STANDARD_DESCRIPTIONS = {
    "flash_sync_agents.sh": "Synchronize all agents and update verification status",
    "create_mesh_graph.sh": "Generate relationship graphs between agents",
    "run_epochcore.sh": "Run the EpochCore agent system",
    "validate_github_token.py": "Validate GitHub API token for EpochCore Flash Sync",
    "validate_secrets_sync.py": "Validate secrets for EpochCore Flash Sync",
    "governance_sync.py": "Governance compliance auditing and synchronization",
}

# Standard usage patterns for common files
STANDARD_USAGE = {
    "flash_sync_agents.sh": "./flash_sync_agents.sh [--force] [--verify] [--report]",
    "create_mesh_graph.sh": "./create_mesh_graph.sh [--output json|dot] [--visualize]",
    "run_epochcore.sh": "./run_epochcore.sh [--agent registry|compliance|summary] [--sync]",
    "validate_github_token.py": "python validate_github_token.py [--token TOKEN] [--verbose]",
    "validate_secrets_sync.py": "python validate_secrets_sync.py [--verbose] [--strict]",
    "governance_sync.py": "python governance_sync.py [--strict] [--fix] [--report-file REPORT_FILE]",
}


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Governance compliance auditing for EpochCore Flash Sync"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict governance compliance"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix governance compliance issues"
    )
    parser.add_argument(
        "--report-file",
        help="Path to save the governance report JSON file"
    )
    return parser.parse_args()


def validate_directory_structure() -> Tuple[bool, Dict[str, Any]]:
    """
    Validate the repository directory structure.
    
    Returns:
        Tuple of (success, results_dict)
    """
    results = {
        "success": True,
        "missing_directories": [],
        "existing_directories": [],
    }
    
    for directory in REQUIRED_DIRECTORIES:
        if os.path.isdir(directory):
            results["existing_directories"].append(directory)
            logger.info(f"✅ Required directory exists: {directory}")
        else:
            results["missing_directories"].append(directory)
            results["success"] = False
            logger.error(f"❌ Required directory missing: {directory}")
    
    return results["success"], results


def fix_directory_structure(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix missing directories in the repository structure.
    
    Args:
        results: Results from validate_directory_structure()
        
    Returns:
        Updated results dict
    """
    fixed_directories = []
    
    for directory in results["missing_directories"]:
        try:
            os.makedirs(directory, exist_ok=True)
            fixed_directories.append(directory)
            logger.info(f"✅ Created missing directory: {directory}")
        except Exception as e:
            logger.error(f"❌ Failed to create directory {directory}: {str(e)}")
    
    # Update results
    results["fixed_directories"] = fixed_directories
    results["missing_directories"] = [d for d in results["missing_directories"] 
                                     if d not in fixed_directories]
    results["success"] = len(results["missing_directories"]) == 0
    
    return results


def find_files_requiring_headers() -> List[str]:
    """Find all files that require governance headers."""
    files_to_check = []
    
    for pattern in HEADER_REQUIRED_PATTERNS:
        # Handle glob patterns
        for file_path in Path(".").glob("**/" + pattern):
            # Convert to string and normalize
            file_str = str(file_path)
            
            # Skip excluded files
            if any(file_str.endswith(excluded) for excluded in HEADER_EXCLUDED_FILES):
                continue
                
            # Skip dot directories
            if "/." in file_str:
                continue
                
            files_to_check.append(file_str)
    
    return sorted(files_to_check)


def check_file_header(file_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a file has the correct governance header.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        Tuple of (has_valid_header, header_info)
    """
    result = {
        "file_path": file_path,
        "has_header": False,
        "header_complete": False,
        "has_filename": False,
        "has_description": False,
        "has_usage": False,
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check for the basic header pattern
        if "EPOCHCORE — ULTRA MASTERY" in content:
            result["has_header"] = True
            
            # Check for filename
            filename_match = re.search(r"# (\S+) —", content)
            if filename_match and os.path.basename(file_path) in filename_match.group(1):
                result["has_filename"] = True
                
            # Check for description
            description_match = re.search(r"— (.+?)\n", content)
            if description_match and len(description_match.group(1).strip()) > 5:
                result["has_description"] = True
                
            # Check for usage
            usage_match = re.search(r"# Usage: (.+?)\n", content)
            if usage_match and len(usage_match.group(1).strip()) > 5:
                result["has_usage"] = True
                
            # Check if header is complete
            result["header_complete"] = (
                result["has_header"] and
                result["has_filename"] and
                result["has_description"] and
                result["has_usage"]
            )
    except Exception as e:
        logger.error(f"❌ Error checking header for {file_path}: {str(e)}")
        result["error"] = str(e)
    
    return result["header_complete"], result


def generate_header_for_file(file_path: str) -> str:
    """
    Generate an appropriate governance header for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Header string
    """
    filename = os.path.basename(file_path)
    
    # Get description
    if filename in STANDARD_DESCRIPTIONS:
        description = STANDARD_DESCRIPTIONS[filename]
    else:
        # Generate a generic description based on filename
        description_parts = filename.split(".")
        verb = "Run" if description_parts[0].startswith("run_") else "Manage"
        noun = description_parts[0].replace("_", " ").title()
        description = f"{verb} the {noun} component"
    
    # Get usage
    if filename in STANDARD_USAGE:
        usage = STANDARD_USAGE[filename]
    else:
        extension = filename.split(".")[-1]
        if extension == "py":
            usage = f"python {filename} [options]"
        elif extension == "sh":
            usage = f"./{filename} [options]"
        else:
            usage = f"See documentation for usage"
    
    # Generate the header
    return GOVERNANCE_HEADER.format(
        filename=filename,
        description=description,
        usage=usage
    )


def fix_file_header(file_path: str, header_info: Dict[str, Any]) -> bool:
    """
    Fix the governance header in a file.
    
    Args:
        file_path: Path to the file
        header_info: Header information from check_file_header()
        
    Returns:
        True if fixed successfully, False otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Generate the correct header
        new_header = generate_header_for_file(file_path)
        
        # If there's an existing incomplete header, replace it
        if header_info["has_header"]:
            # Find the header section and replace it
            pattern = r"(?:#.*?EPOCHCORE.*?ULTRA MASTERY.*?# -+\n)"
            new_content = re.sub(pattern, new_header, content, flags=re.DOTALL)
        else:
            # Add the header at the beginning of the file
            # Special handling for shebang lines
            if content.startswith("#!"):
                shebang_end = content.find("\n") + 1
                new_content = content[:shebang_end] + "\n" + new_header + content[shebang_end:]
            else:
                new_content = new_header + content
        
        # Write the updated content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        logger.info(f"✅ Fixed governance header in {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix header in {file_path}: {str(e)}")
        return False


def validate_headers() -> Tuple[bool, Dict[str, Any]]:
    """
    Validate governance headers in all required files.
    
    Returns:
        Tuple of (success, results_dict)
    """
    results = {
        "success": True,
        "files_checked": 0,
        "files_with_valid_headers": 0,
        "files_with_invalid_headers": 0,
        "files_missing_headers": 0,
        "compliance_percentage": 0,
        "files": []
    }
    
    files_to_check = find_files_requiring_headers()
    results["files_checked"] = len(files_to_check)
    
    for file_path in files_to_check:
        header_valid, header_info = check_file_header(file_path)
        results["files"].append(header_info)
        
        if header_valid:
            results["files_with_valid_headers"] += 1
            logger.info(f"✅ Valid governance header: {file_path}")
        elif header_info["has_header"]:
            results["files_with_invalid_headers"] += 1
            results["success"] = False
            logger.warning(f"⚠️ Incomplete governance header: {file_path}")
        else:
            results["files_missing_headers"] += 1
            results["success"] = False
            logger.error(f"❌ Missing governance header: {file_path}")
    
    # Calculate compliance percentage
    if results["files_checked"] > 0:
        results["compliance_percentage"] = (
            results["files_with_valid_headers"] / results["files_checked"] * 100
        )
    
    logger.info(
        f"Header compliance: {results['compliance_percentage']:.1f}% "
        f"({results['files_with_valid_headers']}/{results['files_checked']})"
    )
    
    return results["success"], results


def fix_headers(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix governance headers in files.
    
    Args:
        results: Results from validate_headers()
        
    Returns:
        Updated results dict
    """
    fixed_files = []
    
    for file_info in results["files"]:
        if not file_info.get("header_complete", True):
            file_path = file_info["file_path"]
            if fix_file_header(file_path, file_info):
                fixed_files.append(file_path)
    
    # Update results
    results["fixed_files"] = fixed_files
    results["files_fixed"] = len(fixed_files)
    
    return results


def generate_governance_report(
    dir_results: Dict[str, Any],
    header_results: Dict[str, Any],
    args: argparse.Namespace
) -> Dict[str, Any]:
    """
    Generate a comprehensive governance report.
    
    Args:
        dir_results: Results from directory structure validation
        header_results: Results from header validation
        args: Command line arguments
        
    Returns:
        Report dict
    """
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "governance_validation": {
            "success": dir_results["success"] and header_results["success"],
            "directory_structure_valid": dir_results["success"],
            "header_compliance_valid": header_results["success"],
            "header_compliance_percentage": header_results["compliance_percentage"],
        },
        "directory_structure": {
            "required_directories": REQUIRED_DIRECTORIES,
            "existing_directories": dir_results["existing_directories"],
            "missing_directories": dir_results["missing_directories"],
        },
        "header_compliance": {
            "files_checked": header_results["files_checked"],
            "files_with_valid_headers": header_results["files_with_valid_headers"],
            "files_with_invalid_headers": header_results["files_with_invalid_headers"],
            "files_missing_headers": header_results["files_missing_headers"],
        },
        "fixes_applied": {}
    }
    
    # Add fix information if --fix was used
    if args.fix:
        report["fixes_applied"] = {
            "directories_fixed": dir_results.get("fixed_directories", []),
            "files_fixed": header_results.get("fixed_files", []),
        }
    
    return report


def save_governance_report(report: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """
    Save the governance report to a file.
    
    Args:
        report: Governance report dict
        file_path: Path to save the report (optional)
        
    Returns:
        Path to the saved report file
    """
    if file_path is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"governance_report_{timestamp}.json"
        
    # Create reports directory if it doesn't exist
    reports_dir = os.path.dirname(file_path)
    if reports_dir and not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Governance report saved to {file_path}")
    return file_path


def print_governance_report(report: Dict[str, Any]) -> None:
    """Print a formatted governance report."""
    print("\n" + "=" * 60)
    print("GOVERNANCE COMPLIANCE REPORT")
    print("=" * 60)
    
    print(f"\nOverall Compliance: {'✅ PASSED' if report['governance_validation']['success'] else '❌ FAILED'}")
    print(f"Directory Structure: {'✅ VALID' if report['governance_validation']['directory_structure_valid'] else '❌ INVALID'}")
    print(f"Header Compliance:   {'✅ VALID' if report['governance_validation']['header_compliance_valid'] else '❌ INVALID'}")
    print(f"Compliance Rate:     {report['governance_validation']['header_compliance_percentage']:.1f}%")
    
    print("\nDirectory Structure:")
    if report['directory_structure']['missing_directories']:
        print(f"  ❌ Missing Directories: {', '.join(report['directory_structure']['missing_directories'])}")
    else:
        print(f"  ✅ All {len(report['directory_structure']['existing_directories'])} required directories exist")
    
    print("\nHeader Compliance:")
    print(f"  Files Checked:      {report['header_compliance']['files_checked']}")
    print(f"  Valid Headers:      {report['header_compliance']['files_with_valid_headers']}")
    print(f"  Invalid Headers:    {report['header_compliance']['files_with_invalid_headers']}")
    print(f"  Missing Headers:    {report['header_compliance']['files_missing_headers']}")
    
    if "fixes_applied" in report and (
        report["fixes_applied"].get("directories_fixed") or 
        report["fixes_applied"].get("files_fixed")
    ):
        print("\nFixes Applied:")
        if report["fixes_applied"].get("directories_fixed"):
            print(f"  Directories Created: {len(report['fixes_applied']['directories_fixed'])}")
        if report["fixes_applied"].get("files_fixed"):
            print(f"  Headers Fixed:       {len(report['fixes_applied']['files_fixed'])}")
    
    print("\nRecommendations:")
    if report['governance_validation']['success']:
        print("  ✅ Repository meets governance compliance standards!")
        print("  ✅ Ready for Ultra-Mega-Alpha-Tier operations!")
    else:
        if not report['governance_validation']['directory_structure_valid']:
            print("  - Create the missing required directories")
        if not report['governance_validation']['header_compliance_valid']:
            print("  - Add governance headers to files missing them")
            print("  - Fix incomplete headers according to the standard format")
        print("  - Run with --fix to automatically apply fixes")
    
    print("\nTimestamp:", report['timestamp'])
    print("=" * 60 + "\n")


def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info("Starting governance compliance audit for EpochCore Flash Sync system")
    
    # Validate directory structure
    dir_success, dir_results = validate_directory_structure()
    
    # Fix directory structure if requested
    if args.fix and not dir_success:
        dir_results = fix_directory_structure(dir_results)
    
    # Validate headers
    header_success, header_results = validate_headers()
    
    # Fix headers if requested
    if args.fix and not header_success:
        header_results = fix_headers(header_results)
    
    # Generate governance report
    report = generate_governance_report(dir_results, header_results, args)
    
    # Save report if requested
    if args.report_file:
        save_governance_report(report, args.report_file)
    
    # Print report
    print_governance_report(report)
    
    # Exit with appropriate code
    # In strict mode, exit with error if compliance failed
    # In non-strict mode, only exit with error if directory structure is invalid
    if args.strict:
        sys.exit(0 if report["governance_validation"]["success"] else 1)
    else:
        sys.exit(0 if report["governance_validation"]["directory_structure_valid"] else 1)


if __name__ == "__main__":
    main()
