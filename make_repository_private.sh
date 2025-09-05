#!/bin/bash

# make_repository_private.sh
# Script to configure a GitHub repository as private with appropriate security settings

set -e

# Configuration
REPO_NAME="demo-repository"
ORGANIZATION="EpochCore5"  # Replace with your organization name if applicable
BRANCH_PROTECTION_ENABLED=true
REQUIRE_REVIEWS=true
MIN_REVIEWERS=1
REQUIRE_SIGNED_COMMITS=true

# Text colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Making Repository Private ===${NC}"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}GitHub CLI (gh) is not installed. Please install it first:${NC}"
    echo "  https://cli.github.com/manual/installation"
    exit 1
fi

# Check if user is authenticated with GitHub CLI
if ! gh auth status &> /dev/null; then
    echo -e "${RED}You are not authenticated with GitHub CLI. Please run:${NC}"
    echo "  gh auth login"
    exit 1
fi

# Function to get the full repository name
get_full_repo_name() {
    if [[ -n "$ORGANIZATION" ]]; then
        echo "$ORGANIZATION/$REPO_NAME"
    else
        # Get the authenticated user's username
        local username=$(gh api user | jq -r '.login')
        echo "$username/$REPO_NAME"
    fi
}

FULL_REPO_NAME=$(get_full_repo_name)

echo -e "${YELLOW}Setting repository to private: $FULL_REPO_NAME${NC}"

# Make the repository private
gh api --method PATCH "repos/$FULL_REPO_NAME" \
  -f private=true \
  -f security_and_analysis='{"advanced_security": {"status": "enabled"}, "secret_scanning": {"status": "enabled"}}' \
  -f delete_branch_on_merge=true

echo -e "${GREEN}Repository is now private with advanced security features enabled${NC}"

# Set up branch protection if enabled
if [[ "$BRANCH_PROTECTION_ENABLED" == true ]]; then
    echo -e "${YELLOW}Setting up branch protection rules...${NC}"
    
    PROTECTION_CONFIG='{
        "required_status_checks": {
            "strict": true,
            "contexts": ["security-scan"]
        },
        "enforce_admins": false,
        "required_pull_request_reviews": null,
        "restrictions": null
    }'
    
    # Add pull request review requirements if enabled
    if [[ "$REQUIRE_REVIEWS" == true ]]; then
        PROTECTION_CONFIG=$(echo $PROTECTION_CONFIG | jq --arg min "$MIN_REVIEWERS" '.required_pull_request_reviews = {"required_approving_review_count": ($min|tonumber), "dismiss_stale_reviews": true}')
    fi
    
    # Apply branch protection rules
    gh api --method PUT "repos/$FULL_REPO_NAME/branches/main/protection" \
      -H "Accept: application/vnd.github.luke-cage-preview+json" \
      --input <(echo "$PROTECTION_CONFIG")
      
    echo -e "${GREEN}Branch protection rules applied to main branch${NC}"
fi

# Enable signed commits if required
if [[ "$REQUIRE_SIGNED_COMMITS" == true ]]; then
    echo -e "${YELLOW}Requiring signed commits...${NC}"
    
    gh api --method POST "repos/$FULL_REPO_NAME/branches/main/protection/required_signatures" \
      -H "Accept: application/vnd.github.zzzax-preview+json"
      
    echo -e "${GREEN}Signed commits are now required${NC}"
fi

echo -e "${GREEN}Repository is now configured as private with security settings${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update team permissions in the GitHub web interface"
echo "2. Review branch protection rules"
echo "3. Set up required status checks for the security-scan workflow"
echo "4. Consider enabling vulnerability alerts and automated security fixes"

exit 0
