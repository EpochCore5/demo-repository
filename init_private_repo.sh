#!/bin/bash

# init_private_repo.sh
# Initialize the private repository structure if it doesn't already exist

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

WORKSPACE_DIR="$(pwd)"
echo -e "${YELLOW}Initializing private repository structure in: $WORKSPACE_DIR${NC}"

# Create required directories if they don't exist
create_dir() {
    local dir=$1
    if [ ! -d "$WORKSPACE_DIR/$dir" ]; then
        echo -e "Creating directory: ${GREEN}$dir${NC}"
        mkdir -p "$WORKSPACE_DIR/$dir"
    else
        echo -e "Directory already exists: ${YELLOW}$dir${NC}"
    fi
}

# Create required directories
create_dir "agents/manifests"
create_dir "agents/private"
create_dir "agents/keys"
create_dir "assets/glyphs"
create_dir "assets/private"
create_dir "reports"
create_dir "reports/private"
create_dir "ledger"
create_dir "ledger/private"
create_dir ".github/ISSUE_TEMPLATE"
create_dir ".github/workflows"
create_dir "docs"

# Create README files in each directory to explain its purpose
create_readme() {
    local dir=$1
    local description=$2
    
    if [ ! -f "$WORKSPACE_DIR/$dir/README.md" ]; then
        echo -e "Creating README in: ${GREEN}$dir${NC}"
        cat > "$WORKSPACE_DIR/$dir/README.md" << EOF
# $dir

$description

## Purpose

This directory is part of the EpochCore5 private repository structure.

## Security Considerations

Files in this directory are subject to the repository's access control policies.
See [ACCESS_CONTROL.md](/docs/ACCESS_CONTROL.md) for details on access permissions.
EOF
    else
        echo -e "README already exists in: ${YELLOW}$dir${NC}"
    fi
}

# Create README files
create_readme "agents/manifests" "This directory contains agent manifest files that define agent capabilities, permissions, and metadata."
create_readme "agents/private" "This directory contains private agent configuration files. Access is restricted to administrators and agent operators."
create_readme "agents/keys" "This directory contains cryptographic keys for agent verification. Access is highly restricted."
create_readme "assets/glyphs" "This directory contains visual representations and UI assets for agents."
create_readme "assets/private" "This directory contains private assets for internal use. Access is restricted."
create_readme "reports" "This directory contains agent activity and audit reports."
create_readme "reports/private" "This directory contains private and sensitive audit reports. Access is restricted to administrators and auditors."
create_readme "ledger" "This directory contains transaction ledgers and verification records."
create_readme "ledger/private" "This directory contains private ledger data. Access is restricted to administrators and auditors."

# Create a .gitkeep file in empty directories to ensure they are tracked by git
touch_gitkeep() {
    local dir=$1
    if [ ! -f "$WORKSPACE_DIR/$dir/.gitkeep" ] && [ -z "$(ls -A "$WORKSPACE_DIR/$dir" 2>/dev/null)" ]; then
        echo -e "Creating .gitkeep in: ${GREEN}$dir${NC}"
        touch "$WORKSPACE_DIR/$dir/.gitkeep"
    fi
}

# Add .gitkeep files
touch_gitkeep "agents/manifests"
touch_gitkeep "agents/private"
touch_gitkeep "agents/keys"
touch_gitkeep "assets/glyphs"
touch_gitkeep "assets/private"
touch_gitkeep "reports"
touch_gitkeep "reports/private"
touch_gitkeep "ledger"
touch_gitkeep "ledger/private"

echo -e "${GREEN}Repository structure initialization complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the created directory structure"
echo "2. Add agent manifests to the agents/manifests directory"
echo "3. Set up team permissions in GitHub"
echo "4. Run ./make_repository_private.sh to configure repository privacy settings"

exit 0
