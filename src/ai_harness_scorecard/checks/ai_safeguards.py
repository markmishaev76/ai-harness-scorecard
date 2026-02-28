"""Category 5: AI-Specific Safeguards (15% weight).

Blog principle: 'The solution is not better prompts. It's a better environment.'
"""

from __future__ import annotations

from ..models import CheckResult
from ..repo_context import RepoContext
from .base import BaseCheck


class AIUsageNormsCheck(BaseCheck):
    check_id = "ai_usage_norms"
    name = "AI Usage Norms"
    description = "Documented policy on AI usage and review expectations"
    max_points = 4.0
    source = "DORA 2025 - clear organizational stance on AI use"

    AI_NORM_FILES = [
        "claude.md", "agents.md", "contributing.md",
        "docs/ai-*.md", "docs/development.md",
        ".cursor/rules/*.mdc",
    ]

    AI_NORM_PATTERNS = [
        r"ai.*(usage|policy|guideline|norm|review)",
        r"(review|verify|check).*(ai|generated|agent)",
        r"(test|tests)\s+before\s+(implement|code|asking)",
        r"code\s+style",
        r"(naming|error.handling|comment)\s+(convention|standard|policy)",
    ]

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.AI_NORM_PATTERNS:
            found = context.search_any_file(self.AI_NORM_FILES, pattern)
            if found:
                return self.pass_result(f"AI usage norms found in {found}")

        agent_file = context.has_file("claude.md", "agents.md")
        if agent_file:
            return self.partial_result(
                2.0,
                f"Agent file found ({agent_file}) but no explicit review norms detected",
                "Add a section on AI review expectations: what reviewers should specifically "
                "check in AI-generated code, when to require manual implementation.",
            )

        return self.fail_result(
            "No AI usage norms documented",
            "Document AI usage policies: review expectations for AI-generated code, "
            "when manual implementation is required, testing-before-implementation norms.",
        )


class SmallBatchEnforcementCheck(BaseCheck):
    check_id = "small_batch_enforcement"
    name = "Small Batch Enforcement"
    description = "PR/MR size limits or guidelines enforced"
    max_points = 3.0
    source = "DORA 2025 - working in small batches"

    def run(self, context: RepoContext) -> CheckResult:
        if context.ci_has_command(r"danger|pr-size|diffstat|size-limit"):
            return self.pass_result("PR size check tool found in CI")

        contributing = context.has_file("contributing.md", "CONTRIBUTING.md")
        if contributing and context.search_file(
            contributing, r"small\s+(pr|mr|batch|change)|size\s+limit|keep.*(small|focused)"
        ):
            return self.pass_result(f"Small batch guidelines found in {contributing}")

        agent_file = context.has_file("claude.md", "agents.md")
        if agent_file and context.search_file(
            agent_file, r"small|batch|incremental|focused"
        ):
            return self.partial_result(
                1.5,
                f"Small batch hints found in {agent_file}",
                "Add explicit PR size guidelines or automated size checks to CI.",
            )

        return self.fail_result(
            "No small batch enforcement found",
            "Add PR size checks (Danger, pr-size-labeler) or document size guidelines "
            "in CONTRIBUTING.md. Large AI-generated PRs are harder to review.",
        )


