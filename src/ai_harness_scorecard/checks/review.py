"""Category 4: Review & Drift Prevention (15% weight).

Blog principle: 'Separate author from reviewer' + 'garbage collection agents.'
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .base import BaseCheck

if TYPE_CHECKING:
    from ..models import CheckResult
    from ..repo_context import RepoContext


class CodeReviewRequiredCheck(BaseCheck):
    check_id = "review.code_review_required"
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
    check_id = "review.scheduled_ci"
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
    check_id = "review.stale_doc_detection"
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
            "Add TODO/FIXME scanning, link checking (lychee), or prose linting (vale) to CI.",
        )


_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HEADING_LINE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<label>.+?)\s*#*\s*$")
_BOLD_LABEL_LINE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\*\*|__)(?P<label>[^*_\n]+?)(?:\*\*|__)")
_COLON_LABEL_LINE = re.compile(r"^\s*(?:[-*+]\s+)?(?P<label>[A-Za-z][A-Za-z0-9 /'&()?-]{0,48}):")

TEMPLATE_SECTIONS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Testing", re.compile(r"\b(?:test plan|testing|tests?|tested)\b", re.IGNORECASE)),
    ("Risk", re.compile(r"\b(?:risks?|impact)\b", re.IGNORECASE)),
    (
        "How to revert",
        re.compile(r"\b(?:revert(?:ing)?|rollback|roll[ -]back|how to undo)\b", re.IGNORECASE),
    ),
)


def _section_label(line: str) -> str | None:
    for pattern in (_HEADING_LINE, _BOLD_LABEL_LINE, _COLON_LABEL_LINE):
        match = pattern.match(line)
        if match:
            return match.group("label")
    return None


def find_template_sections(content: str) -> frozenset[str]:
    """Return the names of TEMPLATE_SECTIONS that appear as a heading or label line.

    Only markdown headings, lines starting with bold text, and short `Label:` lines count,
    so a keyword mentioned in prose or inside an HTML comment does not.
    """
    found: set[str] = set()
    for line in _HTML_COMMENT.sub("", content).splitlines():
        label = _section_label(line)
        if label is None:
            continue
        for name, pattern in TEMPLATE_SECTIONS:
            if pattern.search(label):
                found.add(name)
    return frozenset(found)


class MRTemplateCheck(BaseCheck):
    check_id = "review.mr_template"
    name = "PR/MR Template"
    description = "Pull/merge request template with testing, risk, and revert sections"
    max_points = 2.0
    source = (
        "DORA 2025 - working in small batches; "
        "Anthropic Claude Code team - How the Claude Code team does code review (2026)"
    )

    TEMPLATE_PATTERNS = (
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".gitlab/merge_request_templates/*.md",
        "docs/pull_request_template.md",
    )
    GITLAB_TEMPLATE_DIR = ".gitlab/merge_request_templates"

    def run(self, context: RepoContext) -> CheckResult:
        templates = list(dict.fromkeys(context.find_files(*self.TEMPLATE_PATTERNS)))
        all_sections = [name for name, _ in TEMPLATE_SECTIONS]

        if not templates:
            if context.has_dir(self.GITLAB_TEMPLATE_DIR):
                return self.partial_result(
                    1.0,
                    f"{self.GITLAB_TEMPLATE_DIR}/ found, but it contains no .md templates",
                    self._remediation(f"{self.GITLAB_TEMPLATE_DIR}/Default.md", all_sections),
                )
            return self.fail_result(
                "No PR/MR template found",
                "Add .github/PULL_REQUEST_TEMPLATE.md or "
                ".gitlab/merge_request_templates/Default.md with "
                "sections for testing, risk, and how to revert.",
            )

        best_path = templates[0]
        best_missing = all_sections
        for path in templates:
            present = find_template_sections(context.read_file(path) or "")
            missing = [name for name in all_sections if name not in present]
            if not missing:
                return self.pass_result(
                    f"PR/MR template with testing, risk, and revert sections: {path}"
                )
            if len(missing) < len(best_missing):
                best_path, best_missing = path, missing

        return self.partial_result(
            1.0,
            f"PR/MR template found: {best_path} (missing: {', '.join(best_missing)})",
            self._remediation(best_path, best_missing),
        )

    @staticmethod
    def _remediation(path: str, missing: list[str]) -> str:
        headings = ", ".join(f"## {name}" for name in missing)
        return f"Add these sections to {path}: {headings}."


class AutomatedReviewCheck(BaseCheck):
    check_id = "review.automated_review"
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
    check_id = "review.doc_sync_check"
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
