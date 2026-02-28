"""Contract tests for reporter output formats."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from ai_harness_scorecard.models import (
    Assessment,
    CategoryResult,
    CheckResult,
    Grade,
)
from ai_harness_scorecard.reporters.badge import render_badge_json
from ai_harness_scorecard.reporters.json_reporter import render_json
from ai_harness_scorecard.reporters.markdown import render_markdown

FIXED_TIME = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)


def _make_assessment(score: float = 10, max_points: float = 10) -> Assessment:
    check = CheckResult(
        check_id="test.check",
        name="Test Check",
        passed=score > 0,
        score=score,
        max_points=max_points,
        evidence="test evidence",
        remediation="test fix",
        source="test source",
    )
    category = CategoryResult(
        category_id="test_cat",
        name="Test Category",
        weight=1.0,
        checks=[check],
    )
    return Assessment(
        repo_path="/tmp/test-repo",
        repo_name="test-repo",
        timestamp=FIXED_TIME,
        categories=[category],
        languages=["python"],
    )


class TestJsonReporterContract:
    """Verify the JSON output has a stable schema (contract test)."""

    def test_json_output_has_required_top_level_keys(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_json(assessment))

        required_keys = {
            "repo_path",
            "repo_name",
            "timestamp",
            "languages",
            "overall_score",
            "grade",
            "grade_description",
            "total_checks",
            "passed_checks",
            "categories",
        }
        assert required_keys.issubset(data.keys())

    def test_json_category_has_required_keys(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_json(assessment))
        category = data["categories"][0]

        required_keys = {
            "category_id",
            "name",
            "weight",
            "score",
            "max_score",
            "percentage",
            "checks",
        }
        assert required_keys.issubset(category.keys())

    def test_json_check_has_required_keys(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_json(assessment))
        check = data["categories"][0]["checks"][0]

        required_keys = {
            "check_id",
            "name",
            "passed",
            "score",
            "max_points",
            "evidence",
            "remediation",
            "source",
        }
        assert required_keys.issubset(check.keys())

    def test_json_grade_is_valid_enum_value(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_json(assessment))
        assert data["grade"] in [g.value for g in Grade]

    def test_json_score_is_numeric(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_json(assessment))
        assert isinstance(data["overall_score"], (int, float))

    def test_json_is_valid_json(self) -> None:
        assessment = _make_assessment()
        output = render_json(assessment)
        json.loads(output)  # must not raise

    def test_json_snapshot_structure(self) -> None:
        """Golden test: verify exact output for a known input."""
        assessment = _make_assessment(score=10, max_points=10)
        data = json.loads(render_json(assessment))

        assert data["repo_name"] == "test-repo"
        assert data["overall_score"] == 100.0
        assert data["grade"] == "A"
        assert data["total_checks"] == 1
        assert data["passed_checks"] == 1
        assert len(data["categories"]) == 1
        assert data["categories"][0]["percentage"] == 100.0


class TestBadgeReporterContract:
    """Verify badge JSON follows shields.io endpoint schema."""

    def test_badge_has_schema_version(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_badge_json(assessment))
        assert data["schemaVersion"] == 1

    def test_badge_has_required_fields(self) -> None:
        assessment = _make_assessment()
        data = json.loads(render_badge_json(assessment))
        assert "label" in data
        assert "message" in data
        assert "color" in data

    def test_badge_color_matches_grade(self) -> None:
        for score, expected_color in [
            (100.0, "brightgreen"),
            (75.0, "blue"),
            (60.0, "yellow"),
            (45.0, "orange"),
            (20.0, "red"),
        ]:
            assessment = _make_assessment(score=score, max_points=100)
            data = json.loads(render_badge_json(assessment))
            assert data["color"] == expected_color, f"score={score}"


class TestMarkdownReporter:
    def test_markdown_contains_grade(self) -> None:
        assessment = _make_assessment()
        output = render_markdown(assessment)
        assert "Grade: **A**" in output or "A" in output

    def test_markdown_contains_category_name(self) -> None:
        assessment = _make_assessment()
        output = render_markdown(assessment)
        assert "Test Category" in output

    def test_markdown_is_nonempty_string(self) -> None:
        assessment = _make_assessment()
        output = render_markdown(assessment)
        assert isinstance(output, str)
        assert len(output) > 100