class MultipleApproachCultureCheck(BaseCheck):
    check_id = "multiple_approach_culture"
    name = "Design-Before-Code Culture"
    description = "RFC process, design docs, or plan-before-code workflow"
    max_points = 3.0
    source = "Blog: cognitive offloading guardrails"

    def run(self, context: RepoContext) -> CheckResult:
        rfc_dir = context.has_dir("docs/rfcs", "rfcs", "docs/proposals", "docs/designs")
        if rfc_dir:
            return self.pass_result(f"RFC/design document directory found: {rfc_dir}")

        design_docs = context.find_files(
            "docs/*plan*.md", "docs/*design*.md", "docs/*rfc*.md",
            "docs/*proposal*.md", "docs/phase-*.md",
        )
        if design_docs:
            names = ", ".join(design_docs[:3])
            return self.pass_result(f"Design/plan documents found: {names}")

        agent_file = context.has_file("claude.md", "agents.md")
        if agent_file and context.search_file(
            agent_file, r"plan.*before|design.*first|multiple.*approach|spec\.md|plan\.md"
        ):
            return self.pass_result(f"Plan-before-code workflow documented in {agent_file}")

        cursor_rules = context.has_dir(".cursor/rules")
        if cursor_rules:
            rule_files = context.find_files(".cursor/rules/*.mdc")
            for rf in rule_files:
                if context.search_file(rf, r"plan|design|spec"):
                    return self.pass_result(
                        f"Plan-driven development rule found in {rf}"
                    )

        return self.fail_result(
            "No design-before-code process found",
            "Create docs/rfcs/ or docs/designs/ directory. Document a process where "
            "significant changes start with a design doc or plan before implementation.",
        )


class ErrorHandlingPolicyCheck(BaseCheck):
    check_id = "error_handling_policy"
    name = "Error Handling Policy"
    description = "Policy against panic/crash patterns in code"
    max_points = 3.0
    source = "Blog: AI agents deleting tests, using expect()"

    def run(self, context: RepoContext) -> CheckResult:
        cargo_toml = context.has_file("cargo.toml")
        if cargo_toml and context.search_file(cargo_toml, r"unwrap_used|expect_used"):
            return self.pass_result("Clippy panic-prevention lints configured")

        if context.ci_has_command(r"clippy.*unwrap_used|clippy.*expect_used"):
            return self.pass_result("Panic-prevention clippy lints in CI")

        eslintrc = context.has_file(
            ".eslintrc.json", ".eslintrc.yml", "eslint.config.js",
        )
        if eslintrc and context.search_file(eslintrc, r"no-throw-literal|no-implicit-coercion"):
            return self.pass_result("Error handling ESLint rules configured")

        agent_file = context.has_file("claude.md", "agents.md")
        if agent_file and context.search_file(
            agent_file, r"error.handling|unwrap|expect|panic|Result.*\?"
        ):
            return self.partial_result(
                1.5,
                f"Error handling guidelines found in {agent_file}",
                "Enforce error handling rules mechanically via lints, not just documentation.",
            )

        return self.fail_result(
            "No error handling policy found",
            "Add clippy lints (unwrap_used, expect_used) for Rust, "
            "ESLint rules for JS/TS, or document error handling patterns in agent instructions.",
        )


class SecurityCriticalMarkingCheck(BaseCheck):
    check_id = "security_critical_marking"
    name = "Security-Critical Path Marking"
    description = "Critical code paths identified for extra review"
    max_points = 2.0
    source = "Blog: 80% problem in security infrastructure"

    def run(self, context: RepoContext) -> CheckResult:
        codeowners = context.has_file("CODEOWNERS", ".github/CODEOWNERS")
        if codeowners:
            return self.pass_result(f"CODEOWNERS found: {codeowners}")

        security_md = context.has_file("SECURITY.md", "security.md")
        if security_md:
            return self.pass_result(f"Security policy found: {security_md}")

        if context.ci_has_command(r"sast|dast|semgrep|bandit|gosec|brakeman"):
            return self.pass_result("Security scanning in CI")

        return self.fail_result(
            "No security-critical path marking found",
            "Add CODEOWNERS for sensitive directories, SECURITY.md for vuln reporting, "
            "or SAST scanning in CI.",
        )


AI_SAFEGUARD_CHECKS: list[BaseCheck] = [
    AIUsageNormsCheck(),
    SmallBatchEnforcementCheck(),
    MultipleApproachCultureCheck(),
    ErrorHandlingPolicyCheck(),
    SecurityCriticalMarkingCheck(),
]
