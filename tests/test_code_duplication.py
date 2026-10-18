"""Tests for deterministic code duplication measurement."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from ai_harness_scorecard.checks.testing import CodeDuplicationCheck
from ai_harness_scorecard.repo_context import RepoContext

if TYPE_CHECKING:
    from pathlib import Path


def _build_context(tmp_path: Path, files: dict[str, str]) -> RepoContext:
    for name, content in files.items():
        file_path = tmp_path / name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
    return RepoContext.build(tmp_path)


def _unique_source(prefix: str, line_count: int) -> str:
    return "\n".join(f"{prefix}_{index} = {index}" for index in range(line_count))


def _duplicate_block() -> list[str]:
    return [
        (
            f"shared_{index} = build_value(input_{index}, config_{index}, options_{index}, "
            f"metadata_{index}, retries_{index})"
        )
        for index in range(5)
    ]


def _duplicate_files(total_lines: int) -> dict[str, str]:
    lines_per_file = total_lines // 2
    common = _duplicate_block()
    first = common + [f"first_{index} = {index}" for index in range(lines_per_file - 5)]
    second = common + [f"second_{index} = {index}" for index in range(lines_per_file - 5)]
    return {"src/first.py": "\n".join(first), "src/second.py": "\n".join(second)}


def _github_job(command: str, *, continue_on_error: bool = False) -> str:
    continue_setting = f"\n    continue-on-error: {str(continue_on_error).lower()}"
    return f"""\
name: CI
on: push
jobs:
  duplication:
    runs-on: ubuntu-latest{continue_setting}
    steps:
      - run: {command}
