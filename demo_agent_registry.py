"""
This script demonstrates the agent registry tracking system from EpochCore.

It initializes the agent tracking system and outputs evolution metrics for
the agent ecosystem.
"""

from epochcore.agents import track_agent_evolution

def main():
    """Run the agent registry tracking demo."""
    print("=" * 80)
    print("EpochCore Agent Registry - Evolution Tracking Demo")
    print("=" * 80)
    print()
    
    # Track agent evolution
    results = track_agent_evolution()
    
    # Display summary
    print("\nSummary:")
    print(f"  Total active agents: {results['registry_summary']['total_agents_managed']}")
    print(f"  Ecosystem health: {results['registry_summary']['final_ecosystem_health']:.1f}%")
    print(f"  Evolution events: {results['registry_summary']['evolution_events_processed']}")
    print(f"  Governance violations: {results['registry_summary']['governance_violations']}")
    
    print("\nResults saved to: manifests/agent_registry_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
