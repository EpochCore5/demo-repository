#!/usr/bin/env pwsh
<#
.SYNOPSIS
EpochCore Agent Management System - Create and manage agents with strict governance

.DESCRIPTION
This script provides comprehensive agent management with:
- Strict governance and parameter validation
- Atomic file operations and audit trails
- Idempotent operations (safe to run multiple times)
- GitHub integration with governance scaffolding
- SHA256 integrity verification and JSONL ledger

.PARAMETER AgentId
Unique identifier for the agent (required)

.PARAMETER AgentName
Human-readable name for the agent (required)

.PARAMETER Role
Agent's primary role or function (required)

.PARAMETER Bundle
Create a ZIP bundle of agent files

.PARAMETER Transcript
Enable detailed operation logging

.PARAMETER Quiet
Suppress non-essential output

.EXAMPLE
.\add_agent.ps1 -AgentId "revenue_optimizer" -AgentName "Revenue Optimizer" -Role "Sales Funnel Automation"

.EXAMPLE
.\add_agent.ps1 -AgentId "support_bot" -AgentName "Support Bot" -Role "Customer Success Manager" -Bundle -Transcript
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[a-zA-Z0-9_-]+$')]
    [string]$AgentId,
    
    [Parameter(Mandatory=$true)]
    [ValidateLength(1,100)]
    [string]$AgentName,
    
    [Parameter(Mandatory=$true)]
    [ValidateLength(1,200)]
    [string]$Role,
    
    [switch]$Bundle,
    [switch]$Transcript,
    [switch]$Quiet
)