"""


class TestCodeDuplicationCheck:
    def test_testing_code_duplication_pass(self, tmp_path: Path) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": _github_job("jscpd --threshold 5 src"),
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.passed
        assert result.score == pytest.approx(3.0)
        assert "0.00% (0/10 lines)" in result.evidence
        assert "blocking duplication limit found" in result.evidence

    def test_testing_code_duplication_fail(self, tmp_path: Path) -> None:
        context = _build_context(tmp_path, _duplicate_files(60))

        result = CodeDuplicationCheck().run(context)

        assert not result.passed
        assert result.score == pytest.approx(0.0)
        assert "16.67% (10/60 lines)" in result.evidence
        assert "src/first.py:1-5" in result.remediation

    @pytest.mark.parametrize(
        ("total_lines", "expected_score", "expected_percentage"),
        [
            (210, 2.0, "4.76%"),
            (120, 1.0, "8.33%"),
            (60, 0.0, "16.67%"),
        ],
    )
    def test_testing_code_duplication_thresholds(
        self,
        tmp_path: Path,
        total_lines: int,
        expected_score: float,
        expected_percentage: str,
    ) -> None:
        context = _build_context(tmp_path, _duplicate_files(total_lines))

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(expected_score)
        assert expected_percentage in result.evidence

    def test_testing_code_duplication_detects_same_file_blocks(self, tmp_path: Path) -> None:
        common = _duplicate_block()
        source = "\n".join(common + ["separator = 1"] + common)
        context = _build_context(tmp_path, {"src/app.py": source})

        result = CodeDuplicationCheck().run(context)

        assert "(10/11 lines)" in result.evidence

    def test_testing_code_duplication_detects_cross_file_blocks(self, tmp_path: Path) -> None:
        common = "\n".join(_duplicate_block())
        context = _build_context(
            tmp_path,
            {"src/first.py": common, "src/second.py": common},
        )

        result = CodeDuplicationCheck().run(context)

        assert "100.00% (10/10 lines)" in result.evidence

    def test_testing_code_duplication_reports_matching_partner_ranges(self, tmp_path: Path) -> None:
        common = _duplicate_block() + [
            "shared_final = build_value(final, config, options, meta, retries)"
        ]
        context = _build_context(
            tmp_path,
            {"src/first.py": "\n".join(common), "src/second.py": "\n".join(common)},
        )

        result = CodeDuplicationCheck().run(context)

        assert "src/first.py:1-6 ↔ src/second.py:1-6" in result.remediation

    def test_testing_code_duplication_counts_overlapping_lines_once(self, tmp_path: Path) -> None:
        source = "\n".join(_duplicate_block() * 2)
        context = _build_context(tmp_path, {"src/app.py": source})

        result = CodeDuplicationCheck().run(context)

        assert "100.00% (10/10 lines)" in result.evidence

    def test_testing_code_duplication_discards_overlapping_single_file_windows(
        self,
    ) -> None:
        duplicated_indexes: dict[str, set[int]] = defaultdict(set)

        CodeDuplicationCheck()._mark_duplicate_occurrences(
            [("src/app.py", 0), ("src/app.py", 5), ("src/app.py", 6)],
            duplicated_indexes,
        )

        assert duplicated_indexes["src/app.py"] == set(range(10))

    def test_testing_code_duplication_normalizes_whitespace_and_comments(
        self, tmp_path: Path
    ) -> None:
        first = "\n".join(["# comment", "", *_duplicate_block()])
        second = "\n".join(
            ["# another comment", *[line.replace(" ", "   ") for line in _duplicate_block()]]
        )
        context = _build_context(
            tmp_path,
            {"src/first.py": first, "src/second.py": second},
        )

        result = CodeDuplicationCheck().run(context)

        assert "100.00% (10/10 lines)" in result.evidence

    def test_testing_code_duplication_reads_each_source_file_once(self, tmp_path: Path) -> None:
        context = _build_context(tmp_path, {"src/app.py": _unique_source("value", 10)})

        with patch.object(context, "read_file", wraps=context.read_file) as read_file:
            CodeDuplicationCheck()._analyze(context)

        assert read_file.call_count == 1

    def test_testing_code_duplication_excludes_nonproduction_files(self, tmp_path: Path) -> None:
        duplicate = "\n".join(_duplicate_block())
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                "tests/first.py": duplicate,
                "tests/second.py": duplicate,
                "src/generated/first.py": duplicate,
                "src/generated/second.py": duplicate,
                "src/tool.py": f"# Code generated by a tool. DO NOT EDIT.\n{duplicate}",
                ".agents/skills/first.py": duplicate,
                ".agents/skills/second.py": duplicate,
                ".claude/skills/first.py": duplicate,
                ".claude/skills/second.py": duplicate,
                ".codex/skills/first.py": duplicate,
                ".codex/skills/second.py": duplicate,
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert "0.00% (0/10 lines)" in result.evidence

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("src/main/java/TestMatch.java", False),
            ("src/main/java/MatchTest.java", False),
            ("src/main/java/Contest.java", True),
            ("src/main/java/Testament.java", True),
            ("src/main/java/Match.java", True),
        ],
    )
    def test_testing_code_duplication_java_test_filename_conventions(
        self, path: str, expected: bool
    ) -> None:
        assert CodeDuplicationCheck()._is_production_source(path) is expected

    @pytest.mark.parametrize(
        "command",
        [
            "jscpd --threshold=5 src",
            "jscpd --threshold 0.5 src",
            "pylint --enable=R0801 src",
            "pylint --enable=duplicate-code src",
            "sonar-scanner -Dsonar.qualitygate.wait=true",
            "mvn pmd:cpd-check",
            "./mvnw verify -Dcpd.failOnViolation=true",
        ],
    )
    def test_testing_code_duplication_detects_blocking_ci_controls(
        self, tmp_path: Path, command: str
    ) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": _github_job(command),
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(3.0)
        assert "blocking duplication limit found" in result.evidence

    @pytest.mark.parametrize(
        ("command", "expected_score", "expected_evidence"),
        [
            ("jscpd --threshold 0 src", 2.5, "without a blocking limit"),
            (
                "pylint --disable=duplicate-code src",
                2.0,
                "no duplication control found",
            ),
            (
                "pylint --enable=duplicate-code --disable=duplicate-code src",
                2.0,
                "no duplication control found",
            ),
            (
                "sonar-scanner -Dsonar.qualitygate.wait=false",
                2.5,
                "without a blocking limit",
            ),
            (
                "sonar-scanner -Dsonar.qualitygate.wait=trueish",
                2.5,
                "without a blocking limit",
            ),
        ],
    )
    def test_testing_code_duplication_rejects_disabled_or_zero_ci_controls(
        self,
        tmp_path: Path,
        command: str,
        expected_score: float,
        expected_evidence: str,
    ) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": _github_job(command),
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(expected_score)
        assert expected_evidence in result.evidence

    def test_testing_code_duplication_gives_partial_ci_credit(self, tmp_path: Path) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": _github_job("pmd cpd --minimum-tokens 50"),
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.5)
        assert "without a blocking limit" in result.evidence

    def test_testing_code_duplication_detects_nonblocking_ci_control(self, tmp_path: Path) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": _github_job(
                    "jscpd --threshold 5 src", continue_on_error=True
                ),
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.5)
        assert "without a blocking limit" in result.evidence

    def test_testing_code_duplication_detects_jscpd_action_threshold(self, tmp_path: Path) -> None:
        workflow = """\
