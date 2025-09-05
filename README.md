# EpochCore5 Demo Repository

This repository demonstrates advanced Copilot coding agent automation with agent management tools.

## Copilot Coding Agent Onboarding

This repository is onboarded for Copilot coding agent automation with enhanced agent management.

### Impact Propagation Engine

- See `impact_propagation_engine.py` for the core engine implementation.
- Follow [Copilot coding agent best practices](https://gh.io/copilot-coding-agent-tips) for automation and recursive improvements.

### Agent Management Tools

- **Agent Creation**: Use `add_agent.ps1` to add new agents with proper governance and audit trails.
- **Flash Sync**: Run `flash_sync_agents.sh` to synchronize all agents and update their verification status.
- **Mesh Graph**: Run `create_mesh_graph.sh` to generate relationship graphs between agents.
- **Import Agents**: Use `import_agents.sh` to import agents from another repository.
- **Generate Samples**: Run `generate_sample_agents.sh` to create sample agents for testing.
- **EpochCore System**: Run `run_epochcore.sh` to execute the recursive agent system with governance compliance.

### Usage

#### Creating a New Agent

````markdown
# EpochCore5 Demo Repository

This repository demonstrates advanced Copilot coding agent automation with agent management tools.

## Copilot Coding Agent Onboarding

This repository is onboarded for Copilot coding agent automation with enhanced agent management.

### Impact Propagation Engine

- See `impact_propagation_engine.py` for the core engine implementation.
- Follow [Copilot coding agent best practices](https://gh.io/copilot-coding-agent-tips) for automation and recursive improvements.

### Agent Management Tools

- **Agent Creation**: Use `add_agent.ps1` to add new agents with proper governance and audit trails.
- **Flash Sync**: Run `flash_sync_agents.sh` to synchronize all agents and update their verification status.
- **Mesh Graph**: Run `create_mesh_graph.sh` to generate relationship graphs between agents.
- **Import Agents**: Use `import_agents.sh` to import agents from another repository.
- **Generate Samples**: Run `generate_sample_agents.sh` to create sample agents for testing.
- **EpochCore System**: Run `run_epochcore.sh` to execute the recursive agent system with governance compliance.

### Usage

#### Creating a New Agent

```powershell
powershell -ExecutionPolicy Bypass -File .\add_agent.ps1 -AgentId agent42 -AgentName "Revenue Amplifier" -Role "Sales Funnel Commander"
```

#### Synchronizing All Agents

```bash
./flash_sync_agents.sh [--force] [--verify] [--report]
```

#### Generating Agent Mesh Graphs

```bash
./create_mesh_graph.sh [--output json|dot] [--visualize]
```

#### Importing Agents from Another Repository

```bash
./import_agents.sh --source /path/to/source/repo [--filter pattern] [--dry-run]
```

#### Generating Sample Agents

```bash
./generate_sample_agents.sh [--count N] [--prefix string]
```

#### Running the EpochCore Agent System

```bash
./run_epochcore.sh [--agent registry|compliance|summary] [--sync]
```

## Private Repository Security Configuration

This repository is configured as a private repository with enhanced security features to protect sensitive agent data, credentials, and audit logs.

### Security Features

- **Private Access**: Repository is configured with private access controls
- **Branch Protection**: Main branch is protected with required reviews
- **Signed Commits**: All commits must be cryptographically signed
- **Security Scanning**: Automated security scanning via GitHub Actions
- **Dependabot**: Automatic dependency updates with security patches
- **Code Ownership**: CODEOWNERS file defines responsibility for security-critical code
- **Audit Trails**: Full audit logs for all agent operations

### Making the Repository Private

To configure this repository as private with all security features:

```bash
# Review and modify the script if needed
./make_repository_private.sh
```

### Local Security Scanning

Before pushing changes, run the local security scanner:

```bash
./scan_security.sh
```

### Access Control

Repository access is managed according to the principles defined in [ACCESS_CONTROL.md](docs/ACCESS_CONTROL.md).

Security issues should be reported confidentially according to our [SECURITY.md](docs/SECURITY.md) guidelines.

### Team Permissions

- **Administrators**: Full repository access with security governance
- **Core Developers**: Code write access with restricted administrative functions
- **Agent Operators**: Read-write access to agent manifests and configurations
- **Auditors**: Read access to audit logs and reports
- **Security Team**: Security configuration management and reviews

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this repository.
````

#### Synchronizing All Agents

```bash
./flash_sync_agents.sh [--force] [--verify] [--report]
```

#### Generating Agent Mesh Graphs

```bash
./create_mesh_graph.sh [--output json|dot] [--visualize]
```

#### Importing Agents from Another Repository

```bash
./import_agents.sh --source /path/to/source/repo [--filter pattern] [--dry-run]
```

#### Generating Sample Agents

```bash
./generate_sample_agents.sh [--count N] [--prefix string]
```

#### Running the EpochCore Agent System

```bash
./run_epochcore.sh [--agent registry|compliance|summary] [--sync]
```