# --- utility functions ---
function UtcTs { return [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ") }
function Sha256-String($str) { 
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($str)
    $hash = $hasher.ComputeHash($bytes)
    return [System.BitConverter]::ToString($hash) -replace '-',''
}

function Sha256-File($path) {
    if(-not (Test-Path $path)) { return '' }
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    $stream = [System.IO.File]::OpenRead($path)
    try {
        $hash = $hasher.ComputeHash($stream)
        return [System.BitConverter]::ToString($hash) -replace '-',''
    } finally {
        $stream.Close()
    }
}

function Ensure-Dir($path) {
    if(-not (Test-Path $path)) {
        $null = New-Item -ItemType Directory -Path $path -Force
        if(-not $Quiet) { Write-Host "📁 Created directory: $path" -ForegroundColor Green }
    }
    return $path
}

function Write-JsonAtomic($obj, $path) {
    $tempPath = "$path.tmp"
    $json = $obj | ConvertTo-Json -Depth 32 -Compress:$false
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($tempPath, $json, $utf8NoBom)
    Move-Item $tempPath $path -Force
    if(-not $Quiet) { Write-Host "📄 Created: $path" -ForegroundColor Green }
}

# --- parameter validation ---
if($AgentId -match '[^a-zA-Z0-9_-]') {
    throw "AgentId must contain only alphanumeric characters, hyphens, and underscores"
}

if($Transcript) {
    Start-Transcript -Path "agent_creation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
}

$Root = Get-Location

if(-not $Quiet) {
    Write-Host "🚀 EpochCore Agent Management System" -ForegroundColor Cyan
    Write-Host "Creating agent: $AgentName ($AgentId)" -ForegroundColor Yellow
    Write-Host "Role: $Role" -ForegroundColor Yellow
}

# --- directory structure ---
$AgentsDir     = Join-Path $Root 'agents'
$ManifestsDir  = Join-Path $AgentsDir 'manifests'
$AssetsDir     = Join-Path $Root 'assets'
$GlyphsDir     = Join-Path $AssetsDir 'glyphs'
$ReportsDir    = Join-Path $Root 'reports'
$LedgerDir     = Join-Path $Root 'ledger'
$BundlesDir    = Join-Path $Root 'bundles'

$null = Ensure-Dir $AgentsDir
$null = Ensure-Dir $ManifestsDir
$null = Ensure-Dir $AssetsDir
$null = Ensure-Dir $GlyphsDir
$null = Ensure-Dir $ReportsDir
$null = Ensure-Dir $LedgerDir
$null = Ensure-Dir $BundlesDir

# --- governance presets (extensible) ---
$Integrations = [ordered]@{
    payments        = @('Stripe','PayPal','LemonSqueezy','Paddle','Square','Coinbase Commerce')
    analytics       = @('GA4','PostHog','Mixpanel','Amplitude','Segment','Heap')
    crm            = @('HubSpot','Salesforce','Pipedrive','Zoho','Monday CRM')
    email          = @('Mailchimp','ConvertKit','SendGrid','Klaviyo','Amazon SES')
    chat_support   = @('Intercom','Drift','Crisp','Zendesk','HelpScout')
    social         = @('Twitter API','LinkedIn API','Reddit API','Facebook Graph')
    devops_infra   = @('GitHub Actions','GitLab CI','CircleCI','ArgoCD')
    data           = @('BigQuery','Snowflake','Redshift','ClickHouse','Airbyte')
    ecommerce      = @('Shopify','WooCommerce','BigCommerce','Gumroad')
    governance     = @('Multisig Vaults','On-chain Registry','Capsule Ledger')
    content_marketing = @('SEO Engine','Ads Automation','Content Pipeline')
}

# --- create agent manifest ---
$TS = UtcTs
$Manifest = [ordered]@{
    meta = [ordered]@{
        agent_id = $AgentId
        agent_name = $AgentName
        role = $Role
        created_at = $TS
        version = '1.0.0'
        schema_version = '2024.1'
    }
    integrations = $Integrations
    config = [ordered]@{
        governance_mode = 'strict'
        audit_trail = $true
        encryption = 'aes256'
        backup_strategy = 'incremental'
    }
    reports = @{ 
        init_report = "/reports/${AgentId}_init.json"
        activity_log = "/reports/${AgentId}_log.jsonl" 
    }
    ledger  = @{ 
        capsule_id = 'keccak256(manifest.json)'
        seal_hash = "sha256(${AgentId}_bundle.zip)"
        last_verified = $TS 
    }
    covenant = @(
        'Timestamp → Log → Seal → Archive → Reinject',
        'Recurring revenue',
        'Hyper-scalability',
        'Founder sovereignty',
        'MeshCredit integrity'
    )
}

$ManifestPath = Join-Path $ManifestsDir "${AgentId}_manifest.json"
Write-JsonAtomic $Manifest $ManifestPath

# --- roster.json (append or create) with optimistic concurrency ---
$RosterPath = Join-Path $AgentsDir 'roster.json'
$retries = 3
for($i=0;$i -lt $retries;$i++){
    try {
        if(Test-Path $RosterPath){
            $raw = Get-Content -Raw -LiteralPath $RosterPath
            try { $roster = $raw | ConvertFrom-Json } catch { $roster = @() }
        } else {
            $roster = @()
        }
        
        # Convert to array if it's not already
        if($roster -isnot [System.Array]) {
            $roster = @($roster)
        }
        
        # Check if agent already exists
        $existing = $roster | Where-Object { $_.agent_id -eq $AgentId }
        if(-not $existing) {
            $roster += [ordered]@{
                agent_id = $AgentId
                agent_name = $AgentName
                role = $Role
                created_at = $TS
                manifest_path = $ManifestPath
                status = 'active'
            }
            
            Write-JsonAtomic $roster $RosterPath
            if(-not $Quiet) { Write-Host "📋 Updated roster with new agent" -ForegroundColor Green }
        } else {
            if(-not $Quiet) { Write-Host "⚠️  Agent already exists in roster" -ForegroundColor Yellow }
        }
        break
    }
    catch {
        if($i -eq $retries-1) { throw }
        Start-Sleep -Milliseconds (100 * ($i + 1))
    }
}

# --- calculate checksums ---
$ManifestSha = Sha256-File $ManifestPath
$BundleSha = ''
$BundlePath = ''

# --- create bundle if requested ---
if($Bundle) {
    $BundlePath = Join-Path $BundlesDir "${AgentId}_bundle.zip"
    
    # Create temporary directory for bundle contents in the current directory
    $TempBundleDir = Join-Path $Root "temp_bundle_$AgentId"
    if(Test-Path $TempBundleDir) {
        Remove-Item $TempBundleDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempBundleDir -Force | Out-Null
    
    # Copy manifest and related files
    Copy-Item $ManifestPath $TempBundleDir
    
    # Create README for the bundle
    $bundleReadme = @"
# Agent Bundle: $AgentName

**Agent ID**: $AgentId
**Role**: $Role
**Created**: $TS

## Contents
- ${AgentId}_manifest.json - Agent configuration and metadata

## Usage
This bundle contains all necessary files for deploying the $AgentName agent.
Refer to the manifest file for integration configurations and governance settings.
"@
    
    $bundleReadme | Set-Content -Path (Join-Path $TempBundleDir "README.md") -Encoding UTF8
    
    # Create the ZIP bundle
    try {
        Compress-Archive -Path "$TempBundleDir\*" -DestinationPath $BundlePath -Force
        $BundleSha = Sha256-File $BundlePath
        if(-not $Quiet) { Write-Host "📦 Created bundle: $BundlePath" -ForegroundColor Green }
    }
    finally {
        # Clean up temp directory
        if(Test-Path $TempBundleDir) {
            Remove-Item $TempBundleDir -Recurse -Force
        }
    }
}

# --- update manifest with final checksums ---
$Manifest.ledger.capsule_id = 'keccak256(notional)'  # placeholder (keccak not native)
$Manifest.ledger.seal_hash  = if($BundleSha){ $BundleSha } else { $ManifestSha }
Write-JsonAtomic $Manifest $ManifestPath

# --- ledger append (JSONL with per-line seal) ---
$LedgerMain = Join-Path $LedgerDir 'ledger_main.jsonl'
$Line = [ordered]@{
    ts = UtcTs
    event = 'agent_created'
    agent_id = $AgentId
    manifest = (Resolve-Path $ManifestPath).Path
    bundle_zip = if(Test-Path $BundlePath){ (Resolve-Path $BundlePath).Path } else { '' }
    manifest_sha256 = $ManifestSha
    bundle_sha256   = $BundleSha
}
$Line.seal = Sha256-String (($Line | ConvertTo-Json -Depth 32 -Compress))
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($LedgerMain, (($Line | ConvertTo-Json -Depth 32 -Compress) + "`n"), $Utf8NoBom)

# --- optional governance scaffolding in repo (non-destructive) ---
$RepoRoot = $Root
$GovDir = Join-Path $RepoRoot '.github'
$WorkflowsDir = Join-Path $GovDir 'workflows'
Ensure-Dir $GovDir; Ensure-Dir $WorkflowsDir

# CODEOWNERS stub (append if missing)
$CodeOwnersPath = Join-Path $GovDir 'CODEOWNERS'
if(-not (Test-Path $CodeOwnersPath)){
    @"
# Default code owners — update per team
*       @repo-admins
/agents @automation-chairs @security-lead
"@ | Set-Content -LiteralPath $CodeOwnersPath -Encoding UTF8
    if(-not $Quiet) { Write-Host "📋 Created CODEOWNERS file" -ForegroundColor Green }
}

# PR template stub
$PrTemplatePath = Join-Path $GovDir 'PULL_REQUEST_TEMPLATE.md'
if(-not (Test-Path $PrTemplatePath)){
    @"
## Summary
- [ ] Linked issue(s)
- [ ] Code review completed
- [ ] Tests passing
- [ ] Documentation updated

## Agent Management
- [ ] Agent configurations validated
- [ ] Security review completed
- [ ] Audit trail verified

## Governance Checklist
- [ ] CODEOWNERS approval required
- [ ] No secrets in commit
- [ ] Compliance requirements met
- [ ] Change log updated

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security scans clean
- [ ] Performance impact assessed

/cc @automation-chairs @security-lead
"@ | Set-Content -LiteralPath $PrTemplatePath -Encoding UTF8
    if(-not $Quiet) { Write-Host "📋 Created PR template" -ForegroundColor Green }
}

# Governance workflow stub
$GovernanceWorkflowPath = Join-Path $WorkflowsDir 'governance.yml'
if(-not (Test-Path $GovernanceWorkflowPath)){
    @"
name: Governance

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Secrets scanning
      run: |
        # Basic secrets detection
        if grep -r -i "password\|secret\|key\|token" --include="*.json" --include="*.yml" --include="*.ps1" .; then
          echo "⚠️ Potential secrets detected. Please review."
          exit 1
        fi
        echo "✅ No obvious secrets detected"
    
    - name: Agent manifest validation
      run: |
        # Validate agent manifests
        for manifest in agents/manifests/*.json; do
          if [ -f "\$manifest" ]; then
            echo "Validating \$manifest"
            if ! python -m json.tool "\$manifest" > /dev/null; then
              echo "❌ Invalid JSON in \$manifest"
              exit 1
            fi
          fi
        done
        echo "✅ All agent manifests are valid"
    
    - name: Ledger integrity check
      run: |
        # Check ledger integrity
        if [ -f "ledger/ledger_main.jsonl" ]; then
          echo "Checking ledger integrity..."
          while read -r line; do
            if ! echo "\$line" | python -m json.tool > /dev/null; then
              echo "❌ Invalid JSONL entry in ledger"
              exit 1
            fi
          done < ledger/ledger_main.jsonl
          echo "✅ Ledger integrity verified"
        fi
"@ | Set-Content -LiteralPath $GovernanceWorkflowPath -Encoding UTF8
    if(-not $Quiet) { Write-Host "📋 Created governance workflow" -ForegroundColor Green }
}

# --- create initial reports ---
$InitReportPath = Join-Path $ReportsDir "${AgentId}_init.json"
$InitReport = [ordered]@{
    agent_id = $AgentId
    agent_name = $AgentName
    role = $Role
    created_at = $TS
    status = 'initialized'
    integrations_available = $Integrations.Keys
    governance = @{
        mode = 'strict'
        audit_enabled = $true
        governance_files_created = @(
            if(Test-Path $CodeOwnersPath) { 'CODEOWNERS' }
            if(Test-Path $PrTemplatePath) { 'PULL_REQUEST_TEMPLATE.md' }
            if(Test-Path $GovernanceWorkflowPath) { 'governance.yml' }
        )
    }
    files_created = @{
        manifest = $ManifestPath
        bundle = if($Bundle) { $BundlePath } else { $null }
        init_report = $InitReportPath
    }
    checksums = @{
        manifest_sha256 = $ManifestSha
        bundle_sha256 = $BundleSha
    }
}

Write-JsonAtomic $InitReport $InitReportPath

# --- summary output ---
if(-not $Quiet) {
    Write-Host "`n✅ Agent creation completed successfully!" -ForegroundColor Green
    Write-Host "📋 Agent: $AgentName ($AgentId)" -ForegroundColor Cyan
    Write-Host "📁 Manifest: $ManifestPath" -ForegroundColor Gray
    if($Bundle) {
        Write-Host "📦 Bundle: $BundlePath" -ForegroundColor Gray
    }
    Write-Host "📊 Report: $InitReportPath" -ForegroundColor Gray
    Write-Host "🔐 Ledger: $LedgerMain" -ForegroundColor Gray
    Write-Host "`n🎯 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review the agent manifest and configure integrations as needed" -ForegroundColor White
    Write-Host "  2. Update .github/CODEOWNERS with appropriate reviewers" -ForegroundColor White
    Write-Host "  3. Test agent functionality with your specific use case" -ForegroundColor White
    Write-Host "  4. Monitor the ledger for audit trail compliance" -ForegroundColor White
}

if($Transcript) {
    Stop-Transcript
}

# Return success
exit 0