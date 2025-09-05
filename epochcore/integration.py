"""
Integration module connecting EpochCore agents with agent management system.

This module provides the bridge between the Python-based EpochCore recursive
agent system and the shell-based agent management tools.
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from epochcore import track_agent_evolution, audit_compliance


def sync_with_agent_management_system() -> Dict[str, Any]:
    """
    Synchronize EpochCore agents with the shell-based agent management system.
    
    This function:
    1. Runs the EpochCore agents to get current state
    2. Maps EpochCore agents to agent management system entries
    3. Updates the agent manifests and glyphs if needed
    4. Runs flash sync to ensure consistency
    
    Returns:
        Dictionary with synchronization results
    """
    print("🔄 Synchronizing EpochCore agents with agent management system...")
    
    # Run EpochCore agents to get current state
    registry_data = track_agent_evolution()
    compliance_data = audit_compliance()
    
    # Extract agents from registry
    registered_agents = registry_data["detailed_cycles"][-1]["agent_registry"]
    
    # Ensure directories exist
    agent_dirs = [
        "agents/manifests",
        "assets/glyphs",
        "reports",
        "ledger",
    ]
    for directory in agent_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Map EpochCore agents to management system entries
    agent_roster_path = "agents/roster.json"
    if not os.path.exists(agent_roster_path):
        # Create initial roster if it doesn't exist
        with open(agent_roster_path, "w") as f:
            json.dump([], f)
    
    # Read existing roster
    with open(agent_roster_path, "r") as f:
        try:
            roster = json.load(f)
        except json.JSONDecodeError:
            roster = []
    
    # Add or update agents in roster
    agent_count = 0
    new_agents = 0
    updated_agents = 0
    
    for agent_name, agent_data in registered_agents.items():
        agent_id = f"epoch_{agent_name}"
        agent_count += 1
        
        # Check if agent exists in roster
        existing_agent = next(
            (a for a in roster if a.get("agent_id") == agent_id), None
        )
        
        agent_entry = {
            "agent_id": agent_id,
            "name": agent_data["name"].title(),
            "role": agent_data.get("capabilities", ["Unknown"])[0].replace("_", " ").title(),
            "status": agent_data["status"],
        }
        
        if existing_agent:
            # Update existing agent
            for idx, agent in enumerate(roster):
                if agent.get("agent_id") == agent_id:
                    roster[idx] = agent_entry
                    updated_agents += 1
                    break
        else:
            # Add new agent
            roster.append(agent_entry)
            new_agents += 1
            
            # Generate manifest for the agent
            manifest_path = f"agents/manifests/{agent_id}_manifest.json"
            
            # Create baseline manifest
            manifest = {
                "agent_id": agent_id,
                "name": agent_entry["name"],
                "role": agent_entry["role"],
                "status": agent_entry["status"],
                "integrations": {},
                "meshy_triggers": [
                    "FIVE_AND_GO",
                    "FOREST_BRIDGE",
                    "ROOT_OF_ROOTS"
                ],
                "glyph": {
                    "core": "⚡✶✷✦\n✧✩✪✫\n✬✭✮✯\n♆♇♁♃",
                    "mesh": "♄♅♈♉",
                    "files": {
                        "txt": f"assets/glyphs/{agent_id}.txt",
                        "md": f"assets/glyphs/{agent_id}.md"
                    }
                },
                "reports": {
                    "init_report": f"/reports/{agent_id}_init.json",
                    "activity_log": f"/reports/{agent_id}_log.jsonl"
                },
                "ledger": {
                    "capsule_id": f"keccak256({agent_id})",
                    "seal_hash": "",
                    "last_verified": datetime.utcnow().isoformat()
                },
                "covenant": [
                    "Timestamp → Log → Seal → Archive → Reinject",
                    "Recursive Autonomy",
                    "Governance Compliance"
                ]
            }
            
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2)
                
            # Generate glyph files
            glyph_txt_path = f"assets/glyphs/{agent_id}.txt"
            with open(glyph_txt_path, "w") as f:
                f.write(manifest["glyph"]["core"])
                
            glyph_md_path = f"assets/glyphs/{agent_id}.md"
            with open(glyph_md_path, "w") as f:
                f.write(f"# Glyph — {agent_id}\n\n**mesh-variant:** {manifest['glyph']['mesh']}\n")
                
            # Generate init report
            init_report_path = f"reports/{agent_id}_init.json"
            with open(init_report_path, "w") as f:
                json.dump({
                    "ts": datetime.utcnow().isoformat(),
                    "agent_id": agent_id,
                    "event": "agent_init",
                    "role": agent_entry["role"],
                    "name": agent_entry["name"],
                    "source": "EpochCore"
                }, f, indent=2)
    
    # Save updated roster
    with open(agent_roster_path, "w") as f:
        json.dump(roster, f, indent=2)
    
    # Run flash sync if available
    flash_sync_result = None
    if os.path.exists("./flash_sync_agents.sh"):
        try:
            print("Running flash sync to update agent ledger...")
            result = subprocess.run(
                ["./flash_sync_agents.sh", "--report"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            flash_sync_result = result.stdout
        except Exception as e:
            print(f"Warning: Flash sync failed: {e}")
    
    # Create mesh graph if available
    mesh_graph_result = None
    if os.path.exists("./create_mesh_graph.sh"):
        try:
            print("Generating agent mesh graph...")
            result = subprocess.run(
                ["./create_mesh_graph.sh", "--output", "json"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            mesh_graph_result = result.stdout
        except Exception as e:
            print(f"Warning: Mesh graph generation failed: {e}")
    
    # Return results
    results = {
        "agent_count": agent_count,
        "new_agents": new_agents,
        "updated_agents": updated_agents,
        "timestamp": datetime.utcnow().isoformat(),
        "flash_sync_run": flash_sync_result is not None,
        "mesh_graph_created": mesh_graph_result is not None,
    }
    
    print(f"✅ Synchronization complete: {new_agents} new, {updated_agents} updated")
    return results


if __name__ == "__main__":
    sync_with_agent_management_system()
