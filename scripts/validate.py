#!/usr/bin/env python3
"""
Validation script for repository configuration and structure.
Performs basic audits and checks as mentioned in the automation recommendations.
"""

import sys
from pathlib import Path


def validate_repository_structure():
    """Validate that the repository has the expected structure."""
    repo_root = Path(__file__).parent.parent

    required_dirs = ["scripts", "tests", ".github/workflows"]

    required_files = [
        "requirements.txt",
        "scripts/generate_icons.py",
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        ".flake8",
        "pyproject.toml",
    ]

    print("🔍 Validating repository structure...")

    # Check directories
    for dir_path in required_dirs:
        full_path = repo_root / dir_path
        if not full_path.exists():
            print(f"❌ Missing required directory: {dir_path}")
            return False
        print(f"✅ Directory exists: {dir_path}")

    # Check files
    for file_path in required_files:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"❌ Missing required file: {file_path}")
            return False
        print(f"✅ File exists: {file_path}")

    return True


def validate_dependencies():
    """Validate that requirements.txt contains expected dependencies."""
    repo_root = Path(__file__).parent.parent
    requirements_file = repo_root / "requirements.txt"

    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False

    content = requirements_file.read_text()

    required_packages = ["pytest", "flake8", "black", "Pillow"]

    print("🔍 Validating dependencies...")

    for package in required_packages:
        if package.lower() not in content.lower():
            print(f"❌ Missing required package: {package}")
            return False
        print(f"✅ Package found: {package}")

    return True


def validate_workflows():
    """Validate that GitHub workflows have required components."""
    repo_root = Path(__file__).parent.parent
    workflows_dir = repo_root / ".github" / "workflows"

    print("🔍 Validating GitHub workflows...")

    # Check CI workflow
    ci_file = workflows_dir / "ci.yml"
    if not ci_file.exists():
        print("❌ CI workflow missing")
        return False

    ci_content = ci_file.read_text()
    ci_requirements = [
        "install dependencies",
        "flake8",
        "black",
        "pytest",
        "generate_icons.py",
    ]

    for requirement in ci_requirements:
        if requirement.lower() not in ci_content.lower():
            print(f"❌ CI workflow missing: {requirement}")
            return False

    print("✅ CI workflow validation passed")

    # Check CD workflow
    cd_file = workflows_dir / "cd.yml"
    if not cd_file.exists():
        print("❌ CD workflow missing")
        return False

    cd_content = cd_file.read_text()
    cd_requirements = ["generate icons", "commit", "github pages"]

    for requirement in cd_requirements:
        if requirement.lower() not in cd_content.lower():
            print(f"❌ CD workflow missing: {requirement}")
            return False

    print("✅ CD workflow validation passed")

    return True


def main():
    """Main validation function."""
    print("🚀 Starting repository validation...")

    validations = [
        ("Repository Structure", validate_repository_structure),
        ("Dependencies", validate_dependencies),
        ("GitHub Workflows", validate_workflows),
    ]

    all_passed = True

    for name, validation_func in validations:
        print(f"\n--- {name} ---")
        if not validation_func():
            all_passed = False
            print(f"❌ {name} validation failed")
        else:
            print(f"✅ {name} validation passed")

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validations passed!")
        return 0
    else:
        print("💥 Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
