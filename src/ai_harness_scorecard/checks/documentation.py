"""Category 1: Architectural Documentation (20% weight).

Blog principle: 'Document architecture in the repo, not in people's heads.'
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .base import BaseCheck

if TYPE_CHECKING:
    from ..models import CheckResult
    from ..repo_context import RepoContext


class ArchitectureDocCheck(BaseCheck):
    check_id = "architecture_doc"
    name = "Architecture Documentation"
    description = "ARCHITECTURE.md or equivalent at repo root (matklad pattern)"
    max_points = 5.0
    source = "matklad ARCHITECTURE.md guide"

    def run(self, context: RepoContext) -> CheckResult:
        found = context.has_file(
            "architecture.md",
            "architecture",
            "docs/architecture.md",
            "docs/architecture/*.md",
            "doc/architecture.md",
        )
        if found:
            return self.pass_result(f"Found: {found}")
        return self.fail_result(
            "No architecture documentation found",
            "Create ARCHITECTURE.md at repo root following matklad's pattern: "
            "short, stable, focused on module boundaries and constraints.",
        )


class AgentInstructionsCheck(BaseCheck):
    check_id = "agent_instructions"
    name = "Agent Instructions"
    description = "CLAUDE.md, AGENTS.md, or equivalent AI agent configuration"
    max_points = 5.0
    source = "OpenAI Harness Engineering (2026)"

    def run(self, context: RepoContext) -> CheckResult:
        found = context.has_file(
            "claude.md",
            "agents.md",
            ".cursorrules",
            ".github/copilot-instructions.md",
            "copilot.md",
        )
        if found:
            return self.pass_result(f"Found: {found}")

        if context.has_dir(".cursor/rules"):
            return self.pass_result("Found: .cursor/rules/ directory")

        return self.fail_result(
            "No AI agent instruction files found",
            "Create CLAUDE.md or AGENTS.md with project context, code style, "
            "and constraints so AI agents produce consistent output.",
        )


class HarnessDocsCheck(BaseCheck):
    check_id = "documentation.harness_docs"
    name = "Harness Documentation"
    description = "Quality pipeline, CI stages, or quality gates documented for contributors"
    max_points = 2.0
    source = "Morris 2026 - harness engineering"

    DOCUMENTATION_FILES = [
        "contributing.md",
        "docs/*.md",
        "docs/*.rst",
        "doc/*.md",
        "doc/*.rst",
    ]

    PIPELINE_PATTERNS = [
        r"\bci\s+(pipeline|stages?|workflow)\b",
        r"\bquality\s+gates?\b",
        r"\bpre-commit\b",
        r"\bdevelopment\s+workflow\b",
        r"how\s+to\s+add\s+(a\s+)?(new\s+)?(check|quality\s+gate|ci\s+job)",
        r"run\s+in\s+ci\s+and\s+must\s+pass",
    ]

    COMMENTED_CI_PATTERN = r"(?m)^\s*#.*\b(ci|quality|check|lint|test|type|gate|workflow)\b"

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.PIPELINE_PATTERNS:
            found = context.search_any_file(self.DOCUMENTATION_FILES, pattern)
            if found:
                return self.pass_result(f"Quality pipeline documented in {found}")

        contributing = context.has_file("contributing.md")
        if contributing:
            return self.partial_result(
                1.0,
                f"Found {contributing}, but no documented quality pipeline",
                "Document CI stages, quality gates, or how to add a new quality check.",
            )

        if context.ci_configs and re.search(
            self.COMMENTED_CI_PATTERN,
            context.ci_raw_content(),
            re.IGNORECASE,
        ):
            return self.partial_result(
                1.0,
                "CI config comments mention quality checks",
                "Move CI stage and quality gate guidance into CONTRIBUTING.md or docs/.",
            )

        return self.fail_result(
            "No quality pipeline documentation found",
            "Document the quality pipeline, CI stages, quality gates, or how to add a "
            "new check in CONTRIBUTING.md or docs/.",
        )


class ADRPresenceCheck(BaseCheck):
    check_id = "adr_presence"
    name = "Architecture Decision Records"
    description = "ADR directory with decision records"
    max_points = 3.0
    source = "DORA 2025 Report - AI-accessible documentation"

    def run(self, context: RepoContext) -> CheckResult:
        adr_dir = context.has_dir(
            "docs/adr",
            "docs/decisions",
            "docs/ADR",
            "adr",
            "doc/adr",
            "doc/decisions",
        )
        if adr_dir:
            return self.pass_result(f"Found ADR directory: {adr_dir}")

        found = context.has_file("docs/adr-*.md", "docs/decisions/*.md", "docs/000*.md")
        if found:
            return self.pass_result(f"Found ADR-like file: {found}")

        return self.fail_result(
            "No Architecture Decision Records found",
            "Create docs/adr/ directory with numbered markdown decision records. "
            "Use adr-tools or a simple template.",
        )


class ModuleBoundaryDocsCheck(BaseCheck):
    check_id = "module_boundary_docs"
    name = "Module Boundary Documentation"
    description = "Explicit dependency constraints between modules"
    max_points = 4.0
    source = "matklad ARCHITECTURE.md - constraints as absences"

    CONSTRAINT_PATTERNS = [
        r"never\s+depend",
        r"must\s+not\s+depend",
        r"does\s+not\s+(import|depend)",
        r"must\s+not\s+import",
        r"no\s+dependency\s+on",
        r"independent\s+of",
        r"zero.dependency",
    ]

    SEARCH_FILES = [
        "architecture.md",
        "docs/architecture.md",
        "claude.md",
        "agents.md",
        "readme.md",
        "docs/*.md",
    ]

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.CONSTRAINT_PATTERNS:
            found = context.search_any_file(self.SEARCH_FILES, pattern)
            if found:
                return self.pass_result(f"Module boundary constraints found in {found}")

        return self.fail_result(
            "No module boundary constraints documented",
            "Document which modules must NOT depend on each other in ARCHITECTURE.md. "
            "Example: 'The fields crate never depends on any other workspace crate.'",
        )


class APIContractsCheck(BaseCheck):
    check_id = "api_contracts"
    name = "API Documentation"
    description = "Public API documented via doc generation or spec files"
    max_points = 3.0
    source = "DORA 2025 - AI-accessible documentation"

    def run(self, context: RepoContext) -> CheckResult:
        doc_gen_pattern = (
            r"cargo\s+doc|rustdoc|typedoc|jsdoc|sphinx|mkdocs"
            r"|pdoc|javadoc|godoc|swag|dokka"
        )
        if context.ci_has_command(doc_gen_pattern):
            return self.pass_result("Doc generation found in CI")

        spec_file = context.has_file(
            "openapi.yaml",
            "openapi.json",
            "openapi.yml",
            "swagger.yaml",
            "swagger.json",
            "docs/openapi*.yaml",
            "docs/openapi*.json",
            "docs/openapi*.yml",
            "api-docs/*.yaml",
            "api-docs/*.json",
        )
        if spec_file:
            return self.pass_result(f"API spec found: {spec_file}")

        dep_files = ["build.gradle", "build.gradle.kts", "*/build.gradle", "*/build.gradle.kts"]
        for dep_file in dep_files:
            if context.search_any_file([dep_file], r"springdoc-openapi|springfox"):
                return self.pass_result(f"Runtime API documentation library found in {dep_file}")

        doc_config = context.has_file(
            "mkdocs.yml",
            "docs/conf.py",
            "typedoc.json",
            "jsdoc.json",
        )
        if doc_config:
            return self.pass_result(f"Doc generation config found: {doc_config}")

        return self.fail_result(
            "No API documentation generation or spec files found",
            "Add doc generation to CI (cargo doc, typedoc, sphinx) "
            "or maintain OpenAPI/Swagger specs.",
        )


DOCUMENTATION_CHECKS: list[BaseCheck] = [
    ArchitectureDocCheck(),
    AgentInstructionsCheck(),
    HarnessDocsCheck(),
    ADRPresenceCheck(),
    ModuleBoundaryDocsCheck(),
    APIContractsCheck(),
]
