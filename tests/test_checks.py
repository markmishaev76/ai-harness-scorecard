"""Tests for individual assessment checks."""

from __future__ import annotations

from pathlib import Path

from ai_harness_scorecard.repo_context import RepoContext


def _build_context(tmp_path: Path, files: dict[str, str] | None = None) -> RepoContext:
    """Build a RepoContext from a tmp_path with optional files."""
    if files:
        for name, content in files.items():
            filepath = tmp_path / name
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")
    return RepoContext.build(tmp_path)


class TestArchitectureDocCheck:
    def test_pass_with_architecture_md(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import ArchitectureDocCheck

        context = _build_context(tmp_path, {"ARCHITECTURE.md": "# Architecture\nOverview here."})
        result = ArchitectureDocCheck().run(context)
        assert result.passed

    def test_fail_without_architecture_md(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import ArchitectureDocCheck

        context = _build_context(tmp_path)
        result = ArchitectureDocCheck().run(context)
        assert not result.passed


class TestAgentInstructionsCheck:
    def test_pass_with_agents_md(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import AgentInstructionsCheck

        context = _build_context(tmp_path, {"AGENTS.md": "# Agent Instructions"})
        result = AgentInstructionsCheck().run(context)
        assert result.passed

    def test_pass_with_claude_md(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import AgentInstructionsCheck

        context = _build_context(tmp_path, {"CLAUDE.md": "# Claude instructions"})
        result = AgentInstructionsCheck().run(context)
        assert result.passed

    def test_fail_without_any(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import AgentInstructionsCheck

        context = _build_context(tmp_path)
        result = AgentInstructionsCheck().run(context)
        assert not result.passed


class TestLinterEnforcementCheck:
    def test_pass_with_ruff_in_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        ci_content = """
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check src/
"""
        context = _build_context(tmp_path, {".github/workflows/ci.yml": ci_content})
        result = LinterEnforcementCheck().run(context)
        assert result.passed

    def test_fail_without_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        context = _build_context(tmp_path)
        result = LinterEnforcementCheck().run(context)
        assert not result.passed


class TestSecurityCriticalMarkingCheck:
    def test_pass_with_codeowners_and_security_md(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.ai_safeguards import SecurityCriticalMarkingCheck

        context = _build_context(
            tmp_path,
            {
                "CODEOWNERS": "* @owner",
                "SECURITY.md": "# Security Policy",
            },
        )
        result = SecurityCriticalMarkingCheck().run(context)
        assert result.passed

    def test_fail_without_either(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.ai_safeguards import SecurityCriticalMarkingCheck

        context = _build_context(tmp_path)
        result = SecurityCriticalMarkingCheck().run(context)
        assert not result.passed
