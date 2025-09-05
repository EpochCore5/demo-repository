#!/bin/bash
# ========================= EPOCHCORE — ULTRA MASTERY =========================
# secure_repo.sh — Configure privacy and security settings
# Usage: ./secure_repo.sh [--strict] [--audit]
# ----------------------------------------------------------------------------

set -e

STRICT_MODE=false
AUDIT_MODE=false
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Process arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --strict)
      STRICT_MODE=true
      shift
      ;;
    --audit)
      AUDIT_MODE=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./secure_repo.sh [--strict] [--audit]"
      exit 1
      ;;
  esac
done

echo "🔒 Configuring repository security and privacy settings"

# --- Create security directories if they don't exist ---
mkdir -p "${ROOT_DIR}/.github/workflows"
mkdir -p "${ROOT_DIR}/.github/ISSUE_TEMPLATE"

# --- Generate .gitignore with security focus ---
cat > "${ROOT_DIR}/.gitignore" << 'EOF'
# Security focused gitignore

# Secrets and credentials
*.pem
*.key
*.cert
*.env
.env
.env.*
credentials.json
*_credentials.*
*_secrets.*

# Logs that might contain sensitive data
logs/
*.log

# Local development
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Agent specific ignores
private_manifests/
*.private.json
EOF

# --- Add Secret Scanning workflow ---
cat > "${ROOT_DIR}/.github/workflows/security_scan.yml" << 'EOF'
name: Security Scanning

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Run weekly

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Run security scan
        uses: github/codeql-action/init@v2
        with:
          languages: python, javascript, typescript

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v2
        
      - name: Check for secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
  governance-compliance:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          
      - name: Run compliance audit
        run: |
          python -m epochcore.compliance_auditor
          
      - name: Validate governance
        run: |
          if grep -q "GOVERNANCE: Strict adherence" $(find epochcore -name "*.py"); then
            echo "✅ Governance headers present"
          else
            echo "❌ Missing governance headers"
            exit 1
          fi
EOF

# --- Add SECURITY.md link to README ---
if grep -q "## Security" "${ROOT_DIR}/README.md"; then
  echo "Security section already exists in README"
else
  echo -e "\n## Security\n\nThis repository implements strict security and privacy measures. See [SECURITY.md](docs/SECURITY.md) for details.\n" >> "${ROOT_DIR}/README.md"
fi

# --- Create PR template with security focus ---
cat > "${ROOT_DIR}/.github/PULL_REQUEST_TEMPLATE.md" << 'EOF'
## Pull Request

### Security Checklist

- [ ] No secrets or credentials are included in this PR
- [ ] Security scanning passed
- [ ] Governance compliance verified
- [ ] Documentation updated (if necessary)

### Changes

<!-- Describe your changes here -->

### Related Issues

<!-- Link to related issues here -->
EOF

# --- Run security audit if requested ---
if [ "$AUDIT_MODE" = true ]; then
  echo "🔍 Running security audit..."
  
  # Check for potential secrets
  if command -v gitleaks >/dev/null 2>&1; then
    gitleaks detect --source="${ROOT_DIR}" || echo "⚠️ Potential secrets detected"
  else
    echo "⚠️ gitleaks not installed, skipping secrets scan"
  fi
  
  # Check for governance headers
  echo "Checking governance headers..."
  if grep -q "GOVERNANCE: Strict adherence" $(find "${ROOT_DIR}/epochcore" -name "*.py" 2>/dev/null); then
    echo "✅ Governance headers present"
  else
    echo "⚠️ Missing governance headers in some files"
  fi
fi

# --- Apply strict mode if requested ---
if [ "$STRICT_MODE" = true ]; then
  echo "🛡️ Applying strict security mode..."
  
  # Create a pre-commit hook
  PRE_COMMIT_HOOK="${ROOT_DIR}/.git/hooks/pre-commit"
  mkdir -p "${ROOT_DIR}/.git/hooks"
  
  cat > "${PRE_COMMIT_HOOK}" << 'EOF'
#!/bin/bash

echo "Running pre-commit security checks..."

# Check for potential secrets
echo "Checking for secrets..."
files=$(git diff --cached --name-only)
for file in $files; do
  if grep -E '(password|secret|token|key|credential|passwd|auth).*[=:].*[A-Za-z0-9+/]{20,}' "$file"; then
    echo "⚠️ Potential secret found in $file"
    exit 1
  fi
done

# Check for governance headers in Python files
echo "Checking governance headers..."
python_files=$(git diff --cached --name-only | grep -E '\.py$')
for file in $python_files; do
  if ! grep -q "GOVERNANCE: Strict adherence" "$file"; then
    echo "⚠️ Missing governance header in $file"
    exit 1
  fi
done

echo "✅ Pre-commit checks passed"
exit 0
EOF

  chmod +x "${PRE_COMMIT_HOOK}"
  echo "✅ Installed pre-commit security hook"
fi

echo "✅ Repository security configuration complete"
echo "🛡️ Repository is now configured for private and secure operation"
