#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# import_from_epochcore_os.sh — Specialized import from EpochCore_OS repository
# Usage: ./import_from_epochcore_os.sh --source /path/to/EpochCore_OS [--agents agent1,agent2]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR=""
SPECIFIC_AGENTS=""
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --source)
      SOURCE_DIR="$2"
      shift 2
      ;;
    --agents)
      SPECIFIC_AGENTS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./import_from_epochcore_os.sh --source /path/to/EpochCore_OS [--agents agent1,agent2]"
      exit 1
      ;;
  esac
done

# Validate source directory
if [ -z "$SOURCE_DIR" ]; then
  echo "⚠️ Error: Source directory is required (--source)"
  echo "Usage: ./import_from_epochcore_os.sh --source /path/to/EpochCore_OS [--agents agent1,agent2]"
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "⚠️ Error: Source directory does not exist: $SOURCE_DIR"
  exit 1
fi

echo "🌐 Importing from EpochCore_OS at: ${SOURCE_DIR}"

# Define directory paths based on EpochCore_OS structure
# Note: These paths are assumptions and may need to be adjusted based on actual structure
SRC_AGENTS_DIR="${SOURCE_DIR}/agents"
SRC_CORE_DIR="${SOURCE_DIR}/core"
SRC_ASSETS_DIR="${SOURCE_DIR}/assets"
SRC_CONFIG_DIR="${SOURCE_DIR}/config"

DEST_AGENTS_DIR="${DEST_DIR}/agents"
DEST_MANIFESTS_DIR="${DEST_AGENTS_DIR}/manifests"
DEST_ASSETS_DIR="${DEST_DIR}/assets"
DEST_GLYPHS_DIR="${DEST_ASSETS_DIR}/glyphs"
DEST_REPORTS_DIR="${DEST_DIR}/reports"
DEST_LEDGER_DIR="${DEST_DIR}/ledger"

# Ensure directories exist
mkdir -p "${DEST_MANIFESTS_DIR}"
mkdir -p "${DEST_GLYPHS_DIR}"
mkdir -p "${DEST_REPORTS_DIR}"
mkdir -p "${DEST_LEDGER_DIR}"

# Initialize variables for tracking
imported=0
skipped=0
errors=0

# --- Helper Functions ---
sha256sum_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

append_to_ledger() {
  local entry="$1"
  local seal=$(echo -n "${entry}" | sha256sum | awk '{print $1}')
  echo "${entry%\}}, \"seal\": \"${seal}\"}" >> "${DEST_LEDGER_DIR}/ledger_main.jsonl"
}

# --- Main import logic ---

# 1. Check for agents directory or roster
if [ ! -d "${SRC_AGENTS_DIR}" ]; then
  echo "⚠️ Warning: No agents directory found in EpochCore_OS. Checking for alternative structures..."
  
  # Try to find agent definitions in other directories
  POTENTIAL_AGENT_PATHS=(
    "${SRC_CORE_DIR}/agents"
    "${SRC_CONFIG_DIR}/agents"
    "${SOURCE_DIR}/modules/agents"
    "${SOURCE_DIR}/system/agents"
  )
  
  for path in "${POTENTIAL_AGENT_PATHS[@]}"; do
    if [ -d "${path}" ]; then
      echo "✅ Found alternative agents location: ${path}"
      SRC_AGENTS_DIR="${path}"
      break
    fi
  done
fi

# 2. Find agent roster or create from found agents
SRC_ROSTER="${SRC_AGENTS_DIR}/roster.json"
DEST_ROSTER="${DEST_AGENTS_DIR}/roster.json"

# Initialize destination roster if it doesn't exist
if [ ! -f "${DEST_ROSTER}" ]; then
  echo "[]" > "${DEST_ROSTER}"
fi

