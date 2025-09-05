#!/usr/bin/env python3
"""
Impact Propagation Engine for Dependency Analysis

This engine analyzes code dependencies and propagates changes through
the system to identify affected components and automation opportunities.
"""

import json
import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Component:
    """Represents a component in the system."""

    id: str
    name: str
    path: str
    type: str
    dependencies: List[str]
    dependents: List[str]
    last_modified: str
    checksum: str


@dataclass
class Impact:
    """Represents an impact from a change."""

    source_component: str
    affected_component: str
    impact_type: str
    severity: str
    description: str
    automation_opportunity: bool


class ImpactPropagationEngine:
    """
    Core engine for analyzing dependencies and propagating impacts.

    This engine helps identify:
    - Which components are affected by changes
    - Automation opportunities for fixing cascading issues
    - Recursive improvement paths
    """

    def __init__(self, root_path: str = "."):
        """Initialize the engine with a root directory."""
        self.root_path = Path(root_path).resolve()
        self.components: Dict[str, Component] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_graph: Dict[str, Set[str]] = {}

    def scan_repository(self) -> Dict[str, Component]:
        """
        Scan the repository to discover components and their dependencies.

        Returns:
            Dictionary of discovered components
        """
        print("🔍 Scanning repository for components...")

        # Scan different file types
        self._scan_python_files()
        self._scan_yaml_files()
        self._scan_markdown_files()
        self._scan_powershell_files()
        self._scan_javascript_files()

        self._build_dependency_graphs()

        print(f"✅ Discovered {len(self.components)} components")
        return self.components

    def _scan_python_files(self):
        """Scan Python files for imports and dependencies."""
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_path(py_file):
                continue

            component_id = str(py_file.relative_to(self.root_path))
            dependencies = self._extract_python_dependencies(py_file)

            component = Component(
                id=component_id,
                name=py_file.name,
                path=str(py_file),
                type="python",
                dependencies=dependencies,
                dependents=[],
                last_modified=datetime.fromtimestamp(
                    py_file.stat().st_mtime
                ).isoformat(),
                checksum=self._calculate_file_checksum(py_file),
            )

            self.components[component_id] = component

    def _scan_yaml_files(self):
        """Scan YAML workflow files for dependencies."""
        for yaml_file in self.root_path.rglob("*.yml"):
            if self._should_skip_path(yaml_file):
                continue

            component_id = str(yaml_file.relative_to(self.root_path))
            dependencies = self._extract_yaml_dependencies(yaml_file)

            component = Component(
                id=component_id,
                name=yaml_file.name,
                path=str(yaml_file),
                type="workflow",
                dependencies=dependencies,
                dependents=[],
                last_modified=datetime.fromtimestamp(
                    yaml_file.stat().st_mtime
                ).isoformat(),
                checksum=self._calculate_file_checksum(yaml_file),
            )

            self.components[component_id] = component

    def _scan_markdown_files(self):
        """Scan Markdown files for documentation dependencies."""
        for md_file in self.root_path.rglob("*.md"):
            if self._should_skip_path(md_file):
                continue

            component_id = str(md_file.relative_to(self.root_path))
            dependencies = self._extract_markdown_dependencies(md_file)

            component = Component(
                id=component_id,
                name=md_file.name,
                path=str(md_file),
                type="documentation",
                dependencies=dependencies,
                dependents=[],
                last_modified=datetime.fromtimestamp(
                    md_file.stat().st_mtime
                ).isoformat(),
                checksum=self._calculate_file_checksum(md_file),
            )

            self.components[component_id] = component

    def _scan_powershell_files(self):
        """Scan PowerShell files for dependencies."""
        for ps_file in self.root_path.rglob("*.ps1"):
            if self._should_skip_path(ps_file):
                continue

            component_id = str(ps_file.relative_to(self.root_path))
            dependencies = self._extract_powershell_dependencies(ps_file)

            component = Component(
                id=component_id,
                name=ps_file.name,
                path=str(ps_file),
                type="powershell",
                dependencies=dependencies,
                dependents=[],
                last_modified=datetime.fromtimestamp(
                    ps_file.stat().st_mtime
                ).isoformat(),
                checksum=self._calculate_file_checksum(ps_file),
            )

            self.components[component_id] = component

    def _scan_javascript_files(self):
        """Scan JavaScript/JSON files for dependencies."""
        for js_file in self.root_path.rglob("*.json"):
            if self._should_skip_path(js_file):
                continue

            component_id = str(js_file.relative_to(self.root_path))
            dependencies = self._extract_json_dependencies(js_file)

            component = Component(
                id=component_id,
                name=js_file.name,
                path=str(js_file),
                type="configuration",
                dependencies=dependencies,
                dependents=[],
                last_modified=datetime.fromtimestamp(
                    js_file.stat().st_mtime
                ).isoformat(),
                checksum=self._calculate_file_checksum(js_file),
            )

            self.components[component_id] = component

    def _should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped during scanning."""
        skip_patterns = [
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "assets/icons",
        ]

        return any(pattern in str(path) for pattern in skip_patterns)

    def _extract_python_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from Python files."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find import statements
            import_patterns = [
                r"^import\s+(\w+)",
                r"^from\s+(\w+)",
                r"import\s+(\w+)",
            ]

            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                dependencies.extend(matches)

        except Exception:
            pass

        return list(set(dependencies))

    def _extract_yaml_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from YAML workflow files."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find action dependencies and script references
            patterns = [
                r"uses:\s*([^@\s]+)",
                r"run:\s*.*?([a-zA-Z_][a-zA-Z0-9_]*\.py)",
                r"run:\s*.*?([a-zA-Z_][a-zA-Z0-9_]*\.ps1)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                dependencies.extend(matches)

        except Exception:
            pass

        return list(set(dependencies))

    def _extract_markdown_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from Markdown files."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find file references
            patterns = [
                r"`([^`]+\.py)`",
                r"`([^`]+\.ps1)`",
                r"`([^`]+\.yml)`",
                r"`([^`]+\.md)`",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)

        except Exception:
            pass

        return list(set(dependencies))

    def _extract_powershell_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from PowerShell files."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find module imports and file references
            patterns = [
                r"Import-Module\s+([^\s]+)",
                r"\.\\([^\\s]+\.ps1)",
                r'"([^"]+\.json)"',
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)

        except Exception:
            pass

        return list(set(dependencies))

    def _extract_json_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from JSON configuration files."""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # For package.json, extract dependencies
            if file_path.name == "package.json" and "dependencies" in data:
                dependencies.extend(data["dependencies"].keys())

            if "devDependencies" in data:
                dependencies.extend(data["devDependencies"].keys())

        except Exception:
            pass

        return dependencies

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _build_dependency_graphs(self):
        """Build forward and reverse dependency graphs."""
        for component_id, component in self.components.items():
            self.dependency_graph[component_id] = set()
            self.reverse_graph[component_id] = set()

        for component_id, component in self.components.items():
            for dep in component.dependencies:
                # Find matching components
                matching_components = [
                    comp_id
                    for comp_id in self.components.keys()
                    if dep in comp_id
                    or dep
                    == self.components[comp_id]
                    .name.replace(".py", "")
                    .replace(".ps1", "")
                ]

                for match in matching_components:
                    self.dependency_graph[component_id].add(match)
                    self.reverse_graph[match].add(component_id)
                    self.components[match].dependents.append(component_id)

    def analyze_impact(self, changed_components: List[str]) -> List[Impact]:
        """
        Analyze the impact of changes to specific components.

        Args:
            changed_components: List of component IDs that have changed

        Returns:
            List of identified impacts
        """
        impacts = []

        print(
            f"📊 Analyzing impact of changes to {len(changed_components)} components..."
        )

        for component_id in changed_components:
            if component_id not in self.components:
                continue

            # Find directly affected components
            directly_affected = self.reverse_graph.get(component_id, set())

            for affected_id in directly_affected:
                impact = Impact(
                    source_component=component_id,
                    affected_component=affected_id,
                    impact_type="direct_dependency",
                    severity="medium",
                    description=f"{affected_id} directly depends on {component_id}",
                    automation_opportunity=self._has_automation_opportunity(
                        component_id, affected_id
                    ),
                )
                impacts.append(impact)

            # Find cascading impacts
            cascading_impacts = self._find_cascading_impacts(
                component_id, directly_affected
            )
            impacts.extend(cascading_impacts)

        print(f"✅ Identified {len(impacts)} potential impacts")
        return impacts

    def _find_cascading_impacts(
        self, source_id: str, affected_components: Set[str]
    ) -> List[Impact]:
        """Find cascading impacts through the dependency chain."""
        cascading_impacts = []
        visited = set()

        def traverse(current_id: str, depth: int = 0):
            if (
                current_id in visited or depth > 3
            ):  # Limit depth to prevent infinite loops
                return

            visited.add(current_id)
            next_affected = self.reverse_graph.get(current_id, set())

            for next_id in next_affected:
                if next_id not in affected_components:
                    impact = Impact(
                        source_component=source_id,
                        affected_component=next_id,
                        impact_type="cascading_dependency",
                        severity="low" if depth > 1 else "medium",
                        description=f"{next_id} indirectly affected through {current_id}",
                        automation_opportunity=self._has_automation_opportunity(
                            source_id, next_id
                        ),
                    )
                    cascading_impacts.append(impact)
                    traverse(next_id, depth + 1)

        for affected_id in affected_components:
            traverse(affected_id, 1)

        return cascading_impacts

    def _has_automation_opportunity(self, source_id: str, affected_id: str) -> bool:
        """Determine if there's an automation opportunity between components."""
        source_comp = self.components.get(source_id)
        affected_comp = self.components.get(affected_id)

        if not source_comp or not affected_comp:
            return False

        # Automation opportunities exist for:
        # - Python to test relationships
        # - Workflow to script relationships
        # - Documentation to implementation relationships
        automation_patterns = [
            (
                source_comp.type == "python"
                and affected_comp.type == "python"
                and "test" in affected_comp.name
            ),
            (
                source_comp.type == "workflow"
                and affected_comp.type in ["python", "powershell"]
            ),
            (
                source_comp.type == "documentation"
                and affected_comp.type in ["python", "powershell", "workflow"]
            ),
        ]

        return any(automation_patterns)

    def suggest_automations(self, impacts: List[Impact]) -> List[Dict]:
        """Suggest automation improvements based on impacts."""
        suggestions = []

        for impact in impacts:
            if not impact.automation_opportunity:
                continue

            source_comp = self.components.get(impact.source_component)
            affected_comp = self.components.get(impact.affected_component)

            if not source_comp or not affected_comp:
                continue

            suggestion = {
                "type": "automation",
                "source": impact.source_component,
                "target": impact.affected_component,
                "description": self._generate_automation_suggestion(
                    source_comp, affected_comp
                ),
                "priority": "high" if impact.severity == "high" else "medium",
            }

            suggestions.append(suggestion)

        return suggestions

    def _generate_automation_suggestion(
        self, source: Component, target: Component
    ) -> str:
        """Generate specific automation suggestions."""
        if source.type == "python" and "test" in target.name:
            return f"Add automated test execution for {source.name} when {target.name} changes"
        elif source.type == "workflow" and target.type == "python":
            return f"Automate {target.name} execution in CI/CD pipeline"
        elif source.type == "documentation" and target.type == "python":
            return f"Auto-generate documentation from {target.name} code"
        else:
            return (
                f"Create automated dependency update for {source.name} → {target.name}"
            )

    def export_analysis(self, output_path: str = "impact_analysis.json"):
        """Export the complete analysis to a JSON file."""
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "components": {
                comp_id: asdict(comp) for comp_id, comp in self.components.items()
            },
            "dependency_graph": {k: list(v) for k, v in self.dependency_graph.items()},
            "reverse_graph": {k: list(v) for k, v in self.reverse_graph.items()},
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        print(f"📁 Analysis exported to {output_path}")


def main():
    """Main function for command-line usage."""
    print("🚀 Starting Impact Propagation Engine...")

    engine = ImpactPropagationEngine()

    # Scan repository
    components = engine.scan_repository()

    # Example: Analyze impact of changes to Python files
    python_components = [
        comp_id for comp_id, comp in components.items() if comp.type == "python"
    ]

    if python_components:
        impacts = engine.analyze_impact(
            python_components[:2]
        )  # Analyze first 2 Python files
        suggestions = engine.suggest_automations(impacts)

        print(f"\n📋 Automation Suggestions ({len(suggestions)}):")
        for suggestion in suggestions:
            print(f"  • {suggestion['description']}")

    # Export analysis
    engine.export_analysis()

    print("✅ Impact propagation analysis completed!")


if __name__ == "__main__":
    main()
