"""Category 2: Mechanical Constraints (25% weight).

Blog principle: 'Rules enforced by linters, structural tests, and CI gates.'
"""

from __future__ import annotations

from ..models import CheckResult
from ..repo_context import RepoContext
from .base import BaseCheck


class CIPipelineExistsCheck(BaseCheck):
    check_id = "ci_pipeline_exists"
    name = "CI Pipeline"
    description = "CI configuration present for automated checks"
    max_points = 3.0
    source = "DORA 2025 Report"

    def run(self, context: RepoContext) -> CheckResult:
        if context.ci_configs:
            types = ", ".join(ci.ci_type for ci in context.ci_configs)
            return self.pass_result(f"CI detected: {types}")

        ci_files = context.has_file(
            ".travis.yml", "Jenkinsfile", ".circleci/config.yml",
            "azure-pipelines.yml", "bitbucket-pipelines.yml",
        )
        if ci_files:
            return self.pass_result(f"CI config found: {ci_files}")

        return self.fail_result(
            "No CI configuration found",
            "Add .gitlab-ci.yml or .github/workflows/ to run automated checks on every change.",
        )


class LinterEnforcementCheck(BaseCheck):
    check_id = "linter_enforcement"
    name = "Linter Enforcement"
    description = "Linter runs in CI with blocking severity"
    max_points = 4.0
    source = "OpenAI Harness Engineering - mechanical constraints"

    LINTER_PATTERNS = [
        r"cargo\s+clippy",
        r"eslint",
        r"flake8",
        r"pylint",
        r"ruff\s+(check|\.)",
        r"rubocop",
        r"golangci-lint",
        r"mypy",
        r"pyright",
        r"ktlint",
        r"swiftlint",
    ]

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.LINTER_PATTERNS:
            if context.ci_has_blocking_command(pattern):
                return self.pass_result(f"Blocking linter found in CI: {pattern}")

        for pattern in self.LINTER_PATTERNS:
            if context.ci_has_command(pattern):
                return self.partial_result(
                    2.0,
                    f"Linter found in CI ({pattern}) but may not be blocking",
                    "Ensure linter job is not set to allow_failure / continue-on-error.",
                )

        return self.fail_result(
            "No linter found in CI",
            "Add a linter to CI that blocks merges on violations "
            "(e.g. cargo clippy -- -D warnings, eslint --max-warnings 0).",
        )


class FormatterEnforcementCheck(BaseCheck):
    check_id = "formatter_enforcement"
    name = "Formatter Enforcement"
    description = "Code formatter check runs in CI"
    max_points = 3.0
    source = "OpenAI Harness Engineering - mechanical constraints"

    FORMATTER_PATTERNS = [
        r"cargo\s+fmt.*--check",
        r"prettier\s+--check",
        r"black\s+--check",
        r"ruff\s+format\s+--check",
        r"gofmt\s+-l",
        r"goimports",
        r"rustfmt.*--check",
        r"scalafmt\s+--check",
    ]

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.FORMATTER_PATTERNS:
            if context.ci_has_command(pattern):
                return self.pass_result(f"Formatter check found in CI: {pattern}")

        return self.fail_result(
            "No formatter check found in CI",
            "Add a formatter check to CI (e.g. cargo fmt --all -- --check, prettier --check).",
        )


class TypeSafetyCheck(BaseCheck):
    check_id = "type_safety"
    name = "Type Safety"
    description = "Type checking enforced via language features or tools"
    max_points = 3.0
    source = "SlopCodeBench - preventing subtle type errors"

    def run(self, context: RepoContext) -> CheckResult:
        if "rust" in context.languages:
            return self.pass_result("Rust: type safety enforced by compiler")

        if "go" in context.languages:
            return self.pass_result("Go: type safety enforced by compiler")

        if "java" in context.languages or "kotlin" in context.languages:
            return self.pass_result("JVM language: type safety enforced by compiler")

        ts_config = context.has_file("tsconfig.json")
        if ts_config and context.search_file(ts_config, r'"strict"\s*:\s*true'):
            return self.pass_result("TypeScript strict mode enabled")
        if ts_config:
            return self.partial_result(
                1.5, "TypeScript found but strict mode not confirmed",
                "Enable \"strict\": true in tsconfig.json.",
            )

        if context.ci_has_command(r"mypy|pyright|pytype"):
            return self.pass_result("Python type checker found in CI")

        pyproject = context.has_file("pyproject.toml")
        if pyproject and context.search_file(pyproject, r"\[tool\.mypy\]|\[tool\.pyright\]"):
            return self.partial_result(
                1.5, "Type checker configured but not confirmed in CI",
                "Add mypy/pyright to your CI pipeline.",
            )

        return self.fail_result(
            "No type safety enforcement found",
            "Use a statically typed language, enable TypeScript strict mode, "
            "or add mypy/pyright to CI for Python.",
        )


