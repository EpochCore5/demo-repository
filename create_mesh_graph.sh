#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# create_mesh_graph.sh — Generate mesh relationship graph for agents
# Usage: ./create_mesh_graph.sh [--output format] [--visualize]
# ----------------------------------------------------------------------------

set -e

# --- Configuration ---
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="${ROOT_DIR}/agents"
MANIFESTS_DIR="${AGENTS_DIR}/manifests"
REPORTS_DIR="${ROOT_DIR}/reports"
GRAPHS_DIR="${ROOT_DIR}/graphs"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
OUTPUT_FORMAT="json"
VISUALIZE=false

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    --visualize)
      VISUALIZE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# --- Ensure directories exist ---
mkdir -p "${GRAPHS_DIR}"
mkdir -p "${REPORTS_DIR}"

# --- Check for roster file ---
ROSTER_FILE="${AGENTS_DIR}/roster.json"
if [ ! -f "${ROSTER_FILE}" ]; then
  echo "⚠️ Error: Roster file not found at ${ROSTER_FILE}"
  exit 1
fi

# --- Main function ---
echo "🌐 Generating Agent Mesh Graph at $(date -u)"

# Read roster and build mesh relationships
agent_count=$(jq length "${ROSTER_FILE}")
echo "🔍 Found ${agent_count} agents to analyze"

# Initialize graph structure
nodes=()
links=()

# Generate nodes from agent roster
for i in $(seq 0 $(($agent_count - 1))); do
  agent_id=$(jq -r ".[$i].agent_id" "${ROSTER_FILE}")
  agent_name=$(jq -r ".[$i].name" "${ROSTER_FILE}")
  agent_role=$(jq -r ".[$i].role" "${ROSTER_FILE}")
  
  # Add node to graph
  nodes+=("{\"id\":\"${agent_id}\",\"name\":\"${agent_name}\",\"role\":\"${agent_role}\"}")
  
  # Check for manifest to extract mesh relationships
  manifest_file="${MANIFESTS_DIR}/${agent_id}_manifest.json"
  if [ -f "${manifest_file}" ]; then
    # Extract mesh variant for link creation
    mesh_variant=$(jq -r '.glyph.mesh' "${manifest_file}")
    
    # Process each meshy_trigger to create potential links
    triggers=$(jq -r '.meshy_triggers[]' "${manifest_file}")
    for trigger in ${triggers}; do
      # Find potential partners with compatible triggers
      for j in $(seq 0 $(($agent_count - 1))); do
        if [ $i -ne $j ]; then
          partner_id=$(jq -r ".[$j].agent_id" "${ROSTER_FILE}")
          partner_manifest="${MANIFESTS_DIR}/${partner_id}_manifest.json"
          
          if [ -f "${partner_manifest}" ]; then
            # Check if partner has compatible trigger
            if jq -e ".meshy_triggers | index(\"${trigger}\")" "${partner_manifest}" > /dev/null; then
              # Create bidirectional link based on shared trigger
              links+=("{\"source\":\"${agent_id}\",\"target\":\"${partner_id}\",\"type\":\"mesh\",\"trigger\":\"${trigger}\"}")
            fi
          fi
        fi
      done
    done
  fi
done

# Generate output graph
output_file="${GRAPHS_DIR}/agent_mesh_$(date -u +"%Y%m%d").${OUTPUT_FORMAT}"

case "${OUTPUT_FORMAT}" in
  json)
    # Create JSON graph format
    echo "{" > "${output_file}"
    echo "  \"timestamp\": \"${TIMESTAMP}\"," >> "${output_file}"
    echo "  \"nodes\": [" >> "${output_file}"
    for i in "${!nodes[@]}"; do
      echo "    ${nodes[$i]}" >> "${output_file}"
      if [ $i -lt $((${#nodes[@]} - 1)) ]; then
        echo "," >> "${output_file}"
      fi
    done
    echo "  ]," >> "${output_file}"
    echo "  \"links\": [" >> "${output_file}"
    for i in "${!links[@]}"; do
      echo "    ${links[$i]}" >> "${output_file}"
      if [ $i -lt $((${#links[@]} - 1)) ]; then
        echo "," >> "${output_file}"
      fi
    done
    echo "  ]" >> "${output_file}"
    echo "}" >> "${output_file}"
    ;;
  dot)
    # Create GraphViz DOT format
    echo "digraph AgentMesh {" > "${output_file}"
    echo "  // Graph styling" >> "${output_file}"
    echo "  graph [rankdir=LR, fontname=\"Arial\", label=\"Agent Mesh Graph - ${TIMESTAMP}\"];" >> "${output_file}"
    echo "  node [shape=box, style=\"rounded,filled\", fontname=\"Arial\"];" >> "${output_file}"
    echo "  edge [fontname=\"Arial\"];" >> "${output_file}"
    echo "" >> "${output_file}"
    
    # Add nodes
    echo "  // Nodes" >> "${output_file}"
    for node in "${nodes[@]}"; do
      id=$(echo $node | jq -r '.id')
      name=$(echo $node | jq -r '.name')
      role=$(echo $node | jq -r '.role')
      echo "  \"${id}\" [label=\"${name}\\n(${role})\"];" >> "${output_file}"
    done
    
    echo "" >> "${output_file}"
    echo "  // Links" >> "${output_file}"
    # Add edges
    for link in "${links[@]}"; do
      source=$(echo $link | jq -r '.source')
      target=$(echo $link | jq -r '.target')
      trigger=$(echo $link | jq -r '.trigger')
      echo "  \"${source}\" -> \"${target}\" [label=\"${trigger}\"];" >> "${output_file}"
    done
    
    echo "}" >> "${output_file}"
    ;;
  *)
    echo "⚠️ Unsupported output format: ${OUTPUT_FORMAT}"
    exit 1
    ;;
esac

echo "📊 Mesh graph generated: ${output_file}"

# Visualize if requested
if [ "${VISUALIZE}" = true ] && [ "${OUTPUT_FORMAT}" = "dot" ]; then
  if command -v dot >/dev/null 2>&1; then
    png_file="${GRAPHS_DIR}/agent_mesh_$(date -u +"%Y%m%d").png"
    dot -Tpng "${output_file}" -o "${png_file}"
    echo "🖼️  Visualization created: ${png_file}"
  else
    echo "⚠️ GraphViz 'dot' command not found. Install GraphViz to visualize."
  fi
fi

echo "🏁 Mesh graph creation completed at $(date -u)"
