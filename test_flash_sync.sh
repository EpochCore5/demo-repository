#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# test_flash_sync.sh — Test harness for flash_sync_agents.sh
# Usage: ./test_flash_sync.sh
# ----------------------------------------------------------------------------

set -e

echo "🧪 Running agent flash sync test harness"
echo "--------------------------------------"

# Create a test agent with PowerShell script if PowerShell available
if command -v pwsh >/dev/null 2>&1; then
  echo "✓ PowerShell found, creating test agent..."
  
  # Create test agent
  pwsh -ExecutionPolicy Bypass -Command "
    ./add_agent.ps1 -AgentId test_agent1 -AgentName 'Test Agent' -Role 'Test Runner' -SkipZip -Quiet
  "
  
  echo "✓ Test agent created"
else
  echo "⚠️ PowerShell not found, creating minimal test structure..."
  
  # Create minimal test structure manually
  mkdir -p agents/manifests
  mkdir -p assets/glyphs
  mkdir -p reports
  mkdir -p ledger
  
  # Create a minimal manifest
  cat > agents/manifests/test_agent1_manifest.json <<EOF
{
  "agent_id": "test_agent1",
  "name": "Test Agent",
  "role": "Test Runner",
  "status": "active",
  "ledger": {
    "last_verified": "2025-09-05T00:00:00Z"
  },
  "glyph": {
    "core": "⚡✶✷✦",
    "mesh": "☉☍☌☊☋"
  },
  "meshy_triggers": ["TEST_TRIGGER"]
}
EOF

  # Create minimal roster
  cat > agents/roster.json <<EOF
[
  {
    "agent_id": "test_agent1",
    "name": "Test Agent",
    "role": "Test Runner",
    "status": "active"
  }
]
EOF

  echo "✓ Minimal test structure created"
fi

# Run flash sync with report
echo "🔄 Running flash_sync_agents.sh with --report flag..."
./flash_sync_agents.sh --report

# Verify results
echo "📋 Verifying results..."

if [ -f "ledger/ledger_main.jsonl" ]; then
  EVENTS=$(grep -c "agent_sync" ledger/ledger_main.jsonl || echo "0")
  echo "✓ Ledger events found: $EVENTS"
else
  echo "❌ Ledger file not found"
  exit 1
fi

# Check for report
REPORT_COUNT=$(find reports -name "flash_sync_report_*.json" | wc -l)
if [ "$REPORT_COUNT" -gt 0 ]; then
  echo "✓ Report file generated"
else
  echo "❌ No report file found"
  exit 1
fi

echo "🏁 Test completed successfully"
