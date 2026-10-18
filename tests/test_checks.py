"""Tests for individual assessment checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ai_harness_scorecard.repo_context import RepoContext


def _build_context(tmp_path: Path, files: dict[str, str] | None = None) -> RepoContext:
    """Build a RepoContext from a tmp_path with optional files."""
    if files:
        for name, content in files.items():
            filepath = tmp_path / name
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")
    return RepoContext.build(tmp_path)


PMD_PARTIAL_LINTER_CASES: list[tuple[dict[str, str], float, str]] = [
    (
        {"pom.xml": "<project/>", "pmd.xml": "<pmd/>"},
        2.0,
        "pmd config found",
    ),
    (
        {"pom.xml": "<project><plugin>maven-pmd-plugin</plugin></project>"},
        2.0,
        "pmd config found",
    ),
    (
        {"services/app/pom.xml": "<project><plugin>maven-pmd-plugin</plugin></project>"},
        2.0,
        "pmd config found",
    ),
    (
        {
            "build.gradle": """
        plugins {
            id "pmd"
        }
        """
        },
        2.0,
        "pmd config found",
    ),
    (
        {
            "services/app/build.gradle": """
        plugins {
            id "pmd"
        }
        """
        },
        2.0,
        "pmd config found",
    ),
    (
        {
            "services/app/build.gradle.kts": """
        plugins {
            id("pmd")
        }
        """
        },
        2.0,
        "pmd config found",
    ),
]

PMD_CI_LINTER_CASES: list[tuple[dict[str, str], float, str]] = [
    (
        {
            "pom.xml": "<project/>",
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: mvn pmd:check
""",
        },
        4.0,
        "pmd",
    ),
    (
        {
            "build.gradle": "plugins {}",
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew pmdMain
""",
        },
        4.0,
        "pmd",
    ),
    (
        {
            "build.gradle": """
        plugins {
            id "pmd"
        }
        """,
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew check
""",
        },
        4.0,
        "check",
    ),
]

SPOTBUGS_PARTIAL_LINTER_CASES: list[tuple[dict[str, str], float, str]] = [
    (
        {"pom.xml": "<project><plugin>spotbugs-maven-plugin</plugin></project>"},
        2.0,
        "spotbugs config found",
    ),
    (
        {"services/app/pom.xml": "<project><plugin>spotbugs-maven-plugin</plugin></project>"},
        2.0,
        "spotbugs config found",
    ),
    (
        {
            "build.gradle": """
        plugins {
            id "com.github.spotbugs"
        }
        """
        },
        2.0,
        "spotbugs config found",
    ),
    (
        {
            "services/app/build.gradle": """
        plugins {
            id "com.github.spotbugs"
        }
        """
        },
        2.0,
        "spotbugs config found",
    ),
    (
        {
            "services/app/build.gradle.kts": """
        plugins {
            id("com.github.spotbugs")
        }
        """
        },
        2.0,
        "spotbugs config found",
    ),
    (
        {"pom.xml": "<project/>", "spotbugs-exclude.xml": "<FindBugsFilter/>"},
        2.0,
        "spotbugs config found",
    ),
]

