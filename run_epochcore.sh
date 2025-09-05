#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# run_epochcore.sh — Run the EpochCore agent system
# Usage: ./run_epochcore.sh [--agent registry|compliance|summary] [--sync]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_WITH_MANAGEMENT=false
AGENT_TYPE="registry"

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent)
      AGENT_TYPE="$2"
      shift 2
      ;;
    --sync)
      SYNC_WITH_MANAGEMENT=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./run_epochcore.sh [--agent registry|compliance|summary] [--sync]"
      exit 1
      ;;
  esac
done

# --- Ensure Python environment ---
if command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "⚠️ Error: Python not found"
  exit 1
fi

echo "🚀 Starting EpochCore Agent System"
echo "🧠 Running agent: ${AGENT_TYPE}"

# --- Create manifests directory if it doesn't exist ---
mkdir -p "${ROOT_DIR}/epochcore/manifests"
mkdir -p "${ROOT_DIR}/manifests"

# --- Run the selected agent ---
if [ "${AGENT_TYPE}" == "registry" ]; then
  echo "📊 Running Agent Registry..."
  ${PYTHON} -m epochcore.agent_registry
elif [ "${AGENT_TYPE}" == "compliance" ]; then
  echo "🔒 Running Compliance Auditor..."
  ${PYTHON} -m epochcore.compliance_auditor
elif [ "${AGENT_TYPE}" == "summary" ]; then
  echo "📑 Generating Audit Summary..."
  ${PYTHON} -c "from epochcore.audit_evolution_manager import get_audit_summary; print(get_audit_summary())"
else
  echo "⚠️ Invalid agent type: ${AGENT_TYPE}"
  exit 1
fi

# --- Sync with agent management system if requested ---
if [ "${SYNC_WITH_MANAGEMENT}" = true ]; then
  echo "🔄 Synchronizing with agent management system..."
  ${PYTHON} -m epochcore.integration
  
  # Run flash sync if available
  if [ -f "${ROOT_DIR}/flash_sync_agents.sh" ]; then
    echo "⚡ Running flash sync to update all agents..."
    "${ROOT_DIR}/flash_sync_agents.sh" --report
  fi
  
  # Generate mesh graph if available
  if [ -f "${ROOT_DIR}/create_mesh_graph.sh" ]; then
    echo "🌐 Generating agent mesh graph..."
    "${ROOT_DIR}/create_mesh_graph.sh" --output json
  fi
fi

echo "✅ EpochCore execution complete!"
