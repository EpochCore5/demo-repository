#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# import_agents.sh — Import agents from another repository
# Usage: ./import_agents.sh --source /path/to/source/repo [--filter pattern] [--dry-run]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR=""
FILTER=""
DRY_RUN=false

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --source)
      SOURCE_DIR="$2"
      shift 2
      ;;
    --filter)
      FILTER="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./import_agents.sh --source /path/to/source/repo [--filter pattern] [--dry-run]"
      exit 1
      ;;
  esac
done

# Validate source directory
if [ -z "$SOURCE_DIR" ]; then
  echo "⚠️ Error: Source directory is required (--source)"
  echo "Usage: ./import_agents.sh --source /path/to/source/repo [--filter pattern] [--dry-run]"
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  echo "⚠️ Error: Source directory does not exist: $SOURCE_DIR"
  exit 1
fi

# Define directory paths
SRC_AGENTS_DIR="${SOURCE_DIR}/agents"
SRC_MANIFESTS_DIR="${SRC_AGENTS_DIR}/manifests"
SRC_ASSETS_DIR="${SOURCE_DIR}/assets"
SRC_GLYPHS_DIR="${SRC_ASSETS_DIR}/glyphs"
SRC_REPORTS_DIR="${SOURCE_DIR}/reports"

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

# --- Check source roster ---
SRC_ROSTER="${SRC_AGENTS_DIR}/roster.json"
if [ ! -f "${SRC_ROSTER}" ]; then
  echo "⚠️ Error: Source roster not found at ${SRC_ROSTER}"
  exit 1
fi

DEST_ROSTER="${DEST_AGENTS_DIR}/roster.json"
# Initialize destination roster if it doesn't exist
if [ ! -f "${DEST_ROSTER}" ]; then
  echo "[]" > "${DEST_ROSTER}"
fi

echo "🔄 Importing agents from ${SOURCE_DIR}"
echo "📋 Source roster: ${SRC_ROSTER}"

# Parse source roster
agent_count=$(jq length "${SRC_ROSTER}")
echo "🔍 Found ${agent_count} agents in source roster"

# Initialize counters
imported=0
skipped=0
filtered=0

# Process each agent
for i in $(seq 0 $(($agent_count - 1))); do
  agent_id=$(jq -r ".[$i].agent_id" "${SRC_ROSTER}")
  
  # Apply filter if specified
  if [ -n "${FILTER}" ]; then
    if [[ ! "${agent_id}" =~ ${FILTER} ]]; then
      echo "  ⏭️ Filtered out agent: ${agent_id}"
      filtered=$((filtered + 1))
      continue
    fi
  fi
  
  agent_name=$(jq -r ".[$i].name" "${SRC_ROSTER}")
  agent_role=$(jq -r ".[$i].role" "${SRC_ROSTER}")
  
  echo "  🔹 Processing agent: ${agent_id} (${agent_name})"
  
  # Check for manifest
  src_manifest="${SRC_MANIFESTS_DIR}/${agent_id}_manifest.json"
  if [ ! -f "${src_manifest}" ]; then
    echo "    ⚠️ Manifest not found, skipping"
    skipped=$((skipped + 1))
    continue
  fi
  
  # Check for existing agent in destination
  if jq -e ".[] | select(.agent_id == \"${agent_id}\")" "${DEST_ROSTER}" > /dev/null; then
    echo "    ⚠️ Agent already exists in destination, skipping"
    skipped=$((skipped + 1))
    continue
  fi
  
  # Copy files if not in dry-run mode
  if [ "${DRY_RUN}" = false ]; then
    # Copy manifest
    dest_manifest="${DEST_MANIFESTS_DIR}/${agent_id}_manifest.json"
    cp "${src_manifest}" "${dest_manifest}"
    
    # Check and copy glyph files
    src_glyph_txt="${SRC_GLYPHS_DIR}/${agent_id}.txt"
    src_glyph_md="${SRC_GLYPHS_DIR}/${agent_id}.md"
    
    if [ -f "${src_glyph_txt}" ]; then
      cp "${src_glyph_txt}" "${DEST_GLYPHS_DIR}/${agent_id}.txt"
    fi
    
    if [ -f "${src_glyph_md}" ]; then
      cp "${src_glyph_md}" "${DEST_GLYPHS_DIR}/${agent_id}.md"
    fi
    
    # Check and copy reports
    src_init_report="${SRC_REPORTS_DIR}/${agent_id}_init.json"
    if [ -f "${src_init_report}" ]; then
      cp "${src_init_report}" "${DEST_REPORTS_DIR}/${agent_id}_init.json"
    fi
    
    src_log="${SRC_REPORTS_DIR}/${agent_id}_log.jsonl"
    if [ -f "${src_log}" ]; then
      cp "${src_log}" "${DEST_REPORTS_DIR}/${agent_id}_log.jsonl"
    fi
    
    # Add to destination roster
    temp_roster="${DEST_ROSTER}.tmp"
    jq --argjson newAgent "$(jq ".[$i]" "${SRC_ROSTER}")" '. += [$newAgent]' "${DEST_ROSTER}" > "${temp_roster}"
    mv "${temp_roster}" "${DEST_ROSTER}"
    
    # Create ledger entry
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    manifest_hash=$(sha256sum "${dest_manifest}" | awk '{print $1}')
    
    ledger_entry="{\"ts\":\"${timestamp}\",\"event\":\"agent_imported\",\"agent_id\":\"${agent_id}\",\"manifest\":\"${dest_manifest}\",\"manifest_sha256\":\"${manifest_hash}\"}"
    seal=$(echo -n "${ledger_entry}" | sha256sum | awk '{print $1}')
    echo "${ledger_entry%\}}, \"seal\": \"${seal}\"}" >> "${DEST_LEDGER_DIR}/ledger_main.jsonl"
  fi
  
  imported=$((imported + 1))
  echo "    ✅ Agent imported successfully"
done

# --- Summary ---
echo "🏁 Import completed"
echo "📊 Summary:"
echo "  • Total agents in source: ${agent_count}"
echo "  • Agents imported: ${imported}"
echo "  • Agents skipped: ${skipped}"
echo "  • Agents filtered: ${filtered}"

if [ "${DRY_RUN}" = true ]; then
  echo "ℹ️ This was a dry run - no files were copied"
else
  dest_agent_count=$(jq length "${DEST_ROSTER}")
  echo "📋 Destination roster now has ${dest_agent_count} agents"
fi