name: CI
on: push
jobs:
  duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
        with:
          threshold: 5
"""
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": workflow,
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(3.0)
        assert "blocking duplication limit found" in result.evidence

    def test_testing_code_duplication_rejects_zero_jscpd_action_threshold(
        self, tmp_path: Path
    ) -> None:
        workflow = """\
name: CI
on: push
jobs:
  duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
        with:
          threshold: 0
"""
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": workflow,
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.5)
        assert "without a blocking limit" in result.evidence

    def test_testing_code_duplication_keeps_action_thresholds_in_same_step(
        self, tmp_path: Path
    ) -> None:
        workflow = """\
name: CI
on: push
jobs:
  duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
      - uses: kucherenko/jscpd@v5
        continue-on-error: true
        with:
          threshold: 5
"""
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": workflow,
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.5)
        assert "without a blocking limit" in result.evidence

    def test_testing_code_duplication_keeps_action_thresholds_in_same_job(
        self, tmp_path: Path
    ) -> None:
        workflow = """\
name: CI
on: push
jobs:
  blocking:
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
  advisory:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
        with:
          threshold: 5
"""
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".github/workflows/ci.yml": workflow,
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.5)
        assert "without a blocking limit" in result.evidence

    def test_testing_code_duplication_configuration_only_has_no_ci_credit(
        self, tmp_path: Path
    ) -> None:
        context = _build_context(
            tmp_path,
            {
                "src/app.py": _unique_source("value", 10),
                ".jscpd.json": '{"threshold": 5}',
            },
        )

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(2.0)
        assert "configuration found" in result.evidence

    def test_testing_code_duplication_is_not_applicable(self, tmp_path: Path) -> None:
        context = _build_context(tmp_path, {"README.md": "# Small repository"})

        result = CodeDuplicationCheck().run(context)

        assert result.score == pytest.approx(3.0)
        assert "does not apply" in result.evidence

    def test_testing_code_duplication_is_deterministic(self, tmp_path: Path) -> None:
        context = _build_context(tmp_path, _duplicate_files(60))
        check = CodeDuplicationCheck()

        first = check.run(context)
        second = check.run(context)

        assert first == second

    def test_testing_code_duplication_ignores_short_lexical_blocks(self, tmp_path: Path) -> None:
        imports = "\n".join(f"import module_{index}" for index in range(5))
        context = _build_context(
            tmp_path,
            {"src/first.py": imports, "src/second.py": imports},
        )

        analysis = CodeDuplicationCheck()._analyze(context)

        assert analysis.duplicated_lines == 0

    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        unique_line_count=st.integers(min_value=0, max_value=80),
        duplicate_count=st.integers(min_value=0, max_value=12),
    )
    def test_testing_code_duplication_analysis_invariants(
        self,
        tmp_path: Path,
        unique_line_count: int,
        duplicate_count: int,
    ) -> None:
        duplicate_block = _duplicate_block()
        unique_lines = [f"unique_{index} = {index}" for index in range(unique_line_count)]
        source = "\n".join(unique_lines + duplicate_block * duplicate_count)
        context = _build_context(tmp_path, {"src/property.py": source})

        analysis = CodeDuplicationCheck()._analyze(context)

        assert 0 <= analysis.duplicated_lines <= analysis.total_lines
        assert 0 <= analysis.percentage <= 100