SPOTBUGS_CI_LINTER_CASES: list[tuple[dict[str, str], float, str]] = [
    (
        {
            "pom.xml": "<project/>",
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: mvn spotbugs:check
""",
        },
        4.0,
        "spotbugs",
    ),
    (
        {
            "pom.xml": "<project/>",
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./mvnw com.github.spotbugs:spotbugs-maven-plugin:check
""",
        },
        4.0,
        "spotbugs-maven-plugin",
    ),
    (
        {
            "build.gradle": "plugins {}",
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew spotbugsMain
""",
        },
        4.0,
        "spotbugs",
    ),
    (
        {
            "build.gradle": """
        plugins {
            id "com.github.spotbugs"
        }
        """,
            ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew check
""",
        },
        4.0,
        "check",
    ),
]


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
    @pytest.mark.parametrize(
        ("files", "expected_score", "evidence_substring"),
        [
            (
                {
                    ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check src/
"""
                },
                4.0,
                "ruff",
            ),
            (
                {
                    "pom.xml": "<project/>",
                    ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: mvn checkstyle:check
""",
                },
                4.0,
                "checkstyle",
            ),
            *PMD_CI_LINTER_CASES,
            *SPOTBUGS_CI_LINTER_CASES,
            (
                {"pom.xml": "<project/>", "checkstyle.xml": "<checkstyle/>"},
                2.0,
                "checkstyle config found",
            ),
            *PMD_PARTIAL_LINTER_CASES,
            *SPOTBUGS_PARTIAL_LINTER_CASES,
        ],
    )
    def test_linter_enforcement_pass(
        self,
        tmp_path: Path,
        files: dict[str, str],
        expected_score: float,
        evidence_substring: str,
    ) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        context = _build_context(tmp_path, files)
        result = LinterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(expected_score)
        assert evidence_substring in result.evidence.lower()

    @pytest.mark.parametrize(
        "files",
        [
            None,
            {
                "pom.xml": "<project/>",
                ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: cat config/pmd.xml
""",
            },
            {
                "pom.xml": "<project/>",
                ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: mvn pmd:pmd
""",
            },
            {
                "pom.xml": "<project/>",
                ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: cat config/spotbugs-exclude.xml
""",
            },
            {
                "pom.xml": "<project/>",
                ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: echo com.github.spotbugs
""",
            },
            {
                "pom.xml": "<project/>",
                ".github/workflows/ci.yml": """\
name: CI
on: push
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: echo "spotbugs should run later"
""",
            },
        ],
    )
    def test_linter_enforcement_fail(self, tmp_path: Path, files: dict[str, str] | None) -> None:
        from ai_harness_scorecard.checks.constraints import LinterEnforcementCheck

        context = _build_context(tmp_path, files)
        result = LinterEnforcementCheck().run(context)
        assert not result.passed


