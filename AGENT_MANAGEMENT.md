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
# Basic usage
.\add_agent.ps1 -AgentId "agent42" -AgentName "Revenue Amplifier" -Role "Sales Funnel Commander"

# With audit transcript
.\add_agent.ps1 -AgentId "data_sync" -AgentName "Data Synchronizer" -Role "CRM Integration Specialist" -Transcript

# Quiet mode (no console output)
.\add_agent.ps1 -AgentId "analytics_bot" -AgentName "Analytics Bot" -Role "Data Analyzer" -Quiet

# Skip ZIP bundle creation
.\add_agent.ps1 -AgentId "test_agent" -AgentName "Test Agent" -Role "Testing" -SkipZip

# What-if mode (show what would be done)
.\add_agent.ps1 -AgentId "preview" -AgentName "Preview Agent" -Role "Preview" -WhatIf
```

### Parameters

- **AgentId** (Required): Unique identifier (2-64 chars, alphanumeric, dots, dashes, underscores)
- **AgentName** (Required): Human-readable name (1-128 chars)
- **Role** (Required): Agent role description (1-128 chars)
- **Root**: Base directory (default: current directory)
- **Transcript**: Enable audit transcript
- **TranscriptPath**: Custom transcript file path
- **SkipZip**: Don't create bundle ZIP file
- **Quiet**: Suppress console output

### Directory Structure Created

```
├── agents/
│   ├── manifests/          # Agent manifests (JSON)
│   └── roster.json         # Master agent roster
├── assets/
│   └── glyphs/            # Agent glyphs (deterministic visual IDs)
├── bundles/               # Agent bundle ZIP files
├── ledger/               # Audit ledger (JSONL format)
└── reports/              # Agent reports and logs
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