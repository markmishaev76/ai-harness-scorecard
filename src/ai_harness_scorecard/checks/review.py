"""Category 4: Review & Drift Prevention (15% weight).

Blog principle: 'Separate author from reviewer' + 'garbage collection agents.'
"""

from __future__ import annotations

from ..models import CheckResult
from ..repo_context import RepoContext
from .base import BaseCheck


class CodeReviewRequiredCheck(BaseCheck):
    check_id = "code_review_required"
    name = "Code Review Required"
    description = "PR/MR reviews required before merge"
    max_points = 4.0
    source = "OpenAI Harness Engineering - author/reviewer separation"

    def run(self, context: RepoContext) -> CheckResult:
        codeowners = context.has_file("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")
        if codeowners:
            return self.pass_result(f"CODEOWNERS file found: {codeowners}")

        ci_raw = context.ci_raw_content()
        if "approval" in ci_raw.lower() or "review" in ci_raw.lower():
            return self.partial_result(
                2.0,
                "Review-related configuration found in CI",
                "Enforce code review via branch protection rules (requires API access to verify).",
            )

        return self.partial_result(
            0.0,
            "Cannot verify branch protection without API access. "
            "Run with --github-token or --gitlab-token for full assessment.",
            "Enable required reviews in branch protection settings and add CODEOWNERS.",
        )


class ScheduledCICheck(BaseCheck):
    check_id = "scheduled_ci"
    name = "Scheduled CI Jobs"
    description = "Nightly or periodic CI jobs for drift detection"
    max_points = 3.0
    source = "OpenAI Harness Engineering - garbage collection agents"

    def run(self, context: RepoContext) -> CheckResult:
        if context.ci_has_scheduled_job():
            return self.pass_result("Scheduled CI pipeline found")

        ci_raw = context.ci_raw_content()
        if "cron" in ci_raw.lower() or "schedule" in ci_raw.lower():
            return self.pass_result("Scheduled trigger found in CI config")

        return self.fail_result(
            "No scheduled CI jobs found",
            "Add scheduled/nightly CI pipelines for drift detection: "
            "stricter lints, dependency freshness, doc coverage scans.",
        )


class StaleDocDetectionCheck(BaseCheck):
    check_id = "stale_doc_detection"
    name = "Stale Documentation Detection"
    description = "Checks for TODO/FIXME accumulation or doc freshness"
    max_points = 2.0
    source = "OpenAI Harness Engineering - quality drift"

    def run(self, context: RepoContext) -> CheckResult:
        if context.ci_has_command(r"todo|fixme|hack"):
            return self.pass_result("TODO/FIXME scanning found in CI")

        doc_check_patterns = [
            r"link.check|markdown.link|lychee|linkinator",
            r"vale|textlint|markdownlint",
        ]
        for pattern in doc_check_patterns:
            if context.ci_has_command(pattern):
                return self.pass_result(f"Documentation quality check in CI: {pattern}")

        return self.fail_result(
            "No stale documentation detection found",
            "Add TODO/FIXME scanning, link checking (lychee), "
            "or prose linting (vale) to CI.",
        )


class MRTemplateCheck(BaseCheck):
    check_id = "mr_template"
    name = "PR/MR Template"
    description = "Pull/merge request template enforcing description and test plan"
    max_points = 2.0
    source = "DORA 2025 - working in small batches"

    def run(self, context: RepoContext) -> CheckResult:
        templates = [
            ".github/pull_request_template.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".gitlab/merge_request_templates/*.md",
            "docs/pull_request_template.md",
        ]
        found = context.has_file(*templates)
        if found:
            return self.pass_result(f"PR/MR template found: {found}")

        if context.has_dir(".gitlab/merge_request_templates"):
            return self.pass_result("GitLab MR template directory found")

        return self.fail_result(
            "No PR/MR template found",
            "Add .github/PULL_REQUEST_TEMPLATE.md or "
            ".gitlab/merge_request_templates/Default.md with "
            "sections for description, testing, and impact.",
        )


class AutomatedReviewCheck(BaseCheck):
    check_id = "automated_review"
    name = "Automated Code Review"
    description = "Bot reviewers or automated review tools configured"
    max_points = 2.0
    source = "OpenAI Harness Engineering - separate authoring and reviewing agents"

    def run(self, context: RepoContext) -> CheckResult:
        bot_configs = [
            ".coderabbit.yaml",
            ".github/copilot-review.yml",
            "renovate.json",
            ".renovaterc",
            ".renovaterc.json",
            "dependabot.yml",
            ".github/dependabot.yml",
        ]
        found = context.has_file(*bot_configs)
        if found:
            return self.pass_result(f"Automated review tool configured: {found}")

        ci_raw = context.ci_raw_content()
        bot_keywords = ["coderabbit", "codeclimate", "sonarqube", "sonarcloud", "duo"]
        for keyword in bot_keywords:
            if keyword in ci_raw.lower():
                return self.pass_result(f"Automated review tool found in CI: {keyword}")

        return self.fail_result(
            "No automated review tools found",
            "Configure CodeRabbit, SonarCloud, Dependabot/Renovate, or equivalent "
            "for automated review on every PR/MR.",
        )


class DocSyncCheckCheck(BaseCheck):
    check_id = "doc_sync_check"
    name = "Documentation Sync Check"
    description = "CI check that related docs stay in sync"
    max_points = 2.0
    source = "OpenAI Harness Engineering - curated knowledge base"

    def run(self, context: RepoContext) -> CheckResult:
        sync_patterns = [
            r"diff\s+.*\.md",
            r"doc.*sync",
            r"agent.*sync",
            r"golden.*check",
        ]
        for pattern in sync_patterns:
            if context.ci_has_command(pattern):
                return self.pass_result(f"Doc sync check found in CI: {pattern}")

        ci_raw = context.ci_raw_content()
        if "sync" in ci_raw.lower() and ("doc" in ci_raw.lower() or "agent" in ci_raw.lower()):
            return self.pass_result("Documentation sync job found in CI")

        return self.fail_result(
            "No documentation sync checks found in CI",
            "Add CI jobs that verify related docs stay in sync "
            "(e.g. diff AGENTS.md CLAUDE.md, golden fixture checks).",
        )


REVIEW_CHECKS: list[BaseCheck] = [
    CodeReviewRequiredCheck(),
    ScheduledCICheck(),
    StaleDocDetectionCheck(),
    MRTemplateCheck(),
    AutomatedReviewCheck(),
    DocSyncCheckCheck(),
]