class DependencyAuditingCheck(BaseCheck):
    check_id = "dependency_auditing"
    name = "Dependency Auditing"
    description = "Dependency vulnerability scanning in CI (blocking)"
    max_points = 4.0
    source = "Blog: security infrastructure reliability"

    AUDIT_PATTERNS = [
        r"cargo\s+(audit|deny)",
        r"npm\s+audit",
        r"safety\s+check",
        r"pip-audit",
        r"snyk\s+test",
        r"trivy\s+fs",
        r"grype",
        r"dependency.scanning",
        r"gemnasium",
        r"dependabot",
        r"renovate",
    ]

    def run(self, context: RepoContext) -> CheckResult:
        for pattern in self.AUDIT_PATTERNS:
            if context.ci_has_blocking_command(pattern):
                return self.pass_result(f"Blocking dependency audit in CI: {pattern}")

        for pattern in self.AUDIT_PATTERNS:
            if context.ci_has_command(pattern):
                return self.partial_result(
                    2.0,
                    f"Dependency audit found ({pattern}) but set to allow_failure",
                    "Make the audit job blocking (remove allow_failure / continue-on-error).",
                )

        dep_config = context.has_file("deny.toml", ".cargo/audit.toml", ".snyk", "renovate.json")
        if dep_config:
            return self.partial_result(
                1.0,
                f"Audit config found ({dep_config}) but not confirmed in CI",
                "Add the audit tool to your CI pipeline as a blocking job.",
            )

        return self.fail_result(
            "No dependency auditing found",
            "Add cargo deny/audit, npm audit, pip-audit, or Snyk to CI as a blocking check.",
        )


class ConventionalCommitsCheck(BaseCheck):
    check_id = "conventional_commits"
    name = "Conventional Commits"
    description = "Commit or MR title format enforced in CI"
    max_points = 2.0
    source = "DORA 2025 - working in small batches"

    def run(self, context: RepoContext) -> CheckResult:
        if context.ci_has_command(r"commitlint|conventional-changelog|semantic-release"):
            return self.pass_result("Conventional commit enforcement found in CI")

        config = context.has_file(
            ".commitlintrc.yml", ".commitlintrc.json", ".commitlintrc.js",
            "commitlint.config.js", ".releaserc.json", ".releaserc.yml",
        )
        if config:
            return self.pass_result(f"Commit lint config found: {config}")

        return self.fail_result(
            "No conventional commit enforcement found",
            "Add commitlint or equivalent to CI to enforce consistent commit message format.",
        )


class UnsafeCodePolicyCheck(BaseCheck):
    check_id = "unsafe_code_policy"
    name = "Unsafe Code Policy"
    description = "Explicit policy against dangerous code patterns"
    max_points = 3.0
    source = "Blog: 80% problem in AI-generated code"

    def run(self, context: RepoContext) -> CheckResult:
        cargo_toml = context.has_file("cargo.toml")
        if cargo_toml and context.search_file(cargo_toml, r'unsafe_code\s*=\s*"forbid"'):
            return self.pass_result("Rust: unsafe_code = forbid")

        eslintrc = context.has_file(
            ".eslintrc.json", ".eslintrc.yml", ".eslintrc.js", "eslint.config.js",
        )
        if eslintrc and context.search_file(eslintrc, r"no-eval|no-implied-eval"):
            return self.pass_result("ESLint unsafe pattern rules found")

        if context.ci_has_command(r"semgrep|bandit|brakeman|gosec"):
            return self.pass_result("Security linter found in CI")

        ci_raw = context.ci_raw_content()
        if "sast" in ci_raw.lower() or "semgrep" in ci_raw.lower():
            return self.pass_result("SAST scanning found in CI")

        return self.fail_result(
            "No explicit policy against unsafe code patterns",
            "Add unsafe_code = forbid (Rust), security linting (semgrep/bandit), "
            "or ESLint rules against dangerous patterns.",
        )


CONSTRAINT_CHECKS: list[BaseCheck] = [
    CIPipelineExistsCheck(),
    LinterEnforcementCheck(),
    FormatterEnforcementCheck(),
    TypeSafetyCheck(),
    DependencyAuditingCheck(),
    ConventionalCommitsCheck(),
    UnsafeCodePolicyCheck(),
]
