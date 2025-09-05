#!/usr/bin/env python3
"""
Secrets Validation Script
Part of the EpochCoreMASTER Ultra-Mega-Alpha-Tier Agent Flash Sync Automation system

This script validates that all required secrets and environment variables are
properly configured for the EpochCore Flash Sync system. It checks for existence,
format validation, and permissions testing where possible.

Usage:
    python validate_secrets_sync.py [--verbose] [--strict]

Requirements:
    - Python 3.8+
    - requests library (for API validation)
"""

import os
import sys
import re
import logging
import argparse
from typing import Dict, List, Optional, Any, Tuple

try:
    import requests
except ImportError:
    print("Warning: requests library not found. API validation will be skipped.")
    requests = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("secrets-validator")

# Required secrets configuration
REQUIRED_SECRETS = [
    {
        "name": "GITHUB_TOKEN",
        "alt_names": ["SECRET_GITHUB_TOKEN", "GH_TOKEN"],
        "description": "GitHub API token for repository operations",
        "required": True,
        "format_regex": r"^(gh[ps]_[a-zA-Z0-9]{36}|[a-zA-Z0-9_]{40})$",
        "format_description": "40-character classic token or 36-character fine-grained token",
        "validation_function": "validate_github_token"
    },
    {
        "name": "STRIPE_API_KEY",
        "alt_names": ["STRIPE_SECRET_KEY", "STRIPE_SK"],
        "description": "Stripe API key for payment processing",
        "required": False,  # Optional for non-payment workflows
        "format_regex": r"^sk_(test|live)_[a-zA-Z0-9]{24,}$",
        "format_description": "Starts with sk_test_ or sk_live_ followed by at least 24 characters",
        "validation_function": "validate_stripe_api_key"
    },
    {
        "name": "AWS_ACCESS_KEY_ID",
        "alt_names": ["AWS_ACCESS_KEY"],
        "description": "AWS access key for S3 artifact storage",
        "required": False,
        "format_regex": r"^[A-Z0-9]{20}$",
        "format_description": "20 uppercase alphanumeric characters",
        "validation_function": None
    },
    {
        "name": "AWS_SECRET_ACCESS_KEY",
        "alt_names": ["AWS_SECRET_KEY"],
        "description": "AWS secret key for S3 artifact storage",
        "required": False,
        "format_regex": r"^[a-zA-Z0-9+/]{40}$",
        "format_description": "40 base64 characters",
        "validation_function": None
    },
    {
        "name": "EPOCHCORE_LICENSE_KEY",
        "alt_names": ["EPOCH_LICENSE", "EC_LICENSE_KEY"],
        "description": "EpochCore license key for premium features",
        "required": False,
        "format_regex": r"^EC-[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}$",
        "format_description": "Format: EC-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
        "validation_function": None
    },
    {
        "name": "SLACK_WEBHOOK_URL",
        "alt_names": ["SLACK_NOTIFICATION_URL"],
        "description": "Slack webhook URL for notifications",
        "required": False,
        "format_regex": r"^https://hooks\.slack\.com/services/T[A-Z0-9]{8,10}/B[A-Z0-9]{8,10}/[a-zA-Z0-9]{24}$",
        "format_description": "Valid Slack webhook URL format",
        "validation_function": None
    }
]


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate secrets for EpochCore Flash Sync"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce validation of optional secrets if present"
    )
    return parser.parse_args()


