#!/bin/bash

# scan_security.sh
# Local security scanning script using Docker

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

WORKSPACE_DIR="$(pwd)"
echo -e "${YELLOW}Running security scan on: $WORKSPACE_DIR${NC}"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed or not in your PATH. Please install Docker first.${NC}"
    exit 1
fi

# Function to run a security scan
run_scan() {
    local name=$1
    local cmd=$2
    
    echo -e "${YELLOW}Running $name scan...${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ $name scan completed successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ $name scan failed${NC}"
        return 1
    fi
}

# Create results directory
mkdir -p "$WORKSPACE_DIR/security-scan-results"

# Run Python security scans
if [[ -f "$WORKSPACE_DIR/requirements.txt" ]] || ls "$WORKSPACE_DIR"/*.py &> /dev/null; then
    echo -e "${YELLOW}Running Python security scans...${NC}"
    
    # Bandit scan for Python code
    run_scan "Python Bandit" "docker run --rm -v '$WORKSPACE_DIR:/code' cytopia/bandit -r /code -f json -o /code/security-scan-results/bandit-results.json || true"
    
    # Safety scan for Python dependencies
    if [[ -f "$WORKSPACE_DIR/requirements.txt" ]]; then
        run_scan "Python Safety" "docker run --rm -v '$WORKSPACE_DIR:/code' pyupio/safety check -r /code/requirements.txt --json > '$WORKSPACE_DIR/security-scan-results/safety-results.json' || true"
    fi
fi

# Run Node.js security scans
if [[ -f "$WORKSPACE_DIR/package.json" ]]; then
    echo -e "${YELLOW}Running Node.js security scans...${NC}"
    
    # Create temporary Dockerfile for Node.js audit
    cat > "$WORKSPACE_DIR/security-scan-results/Dockerfile.nodescan" << EOF
FROM node:16-alpine
WORKDIR /code
COPY package.json package-lock.json* ./
RUN npm audit --json > /security-audit.json || true
CMD cat /security-audit.json
EOF

    # Run npm audit
    run_scan "npm audit" "docker build -f '$WORKSPACE_DIR/security-scan-results/Dockerfile.nodescan' -t nodescan '$WORKSPACE_DIR' && docker run --rm nodescan > '$WORKSPACE_DIR/security-scan-results/npm-audit-results.json'"
    
    # Cleanup
    rm "$WORKSPACE_DIR/security-scan-results/Dockerfile.nodescan"
    docker rmi nodescan &> /dev/null || true
fi

# Scan for secrets
echo -e "${YELLOW}Scanning for secrets and credentials...${NC}"
run_scan "Secrets" "docker run --rm -v '$WORKSPACE_DIR:/code' trufflesecurity/trufflehog:latest filesystem --directory=/code --json > '$WORKSPACE_DIR/security-scan-results/secrets-scan.json' || true"

# Generate summary report
echo -e "${YELLOW}Generating summary report...${NC}"
cat > "$WORKSPACE_DIR/security-scan-results/summary.txt" << EOF
Security Scan Summary
=====================
Date: $(date)
Repository: $(basename "$WORKSPACE_DIR")

EOF

# Check for critical vulnerabilities
echo -e "${YELLOW}Checking for critical vulnerabilities...${NC}"
CRITICAL_COUNT=0

# Check npm audit results
if [[ -f "$WORKSPACE_DIR/security-scan-results/npm-audit-results.json" ]]; then
    NPM_CRITICAL=$(grep -c "\"severity\":\"critical\"" "$WORKSPACE_DIR/security-scan-results/npm-audit-results.json" || echo "0")
    echo "NPM critical vulnerabilities: $NPM_CRITICAL" >> "$WORKSPACE_DIR/security-scan-results/summary.txt"
    CRITICAL_COUNT=$((CRITICAL_COUNT + NPM_CRITICAL))
fi

# Check Python safety results
if [[ -f "$WORKSPACE_DIR/security-scan-results/safety-results.json" ]]; then
    PYTHON_CRITICAL=$(grep -c "\"severity\":\"critical\"" "$WORKSPACE_DIR/security-scan-results/safety-results.json" || echo "0")
    echo "Python critical vulnerabilities: $PYTHON_CRITICAL" >> "$WORKSPACE_DIR/security-scan-results/summary.txt"
    CRITICAL_COUNT=$((CRITICAL_COUNT + PYTHON_CRITICAL))
fi

# Check secrets scan
if [[ -f "$WORKSPACE_DIR/security-scan-results/secrets-scan.json" ]]; then
    SECRETS_COUNT=$(grep -c "\"Detector\"" "$WORKSPACE_DIR/security-scan-results/secrets-scan.json" || echo "0")
    echo "Potential secrets found: $SECRETS_COUNT" >> "$WORKSPACE_DIR/security-scan-results/summary.txt"
    CRITICAL_COUNT=$((CRITICAL_COUNT + SECRETS_COUNT))
fi

# Print summary
echo -e "${YELLOW}Security scan complete!${NC}"
echo -e "Results saved to: ${GREEN}$WORKSPACE_DIR/security-scan-results/${NC}"

if [[ $CRITICAL_COUNT -gt 0 ]]; then
    echo -e "${RED}Critical issues found: $CRITICAL_COUNT${NC}"
    echo -e "${RED}Please review the security scan results before pushing your changes.${NC}"
    exit 1
else
    echo -e "${GREEN}No critical security issues found.${NC}"
    exit 0
fi