# If no explicit roster, try to detect agents
if [ ! -f "${SRC_ROSTER}" ]; then
  echo "⚠️ No roster.json found. Attempting to detect agents from directory structure..."
  
  # Create a temporary roster from available agent directories or files
  TMP_ROSTER="/tmp/epochcore_os_roster.json"
  echo "[" > "${TMP_ROSTER}"
  
  # Option 1: Look for agent directories
  if [ -d "${SRC_AGENTS_DIR}" ]; then
    first=true
    for agent_dir in "${SRC_AGENTS_DIR}"/*/; do
      if [ -d "${agent_dir}" ]; then
        agent_id=$(basename "${agent_dir}")
        
        # Skip if specific agents were requested and this isn't one of them
        if [ -n "${SPECIFIC_AGENTS}" ]; then
          if [[ ! ",${SPECIFIC_AGENTS}," == *",${agent_id},"* ]]; then
            continue
          fi
        fi
        
        # Try to extract agent name and role from metadata files
        agent_name="${agent_id}"
        agent_role="Unknown"
        
        if [ -f "${agent_dir}/metadata.json" ]; then
          if command -v jq >/dev/null 2>&1; then
            agent_name=$(jq -r '.name // .agent_name // "'"${agent_id}"'"' "${agent_dir}/metadata.json" 2>/dev/null || echo "${agent_id}")
            agent_role=$(jq -r '.role // .agent_role // "Unknown"' "${agent_dir}/metadata.json" 2>/dev/null || echo "Unknown")
          fi
        elif [ -f "${agent_dir}/config.json" ]; then
          if command -v jq >/dev/null 2>&1; then
            agent_name=$(jq -r '.name // .agent_name // "'"${agent_id}"'"' "${agent_dir}/config.json" 2>/dev/null || echo "${agent_id}")
            agent_role=$(jq -r '.role // .agent_role // "Unknown"' "${agent_dir}/config.json" 2>/dev/null || echo "Unknown")
          fi
        fi
        
        # Add comma for JSON array format except for first item
        if [ "$first" = true ]; then
          first=false
        else
          echo "," >> "${TMP_ROSTER}"
        fi
        
        # Write agent info to temporary roster
        cat >> "${TMP_ROSTER}" << EOF
  {
    "agent_id": "${agent_id}",
    "name": "${agent_name}",
    "role": "${agent_role}",
    "status": "active"
  }
EOF
      fi
    done
  fi
  
  # Option 2: Look for agent JSON files if no directories found
  if [ "$(cat "${TMP_ROSTER}")" = "[" ]; then
    first=true
    for agent_file in "${SRC_AGENTS_DIR}"/*.json; do
      if [ -f "${agent_file}" ] && [ "$(basename "${agent_file}")" != "roster.json" ]; then
        agent_id=$(basename "${agent_file}" .json)
        
        # Skip if specific agents were requested and this isn't one of them
        if [ -n "${SPECIFIC_AGENTS}" ]; then
          if [[ ! ",${SPECIFIC_AGENTS}," == *",${agent_id},"* ]]; then
            continue
          fi
        fi
        
        # Try to extract agent name and role from the file
        if command -v jq >/dev/null 2>&1; then
          agent_name=$(jq -r '.name // .agent_name // "'"${agent_id}"'"' "${agent_file}" 2>/dev/null || echo "${agent_id}")
          agent_role=$(jq -r '.role // .agent_role // "Unknown"' "${agent_file}" 2>/dev/null || echo "Unknown")
        else
          agent_name="${agent_id}"
          agent_role="Unknown"
        fi
        
        # Add comma for JSON array format except for first item
        if [ "$first" = true ]; then
          first=false
        else
          echo "," >> "${TMP_ROSTER}"
        fi
        
        # Write agent info to temporary roster
        cat >> "${TMP_ROSTER}" << EOF
  {
    "agent_id": "${agent_id}",
    "name": "${agent_name}",
    "role": "${agent_role}",
    "status": "active"
  }
EOF
      fi
    done
  fi
  
  # Close JSON array
  echo -e "\n]" >> "${TMP_ROSTER}"
  
  # Use the temporary roster
  SRC_ROSTER="${TMP_ROSTER}"
  
  # If still empty, abort
  if [ "$(cat "${SRC_ROSTER}")" = "[\n]" ] || [ "$(cat "${SRC_ROSTER}")" = "[]" ]; then
    echo "⚠️ No agents detected in EpochCore_OS repository."
    exit 1
  fi
fi

# 3. Process agents from roster
echo "📋 Processing agents from EpochCore_OS..."

# Validate roster is valid JSON
if ! jq empty "${SRC_ROSTER}" 2>/dev/null; then
  echo "⚠️ Error: Source roster is not valid JSON"
  exit 1
fi

# Get agent count
agent_count=$(jq length "${SRC_ROSTER}" 2>/dev/null || echo 0)
echo "🔍 Found ${agent_count} agents in source"

# Process each agent
for i in $(seq 0 $(($agent_count - 1))); do
  agent_id=$(jq -r ".[$i].agent_id" "${SRC_ROSTER}" 2>/dev/null || echo "unknown_${i}")
  
  # Skip if specific agents were requested and this isn't one of them
  if [ -n "${SPECIFIC_AGENTS}" ]; then
    if [[ ! ",${SPECIFIC_AGENTS}," == *",${agent_id},"* ]]; then
      echo "  ⏭️ Skipping agent ${agent_id} (not in requested list)"
      skipped=$((skipped + 1))
      continue
    fi
  fi
  
  agent_name=$(jq -r ".[$i].name" "${SRC_ROSTER}" 2>/dev/null || echo "${agent_id}")
  agent_role=$(jq -r ".[$i].role" "${SRC_ROSTER}" 2>/dev/null || echo "Unknown")
  
  echo "  🔹 Processing agent: ${agent_id} (${agent_name})"
  
  # Check for existing agent in destination
  if jq -e ".[] | select(.agent_id == \"${agent_id}\")" "${DEST_ROSTER}" > /dev/null 2>&1; then
    echo "    ⚠️ Agent already exists in destination, skipping"
    skipped=$((skipped + 1))
    continue
  fi
  
  # Look for agent files in different potential locations
  agent_found=false
  manifest_path=""
  
  # Potential locations for agent manifest
  MANIFEST_LOCATIONS=(
    "${SRC_AGENTS_DIR}/manifests/${agent_id}_manifest.json"
    "${SRC_AGENTS_DIR}/${agent_id}/manifest.json"
    "${SRC_AGENTS_DIR}/${agent_id}.json"
    "${SRC_AGENTS_DIR}/${agent_id}/config.json"
    "${SRC_AGENTS_DIR}/${agent_id}/metadata.json"
  )
  
  for path in "${MANIFEST_LOCATIONS[@]}"; do
    if [ -f "${path}" ]; then
      manifest_path="${path}"
      agent_found=true
      break
    fi
  done
  
  if [ "${agent_found}" = true ]; then
    # Create or adapt manifest to our format
    dest_manifest="${DEST_MANIFESTS_DIR}/${agent_id}_manifest.json"
    
    # Try to convert/adapt the manifest format
    if command -v jq >/dev/null 2>&1; then
      # Extract key fields and create a compatible manifest
      jq -n \
        --arg agent_id "${agent_id}" \
        --arg name "${agent_name}" \
        --arg role "${agent_role}" \
        --arg ts "${TIMESTAMP}" \
        '{
          agent_id: $agent_id,
          name: $name,
          role: $role,
          status: "active",
          integrations: {},
          meshy_triggers: [],
          glyph: {
            core: "",
            mesh: ""
          },
          reports: {
            init_report: "/reports/'${agent_id}'_init.json",
            activity_log: "/reports/'${agent_id}'_log.jsonl"
          },
          ledger: {
            capsule_id: "",
            seal_hash: "",
            last_verified: $ts
          },
          covenant: ["Timestamp → Log → Seal → Archive → Reinject"]
        }' > "${dest_manifest}"
      
      # Try to merge in any available fields from the original manifest
      if [ -f "${manifest_path}" ]; then
        tmp_manifest="${dest_manifest}.tmp"
        jq -s '.[0] * .[1]' "${dest_manifest}" "${manifest_path}" > "${tmp_manifest}" 2>/dev/null || true
        if [ -f "${tmp_manifest}" ]; then
          mv "${tmp_manifest}" "${dest_manifest}"
        fi
      fi
    else
      # Simple copy if jq not available
      cp "${manifest_path}" "${dest_manifest}" 2>/dev/null || echo "{}" > "${dest_manifest}"
    fi
    
    # Look for assets/glyphs
    for ext in txt md png svg; do
      glyph_locations=(
        "${SRC_ASSETS_DIR}/glyphs/${agent_id}.${ext}"
        "${SRC_ASSETS_DIR}/${agent_id}/glyph.${ext}"
        "${SRC_AGENTS_DIR}/${agent_id}/glyph.${ext}"
      )
      
      for glyph_path in "${glyph_locations[@]}"; do
        if [ -f "${glyph_path}" ]; then
          cp "${glyph_path}" "${DEST_GLYPHS_DIR}/${agent_id}.${ext}" 2>/dev/null || true
        fi
      done
    done
    
    # Create basic init report if none exists
    init_report="${DEST_REPORTS_DIR}/${agent_id}_init.json"
    echo "{\"ts\":\"${TIMESTAMP}\",\"agent_id\":\"${agent_id}\",\"event\":\"agent_imported\",\"name\":\"${agent_name}\",\"role\":\"${agent_role}\"}" > "${init_report}"
    
    # Add to destination roster
    temp_roster="${DEST_ROSTER}.tmp"
    jq --arg agent_id "${agent_id}" \
       --arg name "${agent_name}" \
       --arg role "${agent_role}" \
      '. += [{"agent_id": $agent_id, "name": $name, "role": $role, "status": "active"}]' "${DEST_ROSTER}" > "${temp_roster}"
    mv "${temp_roster}" "${DEST_ROSTER}"
    
    # Create ledger entry
    manifest_hash=$(sha256sum_file "${dest_manifest}")
    ledger_entry="{\"ts\":\"${TIMESTAMP}\",\"event\":\"agent_imported\",\"source\":\"EpochCore_OS\",\"agent_id\":\"${agent_id}\",\"manifest\":\"${dest_manifest}\",\"manifest_sha256\":\"${manifest_hash}\"}"
    append_to_ledger "${ledger_entry}"
    
    imported=$((imported + 1))
    echo "    ✅ Agent imported successfully"
  else
    echo "    ❌ Could not find agent files"
    errors=$((errors + 1))
  fi
done

# --- Summary ---
echo "🏁 Import from EpochCore_OS completed"
echo "📊 Summary:"
echo "  • Total agents processed: ${agent_count}"
echo "  • Agents imported: ${imported}"
echo "  • Agents skipped: ${skipped}"
echo "  • Errors: ${errors}"

dest_agent_count=$(jq length "${DEST_ROSTER}")
echo "📋 Destination roster now has ${dest_agent_count} agents"
echo "🔄 You can now run ./flash_sync_agents.sh to synchronize all agents"
echo "📊 And run ./create_mesh_graph.sh to generate a relationship graph"