def get_secret_value(secret_config: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Get a secret value from environment variables, checking all possible names.
    
    Returns:
        Tuple of (value, source) where source is the environment variable name
    """
    # Check primary name
    value = os.environ.get(secret_config["name"])
    if value:
        return value, secret_config["name"]
    
    # Check alternative names
    for alt_name in secret_config.get("alt_names", []):
        value = os.environ.get(alt_name)
        if value:
            return value, alt_name
    
    return None, None


def validate_secret_format(value: str, regex: str) -> bool:
    """Validate that a secret matches the expected format."""
    pattern = re.compile(regex)
    return bool(pattern.match(value))


def validate_github_token(token: str) -> Tuple[bool, Optional[str]]:
    """Validate a GitHub token by making a test API call."""
    if not requests:
        return False, "Requests library not available for validation"
        
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return True, f"Authenticated as {user_data.get('login')}"
        else:
            return False, f"API error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Request failed: {str(e)}"


def validate_stripe_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
    """Validate a Stripe API key by making a test API call."""
    if not requests:
        return False, "Requests library not available for validation"
        
    # For security, we'll only check if this is a test key
    is_test = api_key.startswith("sk_test_")
    
    # For test keys, we can actually validate with the API
    if is_test:
        try:
            response = requests.get(
                "https://api.stripe.com/v1/customers",
                auth=(api_key, ""),
                params={"limit": 1}
            )
            if response.status_code == 200:
                return True, "Test key successfully authenticated with Stripe API"
            else:
                return False, f"API error: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Request failed: {str(e)}"
    else:
        # For live keys, we'll just assume it's valid if it matches the format
        return True, "Live key format validated (API call skipped for security)"


def validate_secrets(args: argparse.Namespace) -> Tuple[bool, Dict[str, Any]]:
    """
    Validate all secrets and environment variables.
    
    Returns:
        Tuple of (success, results_dict)
    """
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    results = {
        "success": True,
        "required_secrets_present": True,
        "optional_secrets_present": 0,
        "format_validation": True,
        "api_validation": True,
        "secrets": []
    }
    
    for secret_config in REQUIRED_SECRETS:
        secret_name = secret_config["name"]
        is_required = secret_config["required"]
        
        # Get the value
        value, source = get_secret_value(secret_config)
        
        # Initialize result for this secret
        secret_result = {
            "name": secret_name,
            "alternative_names": secret_config["alt_names"],
            "description": secret_config["description"],
            "required": is_required,
            "present": value is not None,
            "source": source,
            "format_valid": None,
            "api_valid": None,
            "api_message": None
        }
        
        # Check if required secret is missing
        if is_required and value is None:
            logger.error(f"❌ Required secret {secret_name} is missing")
            results["required_secrets_present"] = False
            results["success"] = False
            secret_result["format_valid"] = False
            secret_result["api_valid"] = False
            results["secrets"].append(secret_result)
            continue
        
        # Skip validation for missing optional secrets
        if value is None:
            logger.info(f"ℹ️ Optional secret {secret_name} is not set")
            results["secrets"].append(secret_result)
            continue
        
        # Count optional secrets that are present
        if not is_required and value is not None:
            results["optional_secrets_present"] += 1
        
        # Log source if found in alternative name
        if source and source != secret_name:
            logger.info(f"ℹ️ Found {secret_name} as {source}")
        
        # Validate format
        if "format_regex" in secret_config and secret_config["format_regex"]:
            format_valid = validate_secret_format(value, secret_config["format_regex"])
            secret_result["format_valid"] = format_valid
            
            if not format_valid:
                logger.error(
                    f"❌ Secret {secret_name} has invalid format. "
                    f"Expected: {secret_config['format_description']}"
                )
                results["format_validation"] = False
                
                # Only mark as failure if required or in strict mode
                if is_required or args.strict:
                    results["success"] = False
            else:
                logger.info(f"✅ Secret {secret_name} has valid format")
        
        # Validate with API call if function is specified
        if "validation_function" in secret_config and secret_config["validation_function"]:
            func_name = secret_config["validation_function"]
            if func_name == "validate_github_token":
                api_valid, message = validate_github_token(value)
            elif func_name == "validate_stripe_api_key":
                api_valid, message = validate_stripe_api_key(value)
            else:
                logger.warning(f"⚠️ Unknown validation function: {func_name}")
                api_valid, message = False, "Validation function not implemented"
            
            secret_result["api_valid"] = api_valid
            secret_result["api_message"] = message
            
            if not api_valid:
                logger.error(f"❌ Secret {secret_name} failed API validation: {message}")
                
                # Only mark as failure if required or in strict mode
                if is_required or args.strict:
                    results["api_validation"] = False
                    results["success"] = False
            else:
                logger.info(f"✅ Secret {secret_name} passed API validation: {message}")
        
        results["secrets"].append(secret_result)
    
    return results["success"], results


def print_validation_report(success: bool, results: Dict[str, Any]) -> None:
    """Print a formatted validation report."""
    print("\n" + "=" * 60)
    print("SECRETS VALIDATION REPORT")
    print("=" * 60)
    
    print(f"\nOverall Validation: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"Required Secrets:   {'✅ PRESENT' if results['required_secrets_present'] else '❌ MISSING'}")
    print(f"Optional Secrets:   {results['optional_secrets_present']} present")
    print(f"Format Validation:  {'✅ PASSED' if results['format_validation'] else '❌ FAILED'}")
    print(f"API Validation:     {'✅ PASSED' if results['api_validation'] else '❌ FAILED'}")
    
    print("\nSecret Details:")
    for secret in results["secrets"]:
        status = "✅ VALID" if secret["present"] and (secret["format_valid"] or secret["format_valid"] is None) else "❌ INVALID"
        if not secret["required"] and not secret["present"]:
            status = "⚪ NOT SET"
            
        print(f"  {secret['name']} - {status}")
        print(f"    Description: {secret['description']}")
        print(f"    Required:    {'Yes' if secret['required'] else 'No'}")
        print(f"    Present:     {'Yes' if secret['present'] else 'No'}")
        
        if secret["present"]:
            print(f"    Source:      {secret['source']}")
            
            if secret["format_valid"] is not None:
                print(f"    Format:      {'Valid' if secret['format_valid'] else 'Invalid'}")
                
            if secret["api_valid"] is not None:
                print(f"    API Check:   {'Valid' if secret['api_valid'] else 'Invalid'}")
                if secret["api_message"]:
                    print(f"    API Message: {secret['api_message']}")
        
        print()
    
    print("Recommendations:")
    if success:
        print("  ✅ All required secrets are properly configured!")
        print("  ✅ Ready for Ultra-Mega-Alpha-Tier operations!")
    else:
        missing_required = [s["name"] for s in results["secrets"] if s["required"] and not s["present"]]
        invalid_format = [s["name"] for s in results["secrets"] if s["present"] and s["format_valid"] is False]
        invalid_api = [s["name"] for s in results["secrets"] if s["present"] and s["api_valid"] is False]
        
        if missing_required:
            print(f"  - Set the following required secrets: {', '.join(missing_required)}")
        if invalid_format:
            print(f"  - Fix the format of the following secrets: {', '.join(invalid_format)}")
        if invalid_api:
            print(f"  - Check API permissions for: {', '.join(invalid_api)}")
    
    print("\n" + "=" * 60)


def main():
    """Main execution function."""
    args = parse_args()
    
    logger.info("Starting secrets validation for EpochCore Flash Sync system")
    
    # Validate secrets
    success, results = validate_secrets(args)
    
    # Print report
    print_validation_report(success, results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
