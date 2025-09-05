# Agent Management System

This repository contains the EpochCore Agent Management System with strict governance and audit capabilities.

## Files

- `add_agent.ps1` - PowerShell script for creating and managing agents
- `impact_propagation_engine.py` - Impact propagation engine for dependency analysis

## PowerShell Agent Management Script

The `add_agent.ps1` script provides a comprehensive agent management system with:

### Features

- **Strict Governance**: Parameter validation, atomic writes, and audit trails
- **Idempotency**: Safe to run multiple times
- **Audit Trails**: Complete transaction logging with SHA256 seals
- **Directory Structure**: Automated creation of organized file structure
- **GitHub Integration**: Automatic governance scaffolding (CODEOWNERS, PR templates, CI workflows)

### Usage

```powershell
# Basic agent creation
.\add_agent.ps1 -AgentId "my_agent" -AgentName "My Agent" -Role "Automation"

# Agent creation with bundle and transcript
.\add_agent.ps1 -AgentId "revenue_optimizer" -AgentName "Revenue Optimizer" -Role "Sales Funnel Automation" -Bundle -Transcript
```

### Parameters

- `-AgentId` (Required): Unique identifier for the agent
- `-AgentName` (Required): Human-readable name for the agent
- `-Role` (Required): Agent's primary role or function
- `-Bundle` (Optional): Create a ZIP bundle of agent files
- `-Transcript` (Optional): Enable detailed operation logging
- `-Quiet` (Optional): Suppress non-essential output

### Directory Structure Created

```
agents/
├── manifests/          # Agent manifest files
│   └── {agent_id}_manifest.json
├── roster.json         # Central agent registry
bundles/                # ZIP bundles (if -Bundle flag used)
├── {agent_id}_bundle.zip
assets/
├── glyphs/            # Agent visual assets
reports/               # Agent activity reports
├── {agent_id}_init.json
├── {agent_id}_log.jsonl
ledger/                # Audit trail
├── ledger_main.jsonl
```

### Governance Features

The script automatically creates GitHub governance files if they don't exist:

- `.github/CODEOWNERS` - Code ownership definitions
- `.github/PULL_REQUEST_TEMPLATE.md` - PR template with governance checklist
- `.github/workflows/governance.yml` - CI workflow for secrets scanning and linting

### Integration Presets

Each agent includes integration configurations for:

- **Payments**: Stripe, PayPal, LemonSqueezy, Paddle, Square, Coinbase Commerce
- **Analytics**: GA4, PostHog, Mixpanel, Amplitude, Segment, Heap, etc.
- **CRM**: HubSpot, Salesforce, Pipedrive, Zoho, Monday CRM, etc.
- **Email**: Mailchimp, ConvertKit, SendGrid, Klaviyo, Amazon SES, etc.
- **Chat/Support**: Intercom, Drift, Crisp, Zendesk, HelpScout, etc.
- **Social**: Twitter API, LinkedIn API, Reddit API, Facebook Graph, etc.
- **DevOps/Infra**: GitHub Actions, GitLab CI, CircleCI, ArgoCD, etc.
- **Data**: BigQuery, Snowflake, Redshift, ClickHouse, Airbyte, etc.
- **E-commerce**: Shopify, WooCommerce, BigCommerce, Gumroad, etc.
- **Governance**: Multisig Vaults, On-chain Registry, Capsule Ledger, etc.
- **Content Marketing**: SEO Engine, Ads Automation, Content Pipeline, etc.

### Audit and Security

- All files are written atomically (temp file → move)
- SHA256 hashing for integrity verification
- JSONL ledger with per-line seals
- UTF-8 no-BOM encoding for cross-platform compatibility
- Optimistic concurrency for roster updates

### Requirements

- PowerShell 5.0+ or PowerShell Core 6.0+
- Write permissions to the target directory
- ZIP functionality (for bundle creation)

## Examples

### Creating a Revenue Agent
```powershell
.\add_agent.ps1 -AgentId "revenue_optimizer" -AgentName "Revenue Optimizer" -Role "Sales Funnel Automation"
```

### Creating a Support Agent with Audit
```powershell
.\add_agent.ps1 -AgentId "support_bot" -AgentName "Support Bot" -Role "Customer Success Manager" -Transcript
```

### Batch Agent Creation
```powershell
$agents = @(
    @{Id="seo_engine"; Name="SEO Engine"; Role="Content Optimization"},
    @{Id="social_amplifier"; Name="Social Amplifier"; Role="Social Media Automation"},
    @{Id="lead_qualifier"; Name="Lead Qualifier"; Role="Sales Pipeline Management"}
)

foreach ($agent in $agents) {
    .\add_agent.ps1 -AgentId $agent.Id -AgentName $agent.Name -Role $agent.Role -Quiet
}
```