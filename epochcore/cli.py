"""
Command-line interface for running EpochCore agents.
"""

import argparse
import sys
from epochcore import (
    track_agent_evolution,
    audit_compliance,
    recursive_audit_evolution,
    get_audit_summary,
)


def main():
    """Execute EpochCore agent system from command line."""
    parser = argparse.ArgumentParser(
        description="EpochCore Agent System - Recursive Autonomous Operations"
    )
    
    parser.add_argument(
        "--agent",
        choices=["registry", "compliance", "summary"],
        default="registry",
        help="Agent to execute (default: registry)",
    )
    
    parser.add_argument(
        "--cycles", 
        type=int, 
        default=3, 
        help="Number of recursive cycles (default: 3)"
    )
    
    args = parser.parse_args()
    
    print("🌟 EpochCore Agent System - Initiating recursive operations...")
    
    if args.agent == "registry":
        result = track_agent_evolution()
        print("\n✅ Agent Registry tracking complete")
        print(f"Ecosystem health: {result['registry_summary']['final_ecosystem_health']:.1f}%")
    
    elif args.agent == "compliance":
        result = audit_compliance()
        print("\n✅ Compliance Audit complete")
        print(f"Security score: {result['audit_summary']['final_security_score']:.1f}%")
    
    elif args.agent == "summary":
        result = get_audit_summary()
        print("\n✅ Audit Summary generated")
        print(f"Active agents: {result['active_agents']}")
        print(f"Total entries: {result['total_entries']}")
    
    print("\n⚡ EpochCore Agent System - Operations completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