class TestTestSuiteExistsCheck:
    def test_test_suite_exists_pass_gradlew(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import TestSuiteExistsCheck

        ci_content = """
name: Unit Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew test
"""
        context = _build_context(
            tmp_path, {"src/test/README.md": "", ".github/workflows/ci.yml": ci_content}
        )
        result = TestSuiteExistsCheck().run(context)
        assert result.passed

    def test_test_suite_exists_pass_gradlew_no_dot_slash(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import TestSuiteExistsCheck

        ci_content = """
name: Test
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: gradlew test
"""
        context = _build_context(
            tmp_path, {"src/test/README.md": "", ".github/workflows/ci.yml": ci_content}
        )
        result = TestSuiteExistsCheck().run(context)
        assert result.passed

    def test_test_suite_exists_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import TestSuiteExistsCheck

        context = _build_context(tmp_path)
        result = TestSuiteExistsCheck().run(context)
        assert not result.passed


class TestAPIContractsCheck:
    def test_api_contracts_pass_springdoc(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import APIContractsCheck

        gradle_content = """
dependencies {
    implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.0")
}
"""
        context = _build_context(tmp_path, {"build.gradle.kts": gradle_content})
        result = APIContractsCheck().run(context)
        assert result.passed

    def test_api_contracts_pass_openapi_yaml(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import APIContractsCheck

        context = _build_context(tmp_path, {"openapi.yaml": "openapi: 3.0.0"})
        result = APIContractsCheck().run(context)
        assert result.passed

    def test_api_contracts_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.documentation import APIContractsCheck

        context = _build_context(tmp_path)
        result = APIContractsCheck().run(context)
        assert not result.passed


class TestFormatterEnforcementCheck:
    def test_formatter_enforcement_pass_ktlint(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        ci_content = """
name: Lint
on: push
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew clean ktlintCheck
"""
        context = _build_context(tmp_path, {".github/workflows/ci.yml": ci_content})
        result = FormatterEnforcementCheck().run(context)
        assert result.passed

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

    def test_formatter_enforcement_pass_gradle_spotless(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        gradle_content = """
        plugins {
            id "com.diffplug.spotless" version "6.13.0"
        }
        """
        context = _build_context(tmp_path, {"build.gradle": gradle_content})
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "spotless plugin found" in result.evidence.lower()

    def test_formatter_enforcement_pass_kotlin_gradle_spotless(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        gradle_content = """
        plugins {
            id("com.diffplug.spotless") version "6.13.0"
        }
        """
        # RepoContext detects kotlin if build.gradle.kts exists
        context = _build_context(tmp_path, {"build.gradle.kts": gradle_content, "src/Main.kt": ""})
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "spotless plugin found" in result.evidence.lower()

    def test_formatter_enforcement_pass_nested_gradle_spotless(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        gradle_content = """
        plugins {
            id "com.diffplug.spotless" version "6.13.0"
        }
        """
        context = _build_context(tmp_path, {"services/app/build.gradle": gradle_content})
        result = FormatterEnforcementCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert "spotless plugin found" in result.evidence.lower()

    def test_no_credit_for_checkstyle_xml(self, tmp_path: Path) -> None:
        """checkstyle is a linter, not a formatter — no formatter points for checkstyle.xml."""
        from ai_harness_scorecard.checks.constraints import FormatterEnforcementCheck

        context = _build_context(
            tmp_path, {"pom.xml": "<project/>", "checkstyle.xml": "<checkstyle/>"}
        )
        result = FormatterEnforcementCheck().run(context)
        assert not result.passed
        assert result.score == pytest.approx(0.0)


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

    def test_dependency_auditing_pass_dependabot_config(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import DependencyAuditingCheck

        dependabot_content = """
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
"""
        context = _build_context(tmp_path, {".github/dependabot.yml": dependabot_content})
        result = DependencyAuditingCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(1.0)

    def test_dependency_auditing_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.constraints import DependencyAuditingCheck

        context = _build_context(tmp_path)
        result = DependencyAuditingCheck().run(context)
        assert not result.passed
        assert result.score == pytest.approx(0.0)


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

    def test_property_based_testing_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import PropertyBasedTestingCheck

        context = _build_context(tmp_path)
        result = PropertyBasedTestingCheck().run(context)
        assert not result.passed
        assert result.score == pytest.approx(0.0)


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


class TestFuzzTestingCheck:
    def test_pass_with_jazzer_in_pom(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import FuzzTestingCheck

        pom_content = "<project><dependency>jazzer-junit</dependency></project>"
        context = _build_context(tmp_path, {"pom.xml": pom_content})
        result = FuzzTestingCheck().run(context)
        assert result.passed
        assert "pom.xml" in result.evidence

    def test_pass_with_jazzer_in_gradle(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import FuzzTestingCheck

        gradle_content = "dependencies { testImplementation 'com.code-intelligence:jazzer-junit' }"
        context = _build_context(tmp_path, {"build.gradle": gradle_content})
        result = FuzzTestingCheck().run(context)
        assert result.passed
        assert "build.gradle" in result.evidence

    def test_pass_with_java_fuzz_test_file(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import FuzzTestingCheck

        context = _build_context(
            tmp_path, {"src/test/java/MyFuzzTest.java": "@FuzzTest void test() {}"}
        )
        result = FuzzTestingCheck().run(context)
        assert result.passed
        assert "MyFuzzTest.java" in result.evidence

    def test_fuzz_testing_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.testing import FuzzTestingCheck

        context = _build_context(tmp_path)
        result = FuzzTestingCheck().run(context)
        assert not result.passed
        assert result.score == pytest.approx(0.0)


FULL_PR_TEMPLATE = """\
## What does this PR do?

<!-- Describe the change -->

## Testing

<!-- How did you verify this change works? -->

## Risk

<!-- What could break? -->

## How to revert

<!-- Revert the merge commit, or turn off the flag -->
"""

MR_TEMPLATE_SECTION_PHRASES: dict[str, list[str]] = {
    "Testing": ["test plan", "testing", "how was this tested", "how has this been tested"],
    "Risk": ["risk", "risks", "impact", "risk assessment"],
    "How to revert": ["revert", "rollback", "roll back", "rollback plan", "how to undo"],
}

MR_TEMPLATE_HEADING_STYLES = ["# {}", "## {}", "###### {}?", "**{}**", "- **{}:**", "{}:", "- {}:"]


class TestMRTemplateCheck:
    def test_mr_template_pass(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        context = _build_context(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": FULL_PR_TEMPLATE})
        result = MRTemplateCheck().run(context)
        assert result.passed
        assert result.score == pytest.approx(2.0)
        assert ".github/PULL_REQUEST_TEMPLATE.md" in result.evidence

    def test_mr_template_pass_with_bold_and_label_lines(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        template = "**Test plan**\n\n- **Impact:** low / medium / high\n\nRollback plan:\n"
        context = _build_context(tmp_path, {".github/pull_request_template.md": template})
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(2.0)

    def test_mr_template_partial_missing_risk_and_revert(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        template = "## Summary\n\n## Testing\n\nIf this is risky, explain how to revert it.\n"
        context = _build_context(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": template})
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(1.0)
        assert "## Risk" in result.remediation
        assert "## How to revert" in result.remediation
        assert "Testing" not in result.remediation

    def test_mr_template_partial_ignores_headings_in_html_comments(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        template = "## Testing\n\n<!--\n## Risk\n## How to revert\n-->\n"
        context = _build_context(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": template})
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(1.0)

    @pytest.mark.parametrize("fence", ["```", "~~~", "````markdown"])
    def test_mr_template_partial_ignores_headings_in_code_fences(
        self, tmp_path: Path, fence: str
    ) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        closing = fence.rstrip("markdown")
        template = f"## Testing\n\n{fence}\n## Risk\n## How to revert\n{closing}\n"
        context = _build_context(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": template})
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(1.0)
        assert "## Risk" in result.remediation

    def test_mr_template_pass_with_sections_after_code_fence(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        template = "## Testing\n\n```bash\npytest\n```\n\n## Risk\n\n## How to revert\n"
        context = _build_context(tmp_path, {".github/PULL_REQUEST_TEMPLATE.md": template})
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(2.0)

    def test_mr_template_pass_if_any_gitlab_template_is_complete(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        context = _build_context(
            tmp_path,
            {
                ".gitlab/merge_request_templates/Bug.md": "## Testing\n",
                ".gitlab/merge_request_templates/Default.md": FULL_PR_TEMPLATE,
            },
        )
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(2.0)
        assert "Default.md" in result.evidence

    def test_mr_template_partial_reports_closest_template(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        context = _build_context(
            tmp_path,
            {
                ".gitlab/merge_request_templates/A.md": "## Summary\n",
                ".gitlab/merge_request_templates/B.md": "## Testing\n## Risk\n",
            },
        )
        result = MRTemplateCheck().run(context)
        assert result.score == pytest.approx(1.0)
        assert "B.md" in result.remediation
        assert result.remediation.endswith("## How to revert.")

    def test_mr_template_partial_with_empty_gitlab_dir(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        (tmp_path / ".gitlab" / "merge_request_templates").mkdir(parents=True)
        result = MRTemplateCheck().run(_build_context(tmp_path))
        assert result.score == pytest.approx(1.0)
        assert "## Testing, ## Risk, ## How to revert" in result.remediation

    def test_mr_template_fail(self, tmp_path: Path) -> None:
        from ai_harness_scorecard.checks.review import MRTemplateCheck

        result = MRTemplateCheck().run(_build_context(tmp_path))
        assert not result.passed
        assert result.score == pytest.approx(0.0)

    @given(
        section=st.sampled_from(sorted(MR_TEMPLATE_SECTION_PHRASES)),
        style=st.sampled_from(MR_TEMPLATE_HEADING_STYLES),
        data=st.data(),
    )
    def test_mr_template_heading_variants_detected(
        self, section: str, style: str, data: st.DataObject
    ) -> None:
        from ai_harness_scorecard.checks.review import find_template_sections

        phrase = data.draw(st.sampled_from(MR_TEMPLATE_SECTION_PHRASES[section]))
        upper = data.draw(st.lists(st.booleans(), min_size=len(phrase), max_size=len(phrase)))
        cased = "".join(c.upper() if u else c.lower() for c, u in zip(phrase, upper, strict=True))
        assert section in find_template_sections(style.format(cased))

    @given(
        section=st.sampled_from(sorted(MR_TEMPLATE_SECTION_PHRASES)),
        data=st.data(),
    )
    def test_mr_template_prose_mentions_not_detected(
        self, section: str, data: st.DataObject
    ) -> None:
        from ai_harness_scorecard.checks.review import find_template_sections

        phrase = data.draw(st.sampled_from(MR_TEMPLATE_SECTION_PHRASES[section]))
        prose = f"Please describe the {phrase} in a sentence or two.\n<!-- ## {phrase} -->"
        assert find_template_sections(prose) == frozenset()
