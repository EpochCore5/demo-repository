#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# flash_sync_agents.sh — Synchronize all agents in repository
# Usage: ./flash_sync_agents.sh [--force] [--verify] [--report]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="${ROOT_DIR}/agents"
MANIFESTS_DIR="${AGENTS_DIR}/manifests"
REPORTS_DIR="${ROOT_DIR}/reports"
LEDGER_DIR="${ROOT_DIR}/ledger"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LEDGER_MAIN="${LEDGER_DIR}/ledger_main.jsonl"
SYNC_REPORT="${REPORTS_DIR}/flash_sync_report_$(date -u +"%Y%m%d_%H%M%S").json"

# --- Process arguments ---
FORCE=false
VERIFY=false
REPORT=false

for arg in "$@"; do
  case $arg in
    --force)
      FORCE=true
      ;;
    --verify)
      VERIFY=true
      ;;
    --report)
      REPORT=true
      ;;
  esac
done

# --- Ensure directories exist ---
mkdir -p "${MANIFESTS_DIR}"
mkdir -p "${REPORTS_DIR}"
mkdir -p "${LEDGER_DIR}"

# --- Helper functions ---
sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

sha256_string() {
  echo -n "$1" | sha256sum | awk '{print $1}'
}

append_to_ledger() {
  local entry="$1"
  local seal=$(echo -n "${entry}" | sha256sum | awk '{print $1}')
  echo "${entry%\}}, \"seal\": \"${seal}\"}" >> "${LEDGER_MAIN}"
}

# --- Check for roster file ---
ROSTER_FILE="${AGENTS_DIR}/roster.json"
if [ ! -f "${ROSTER_FILE}" ]; then
  echo "⚠️ Error: Roster file not found at ${ROSTER_FILE}"
  echo "   Run add_agent.ps1 script first to create agents"
  exit 1
fi

# --- Main sync function ---
echo "🔄 Flash Sync Started at $(date -u)"
echo "📋 Processing roster: ${ROSTER_FILE}"

# Initialize sync report
sync_results=()

# Read roster and process each agent
agent_count=$(jq length "${ROSTER_FILE}")
echo "🔍 Found ${agent_count} agents to sync"

for i in $(seq 0 $(($agent_count - 1))); do
  agent_id=$(jq -r ".[$i].agent_id" "${ROSTER_FILE}")
  
  echo "⚡ Syncing agent: ${agent_id}"
  
  # Verify manifest exists
  manifest_file="${MANIFESTS_DIR}/${agent_id}_manifest.json"
  if [ ! -f "${manifest_file}" ]; then
    echo "  ❌ Manifest not found for ${agent_id}, skipping"
    sync_results+=("{\"agent_id\":\"${agent_id}\",\"status\":\"failed\",\"reason\":\"manifest_missing\"}")
    continue
  fi
  
  # Update manifest timestamps
  temp_file="${manifest_file}.tmp"
  jq ".ledger.last_verified = \"${TIMESTAMP}\"" "${manifest_file}" > "${temp_file}"
  mv "${temp_file}" "${manifest_file}"
  
  # Calculate new hash and update ledger
  manifest_hash=$(sha256_file "${manifest_file}")
  
  # Create ledger entry
  ledger_entry="{\"ts\":\"${TIMESTAMP}\",\"event\":\"agent_sync\",\"agent_id\":\"${agent_id}\",\"manifest\":\"${manifest_file}\",\"manifest_sha256\":\"${manifest_hash}\"}"
  append_to_ledger "${ledger_entry}"
  
  # Add to sync results
  sync_results+=("{\"agent_id\":\"${agent_id}\",\"status\":\"success\",\"manifest_hash\":\"${manifest_hash}\"}")
  
  echo "  ✅ Agent ${agent_id} synced successfully"
done

# --- Generate sync report if requested ---
if [ "${REPORT}" = true ]; then
  echo "{"
  echo "  \"ts\": \"${TIMESTAMP}\","
  echo "  \"event\": \"flash_sync\","
  echo "  \"agents_count\": ${agent_count},"
  echo "  \"results\": [" 
  for i in "${!sync_results[@]}"; do
    echo "    ${sync_results[$i]}"
    if [ $i -lt $((${#sync_results[@]} - 1)) ]; then
      echo ","
    fi
  done
  echo "  ]"
  echo "}" > "${SYNC_REPORT}"
  
  echo "📊 Sync report generated: ${SYNC_REPORT}"
fi

echo "🏁 Flash Sync completed at $(date -u)"
echo "📒 Ledger updated: ${LEDGER_MAIN}"
