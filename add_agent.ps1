# ========================= EPOCHCORE — ULTRA MASTERY (Windows One-Block) =========================
# add_agent.ps1 (Hardened v2)  — strict governance, idempotency, atomic writes, audit extras
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\add_agent.ps1 -AgentId agent42 -AgentName "Revenue Amplifier" -Role "Sales Funnel Commander"
# -----------------------------------------------------------------------------------------------

[CmdletBinding(SupportsShouldProcess=$true, PositionalBinding=$false)]
param(
  [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9._-]{2,64}$')] [string] $AgentId,
  [Parameter(Mandatory=$true)][ValidateLength(1,128)] [string] $AgentName,
  [Parameter(Mandatory=$true)][ValidateLength(1,128)] [string] $Role,
  [Parameter()] [ValidateScript({ Test-Path $_ })] [string] $Root = ".",
  [switch] $Transcript,
  [string] $TranscriptPath,
  [switch] $SkipZip,
  [switch] $Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- helper: start transcript for full audit trail ---
if($Transcript){
  if(-not $TranscriptPath){
    $TranscriptPath = Join-Path -Path (Resolve-Path $Root) -ChildPath (Join-Path 'reports' ("transcript_" + (Get-Date -Format 'yyyyMMdd_HHmmss') + ".txt"))
  }
  $tpDir = Split-Path -Parent $TranscriptPath
  if(-not (Test-Path $tpDir)) { New-Item -ItemType Directory -Path $tpDir | Out-Null }
  try{ Start-Transcript -Path $TranscriptPath -Force | Out-Null } catch {}
}

# --- helpers ---
function UtcTs { (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') }
function Ensure-Dir([string]$p) { if (!(Test-Path -LiteralPath $p)) { New-Item -ItemType Directory -Path $p | Out-Null } }
function Write-Json([object]$obj,[string]$path){
  $json = $obj | ConvertTo-Json -Depth 32
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($path, $json, $utf8NoBom)
}
function Write-JsonAtomic([object]$obj,[string]$path){
  $tmp = "$path.tmp"; Write-Json $obj $tmp; Move-Item -LiteralPath $tmp -Destination $path -Force
}
function Sha256-File([string]$p){ (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() }
function Sha256-String([string]$s){ $sha=[System.Security.Cryptography.SHA256]::Create(); $bytes=[System.Text.Encoding]::UTF8.GetBytes($s); ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '' }

# --- root/materialized paths ---
$Root = (Resolve-Path $Root).Path
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
  analytics       = @('GA4','PostHog','Mixpanel','Amplitude','Segment','Heap','Plausible','Matomo','Hotjar','FullStory')
  crm             = @('HubSpot','Salesforce','Pipedrive','Zoho','Monday CRM','Notion CRM','Close','Freshsales','Copper','Keap')
  email           = @('Mailchimp','ConvertKit','SendGrid','Klaviyo','Amazon SES','Mailgun','Postmark','Campaign Monitor','Brevo','Customer.io')
  chat_support    = @('Intercom','Drift','Crisp','Zendesk','HelpScout','Freshdesk','LiveChat','Tidio','Olark','HubSpot Chat')
  social          = @('Twitter API','LinkedIn API','Reddit API','Facebook Graph','Instagram Graph','TikTok API','YouTube Data','Discord Bot','Slack App','Telegram Bot')
  devops_infra    = @('GitHub Actions','GitLab CI','CircleCI','ArgoCD','Terraform','Ansible','Sentry','Datadog','Vercel','Netlify','Fly.io','DigitalOcean','AWS Lambda','Cloud Run')
  data            = @('BigQuery','Snowflake','Redshift','ClickHouse','Airbyte','Fivetran','dbt','Metabase','Superset','Delta Lake')
  ecomm           = @('Shopify','WooCommerce','BigCommerce','Gumroad','LemonSqueezy Store')
  governance      = @('Multisig Vaults','On-chain Registry (recordSeal)','Capsule Ledger JSONL','Timelocks')
  content_marketing = @('SEO Engine','Ads Automation (Google/FB/TikTok)','Content Pipeline','Viral Amplification')
}

$MeshyTriggers = @('FIVE_AND_GO','LEDGER_ECHO','G4_FUEL[5]','FOREST_BRIDGE','CANOPY_LOCK','ROOT_OF_ROOTS','EMOTIONAL_GRAVITY','SURGE_SPIKE','GAMMA_SQUEEZE','STACKED_GEO_BURSTS')

# --- glyph generator (deterministic per AgentId + fresh mesh variant) ---
$GlyphRunes = @('⚡','🜂','🜁','🜃','🜄','✶','✷','✦','✧','✩','✪','✫','✬','✭','✮','✯','⬡','⬢','◆','◇','◈','⬣','⬟','⬠','☉','☍','☌','☊','☋','☌','☷','☵','☲','☰','☷','☽','☾','♆','♇','♁','♃','♄','♅','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','✜','✚','✙','✛','†','‡')
$seedBytes = ([System.Security.Cryptography.SHA1]::Create()).ComputeHash([Text.Encoding]::UTF8.GetBytes($AgentId))
$seed = [System.BitConverter]::ToUInt32($seedBytes,0) % 2147483647
$rand = [System.Random]::new([int]$seed)
function Next-Rune { param([int]$n=1) 1..$n | ForEach-Object { $GlyphRunes[$rand.Next(0,$GlyphRunes.Count)] } }
$CoreSigil = -join (Next-Rune -n 12)
$AccentRow = -join (Next-Rune -n 6)
$GeneratedGlyph = "$($CoreSigil.Substring(0,4))`n$($CoreSigil.Substring(4,4))`n$($CoreSigil.Substring(8,4))`n$AccentRow"
$rand2 = [System.Random]::new([int]([Math]::Abs((Get-Date).GetHashCode()) % 2147483647))
$MeshVariant = -join (0..9 | ForEach-Object { $GlyphRunes[$rand2.Next(0,$GlyphRunes.Count)] })

# --- write glyph files (UTF-8 no BOM) ---
$GlyphTxtPath = Join-Path $GlyphsDir "$AgentId.txt"
$GlyphMdPath  = Join-Path $GlyphsDir "$AgentId.md"
Set-Content -LiteralPath $GlyphTxtPath -Value $GeneratedGlyph -Encoding UTF8
@"
# Glyph — $AgentId

**mesh-variant:** $MeshVariant
"@ | Set-Content -LiteralPath $GlyphMdPath -Encoding UTF8

# --- manifest (Ultra Mastery) ---
$TS = UtcTs
$Manifest = [ordered]@{
  agent_id   = $AgentId
  name       = $AgentName
  role       = $Role
  status     = 'active'
  integrations = $Integrations
  meshy_triggers = $MeshyTriggers
  glyph = @{ core = $GeneratedGlyph; mesh = $MeshVariant; files = @{ txt = (Resolve-Path $GlyphTxtPath).Path; md  = (Resolve-Path $GlyphMdPath).Path } }
  reports = @{ init_report = "/reports/${AgentId}_init.json"; activity_log = "/reports/${AgentId}_log.jsonl" }
  ledger  = @{ capsule_id = 'keccak256(manifest.json)'; seal_hash = "sha256(${AgentId}_bundle.zip)"; last_verified = $TS }
  covenant = @('Timestamp → Log → Seal → Archive → Reinject','Recurring revenue','Hyper-scalability','Founder sovereignty','MeshCredit integrity')
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
      if($roster -isnot [System.Collections.IEnumerable]){ $roster = @() }
    } else { $roster = @() }
    $exists = $false
    foreach($r in $roster){ if($r.agent_id -eq $AgentId){ $exists=$true; break } }
    if(-not $exists){
      $roster = @($roster + ($Manifest | ConvertTo-Json -Depth 32 | ConvertFrom-Json))
      Write-JsonAtomic $roster $RosterPath
    }
    break
  } catch {
    if($i -ge $retries-1){ throw }
    Start-Sleep -Milliseconds 150
  }
}

# --- init report ---
$InitReportPath = Join-Path $ReportsDir "${AgentId}_init.json"
$InitReport = [ordered]@{ ts = $TS; agent_id = $AgentId; event = 'agent_init'; role = $Role; name = $AgentName; integrations = $Integrations.Keys; meshy_triggers = $MeshyTriggers; glyph_preview = $MeshVariant }
Write-JsonAtomic $InitReport $InitReportPath

# --- bundle (zip) + seals ---
$BundlePath = Join-Path $BundlesDir "${AgentId}_bundle.zip"
if(Test-Path $BundlePath){ Remove-Item -LiteralPath $BundlePath -Force }
if(-not $SkipZip){ Compress-Archive -Path $ManifestPath, $GlyphTxtPath, $GlyphMdPath, $InitReportPath -DestinationPath $BundlePath }
$ManifestJson = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8
$ManifestSha  = Sha256-String $ManifestJson
$BundleSha    = if(Test-Path $BundlePath){ Sha256-File $BundlePath } else { '' }

# update manifest.ledger with real seals
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
$Line.seal = Sha256-String (($Line | ConvertTo-Json -Depth 32))
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::AppendAllText($LedgerMain, (($Line | ConvertTo-Json -Depth 32) + "`n"), $Utf8NoBom)

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
}

