"""Category 1: Architectural Documentation (20% weight).

Blog principle: 'Document architecture in the repo, not in people's heads.'
"""

from __future__ import annotations

from ..models import CheckResult
from ..repo_context import RepoContext
from .base import BaseCheck


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


class ADRPresenceCheck(BaseCheck):
    check_id = "adr_presence"
    name = "Architecture Decision Records"
    description = "ADR directory with decision records"
    max_points = 3.0
    source = "DORA 2025 Report - AI-accessible documentation"

    def run(self, context: RepoContext) -> CheckResult:
        adr_dir = context.has_dir(
            "docs/adr", "docs/decisions", "docs/ADR", "adr", "doc/adr", "doc/decisions",
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
            r"cargo\s+doc|rustdoc|typedoc|jsdoc|sphinx|mkdocs|pdoc|javadoc|godoc|swag"
        )
        if context.ci_has_command(doc_gen_pattern):
            return self.pass_result("Doc generation found in CI")

        spec_file = context.has_file(
            "openapi.yaml", "openapi.json", "openapi.yml",
            "swagger.yaml", "swagger.json",
        )
        if spec_file:
            return self.pass_result(f"API spec found: {spec_file}")

        doc_config = context.has_file(
            "mkdocs.yml", "docs/conf.py", "typedoc.json", "jsdoc.json",
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
    ADRPresenceCheck(),
    ModuleBoundaryDocsCheck(),
    APIContractsCheck(),
]
