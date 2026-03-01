"""Tests for individual assessment checks."""

from __future__ import annotations

from pathlib import Path

import pytest

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

    def test_pass_with_checkstyle_in_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        ci_content = """
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: mvn checkstyle:check
"""
        context = _build_context(
            tmp_path, {"pom.xml": "<project/>", ".github/workflows/ci.yml": ci_content}
        )
        result = LinterEnforcementCheck().run(context)
        assert result.passed
        assert "checkstyle" in result.evidence.lower()

    def test_partial_with_checkstyle_xml_no_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        context = _build_context(
            tmp_path, {"pom.xml": "<project/>", "checkstyle.xml": "<checkstyle/>"}
        )
        result = LinterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "checkstyle config found" in result.evidence.lower()

    def test_fail_without_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        context = _build_context(tmp_path)
        result = LinterEnforcementCheck().run(context)
        assert not result.passed


class TestFormatterEnforcementCheck:
    def test_pass_with_spotless_in_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        ci_content = """
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./mvnw spotless:check
"""
        context = _build_context(
            tmp_path, {"pom.xml": "<project/>", ".github/workflows/ci.yml": ci_content}
        )
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert "spotless:check" in result.evidence

    def test_partial_with_spotless_in_pom(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        pom_content = "<project><plugin>spotless-maven-plugin</plugin></project>"
        context = _build_context(tmp_path, {"pom.xml": pom_content})
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "spotless plugin found" in result.evidence.lower()

    def test_partial_with_checkstyle_xml(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        context = _build_context(
            tmp_path, {"pom.xml": "<project/>", "checkstyle.xml": "<checkstyle/>"}
        )
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "checkstyle config found" in result.evidence.lower()


class TestDependencyAuditingCheck:
    def test_pass_with_snyk_action(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import DependencyAuditingCheck

        ci_content = """
name: CI
jobs:
  security:
    steps:
      - uses: snyk/actions/maven@master
"""
        context = _build_context(tmp_path, {".github/workflows/ci.yml": ci_content})
        result = DependencyAuditingCheck().run(context)
        assert result.passed
        assert "snyk/actions" in result.evidence

    def test_pass_with_owasp_in_ci(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import DependencyAuditingCheck

        ci_content = """
name: CI
jobs:
  audit:
    steps:
      - run: ./mvnw org.owasp:dependency-check-maven:check
"""
        context = _build_context(tmp_path, {".github/workflows/ci.yml": ci_content})
        result = DependencyAuditingCheck().run(context)
        assert result.passed
        assert "dependency-check-maven" in result.evidence


class TestPropertyBasedTestingCheck:
    def test_pass_with_jqwik_in_pom(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import PropertyBasedTestingCheck

        pom_content = "<project><dependency>jqwik</dependency></project>"
        context = _build_context(tmp_path, {"pom.xml": pom_content})
        result = PropertyBasedTestingCheck().run(context)
        assert result.passed
        assert "pom.xml" in result.evidence

    def test_pass_with_property_test_file(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import PropertyBasedTestingCheck

        context = _build_context(
            tmp_path, {"src/test/java/MyPropertyTest.java": "@Property void test() {}"}
        )
        result = PropertyBasedTestingCheck().run(context)
        assert result.passed
        assert "MyPropertyTest.java" in result.evidence


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
        assert result.score == result.max_points

    def test_fail_without_either(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.ai_safeguards import SecurityCriticalMarkingCheck

        context = _build_context(tmp_path)
        result = SecurityCriticalMarkingCheck().run(context)
        assert not result.passed
