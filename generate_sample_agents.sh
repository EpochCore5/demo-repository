#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# generate_sample_agents.sh — Create sample agents for demonstration
# Usage: ./generate_sample_agents.sh [--count N] [--prefix string]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_COUNT=5
PREFIX="demo"

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --count)
      AGENT_COUNT="$2"
      shift 2
      ;;
    --prefix)
      PREFIX="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./generate_sample_agents.sh [--count N] [--prefix string]"
      exit 1
      ;;
  esac
done

echo "🤖 Generating ${AGENT_COUNT} sample agents with prefix '${PREFIX}'"

# Sample agent definitions
AGENT_ROLES=(
  "Revenue Amplifier"
  "Content Strategist"
  "Security Sentinel"
  "Data Harvester"
  "Growth Catalyst"
  "User Experience Guardian"
  "Integration Orchestrator"
  "Compliance Monitor"
  "Performance Optimizer"
  "Knowledge Synthesizer"
)

AGENT_NAMES=(
  "Financial Flow Master"
  "Narrative Navigator"
  "Shield Defender"
  "Data Explorer"
  "Expansion Expert"
  "Interface Innovator"
  "System Synchronizer"
  "Rule Enforcer"
  "Speed Optimizer"
  "Insight Aggregator"
)

# Sample trigger combinations
TRIGGER_SETS=(
  "FIVE_AND_GO,LEDGER_ECHO,G4_FUEL[5]"
  "FOREST_BRIDGE,CANOPY_LOCK,ROOT_OF_ROOTS"
  "EMOTIONAL_GRAVITY,SURGE_SPIKE"
  "GAMMA_SQUEEZE,STACKED_GEO_BURSTS"
  "FIVE_AND_GO,EMOTIONAL_GRAVITY,GAMMA_SQUEEZE"
  "FOREST_BRIDGE,SURGE_SPIKE,STACKED_GEO_BURSTS"
  "G4_FUEL[5],ROOT_OF_ROOTS,GAMMA_SQUEEZE"
  "LEDGER_ECHO,CANOPY_LOCK,SURGE_SPIKE"
  "FIVE_AND_GO,FOREST_BRIDGE,EMOTIONAL_GRAVITY,GAMMA_SQUEEZE"
  "LEDGER_ECHO,CANOPY_LOCK,SURGE_SPIKE,STACKED_GEO_BURSTS"
)

# Integration combinations
INTEGRATION_SETS=(
  "payments,analytics"
  "crm,email"
  "chat_support,social"
  "devops_infra,data"
  "ecomm,governance"
  "content_marketing,payments"
  "analytics,crm,email"
  "social,devops_infra,data"
  "governance,content_marketing,payments"
  "chat_support,ecomm,analytics"
)

# Generate agents
for i in $(seq 1 ${AGENT_COUNT}); do
  # Select random index for variety, but ensure it's within bounds
  index=$((i - 1))
  role_index=$((index % ${#AGENT_ROLES[@]}))
  name_index=$((index % ${#AGENT_NAMES[@]}))
  trigger_index=$((index % ${#TRIGGER_SETS[@]}))
  integration_index=$((index % ${#INTEGRATION_SETS[@]}))
  
  # Get values for this agent
  ROLE="${AGENT_ROLES[$role_index]}"
  NAME="${AGENT_NAMES[$name_index]} ${i}"
  AGENT_ID="${PREFIX}_agent${i}"
  
  echo "  🔹 Generating agent: ${AGENT_ID} (${NAME})"
  
  # Use PowerShell script to create the agent
  if command -v pwsh >/dev/null 2>&1; then
    # Create with PowerShell script
    trigger_arg=$(echo "${TRIGGER_SETS[$trigger_index]}" | tr ',' ' ')
    
    pwsh -ExecutionPolicy Bypass -Command "
      ./add_agent.ps1 -AgentId '${AGENT_ID}' -AgentName '${NAME}' -Role '${ROLE}' -Quiet
    "
    
    echo "    ✅ Agent created with PowerShell script"
  else
    echo "    ⚠️ PowerShell not available, skipping agent creation"
  fi
done

echo "🏁 Sample agent generation completed"
echo "📋 To see the agents, check the roster: agents/roster.json"
echo "🔄 You can now run ./flash_sync_agents.sh to synchronize all agents"
echo "📊 Or run ./create_mesh_graph.sh to generate a relationship graph"
