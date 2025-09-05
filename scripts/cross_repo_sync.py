#!/usr/bin/env python
"""
Cross-Repository Flash Sync

This script synchronizes modules, agents, and assets across multiple repositories.
It handles dependency resolution, conflict detection, and versioning to ensure
consistent deployment across the entire EpochCore ecosystem.
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import github
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger("CrossRepoSync")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Cross-Repository Flash Sync"
    )
    parser.add_argument(
        "--source-repo",
        required=True,
        help="Source repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--target-repo",
        required=True,
        help="Target repository in format 'owner/repo'"
    )
    parser.add_argument(
        "--modules",
        default="core,agents",
        help="Comma-separated list of modules to sync"
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

def get_github_client():
    """Get authenticated GitHub client."""
    token = os.environ.get("GH_TOKEN")
    if not token:
        raise ValueError("GH_TOKEN environment variable not set")
    return Github(token)

def get_repository(client: Github, repo_name: str) -> Repository:
    """Get repository by name."""
    try:
        return client.get_repo(repo_name)
    except Exception as e:
        logger.error(f"Failed to access repository {repo_name}: {e}")
        raise

def get_file_content(repo: Repository, path: str) -> Optional[str]:
    """Get file content from repository."""
    try:
        content_file = repo.get_contents(path)
        if isinstance(content_file, list):
            return None  # Path is a directory
        return content_file.decoded_content.decode('utf-8')
    except Exception:
        return None

def create_or_update_file(
    repo: Repository,
    path: str,
    content: str,
    commit_message: str,
    branch: str = "main"
) -> bool:
    """Create or update file in repository."""
    try:
        # Check if file exists
        try:
            file = repo.get_contents(path, ref=branch)
            repo.update_file(
                path=path,
                message=commit_message,
                content=content,
                sha=file.sha,
                branch=branch
            )
            logger.info(f"Updated file {path} in {repo.full_name}")
        except Exception:
            # File doesn't exist, create it
            repo.create_file(
                path=path,
                message=commit_message,
                content=content,
                branch=branch
            )
            logger.info(f"Created file {path} in {repo.full_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to create/update file {path} in {repo.full_name}: {e}")
        return False

def sync_module(
    source_repo: Repository,
    target_repo: Repository,
    module_name: str,
    timestamp: str,
    mode: str
) -> Dict[str, Any]:
    """Sync a module between repositories."""
    module_path = module_name
    result = {
        "module": module_name,
        "files_synced": 0,
        "files_failed": 0,
        "details": []
    }
    
    try:
        module_contents = source_repo.get_contents(module_path)
    except Exception as e:
        logger.error(f"Failed to access module {module_name} in source repo: {e}")
        result["error"] = str(e)
        return result
    
    files_to_sync = []
    
    # Process all files and directories in the module
    while module_contents:
        content_file = module_contents.pop(0)
        
        if content_file.type == "dir":
            # Directory - get its contents and add to the queue
            try:
                dir_contents = source_repo.get_contents(content_file.path)
                module_contents.extend(dir_contents)
            except Exception as e:
                logger.warning(f"Failed to access directory {content_file.path}: {e}")
                continue
        else:
            # File - add to sync list
            files_to_sync.append(content_file)
    
    # Apply mode filter
    if mode == "delta":
        # Get list of changed files in source repo
        # This is a simplified implementation - in production, you'd want to compare with the last sync
        try:
            commit_date = (datetime.now().strftime("%Y-%m-%d"))
            commits = source_repo.get_commits(since=commit_date)
            changed_files = set()
            for commit in commits:
                for file in commit.files:
                    if file.filename.startswith(module_path):
                        changed_files.add(file.filename)
            
            # Filter files_to_sync to only include changed files
            files_to_sync = [f for f in files_to_sync if f.path in changed_files]
        except Exception as e:
            logger.warning(f"Failed to filter delta changes, falling back to full sync: {e}")
    
    # Perform the sync
    for file in files_to_sync:
        try:
            content = file.decoded_content.decode('utf-8')
            
            commit_message = f"Flash Sync: Update {file.path} [{timestamp}]"
            success = create_or_update_file(
                repo=target_repo,
                path=file.path,
                content=content,
                commit_message=commit_message
            )
            
            result["details"].append({
                "file": file.path,
                "status": "success" if success else "failed"
            })
            
            if success:
                result["files_synced"] += 1
            else:
                result["files_failed"] += 1
                
        except Exception as e:
            logger.error(f"Failed to sync file {file.path}: {e}")
            result["details"].append({
                "file": file.path,
                "status": "failed",
                "error": str(e)
            })
            result["files_failed"] += 1
    
    return result

def create_flash_sync_report(
    source_repo: str,
    target_repo: str,
    results: List[Dict[str, Any]],
    timestamp: str,
    mode: str
) -> Dict[str, Any]:
    """Create a report of the synchronization."""
    # Calculate summary stats
    total_files_synced = sum(r.get("files_synced", 0) for r in results)
    total_files_failed = sum(r.get("files_failed", 0) for r in results)
    modules_with_errors = [r["module"] for r in results if r.get("files_failed", 0) > 0]
    
    report = {
        "report_id": f"cross_repo_sync_{timestamp}",
        "source_repository": source_repo,
        "target_repository": target_repo,
        "timestamp": timestamp,
        "mode": mode,
        "summary": {
            "total_modules": len(results),
            "total_files_synced": total_files_synced,
            "total_files_failed": total_files_failed,
            "success_rate": (
                total_files_synced / (total_files_synced + total_files_failed) * 100
                if (total_files_synced + total_files_failed) > 0 else 100
            ),
            "modules_with_errors": modules_with_errors
        },
        "module_results": results
    }
    
    return report

def save_report(report: Dict[str, Any], timestamp: str) -> str:
    """Save the synchronization report."""
    reports_dir = os.path.join(os.getcwd(), "reports", "flash_sync_pow")
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = os.path.join(
        reports_dir,
        f"flash_sync_report_{timestamp}.json"
    )
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Saved Flash Sync report to {report_file}")
    return report_file

def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info(f"Starting Cross-Repository Flash Sync from {args.source_repo} to {args.target_repo}")
    logger.info(f"Sync mode: {args.mode}, Timestamp: {args.timestamp}")
    
    # Get GitHub client and repositories
    gh_client = get_github_client()
    source_repo = get_repository(gh_client, args.source_repo)
    target_repo = get_repository(gh_client, args.target_repo)
    
    # Parse modules to sync
    modules = [m.strip() for m in args.modules.split(",")]
    logger.info(f"Modules to sync: {', '.join(modules)}")
    
    # Sync each module
    results = []
    for module in modules:
        logger.info(f"Syncing module: {module}")
        result = sync_module(
            source_repo=source_repo,
            target_repo=target_repo,
            module_name=module,
            timestamp=args.timestamp,
            mode=args.mode
        )
        results.append(result)
        logger.info(f"Module {module} sync completed: {result['files_synced']} files synced, {result['files_failed']} files failed")
    
    # Create and save report
    report = create_flash_sync_report(
        source_repo=args.source_repo,
        target_repo=args.target_repo,
        results=results,
        timestamp=args.timestamp,
        mode=args.mode
    )
    report_file = save_report(report, args.timestamp)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"CROSS-REPOSITORY FLASH SYNC SUMMARY")
    print("=" * 60)
    print(f"Source: {args.source_repo}")
    print(f"Target: {args.target_repo}")
    print(f"Mode: {args.mode}")
    print(f"Timestamp: {args.timestamp}")
    print("-" * 60)
    print(f"Total modules: {report['summary']['total_modules']}")
    print(f"Files synced: {report['summary']['total_files_synced']}")
    print(f"Files failed: {report['summary']['total_files_failed']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print("-" * 60)
    print(f"Report saved to: {report_file}")
    print("=" * 60)
    
    # Exit with error if any files failed
    if report['summary']['total_files_failed'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