# PR template stub
$PrTemplatePath = Join-Path $GovDir 'PULL_REQUEST_TEMPLATE.md'
if(-not (Test-Path $PrTemplatePath)){
  @"
## Summary
- [ ] Linked issue(s)
- [ ] Governance checks pass (CI, code scanning, secrets scan)

## Checklist
- [ ] Tests added/updated
- [ ] Docs updated (CHANGELOG, README)
- [ ] No secrets/PII committed
"@ | Set-Content -LiteralPath $PrTemplatePath -Encoding UTF8
}

# minimal CI: secrets scan + PS script check (placeholder)
$CiYaml = @"
name: governance
on: [push, pull_request]
jobs:
  scan-and-verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Secret scan (git-secrets placeholder)
        run: |
          echo "Run your secret scanning tool here"
      - name: PowerShell lint (PSScriptAnalyzer)
        uses: PowerShell/psscriptanalyzer-action@v1.0
        with: { }
"@
$CiPath = Join-Path $WorkflowsDir 'governance.yml'
if(-not (Test-Path $CiPath)){
  Set-Content -LiteralPath $CiPath -Value $CiYaml -Encoding UTF8
}

# --- console out ---
if($PSCmdlet.ShouldProcess("Agent [$AgentId]","Create & Seal")){
  if(-not $Quiet){
    Write-Host ""; Write-Host "✅ Agent created & sealed" -ForegroundColor Green
    Write-Host ("   ID:        {0}" -f $AgentId)
    Write-Host ("   Name:      {0}" -f $AgentName)
    Write-Host ("   Role:      {0}" -f $Role)
    Write-Host ("   Manifest:  {0}" -f ((Resolve-Path $ManifestPath).Path))
    Write-Host ("   Glyph:     {0}" -f ((Resolve-Path $GlyphTxtPath).Path))
    if(-not $SkipZip){ Write-Host ("   Bundle:    {0}" -f ((Resolve-Path $BundlePath).Path)) }
    if($BundleSha){ Write-Host ("   SHA256(bundle): {0}" -f $BundleSha) }
    Write-Host ""; Write-Host ("📒 Roster:    {0}" -f ((Resolve-Path $RosterPath).Path))
    Write-Host ("🧾 Ledger:    {0}" -f ((Resolve-Path $LedgerMain).Path))
    Write-Host ""; Write-Host ("⚡ Triggers armed: {0}" -f ($MeshyTriggers -join ', '))
    Write-Host "🏛️ Covenant:   Timestamp → Log → Seal → Archive → Reinject"
  }
}

if($Transcript){ try{ Stop-Transcript | Out-Null } catch{} }

# ===============================================================================================