"""Tests for scoring models and grade computation."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from ai_harness_scorecard.models import (
    Assessment,
    CategoryResult,
    CheckResult,
    Grade,
    compute_grade,
)


class TestComputeGrade:
    def test_grade_a_at_boundary(self) -> None:
        assert compute_grade(85.0) == Grade.A

    def test_grade_a_above(self) -> None:
        assert compute_grade(100.0) == Grade.A

    def test_grade_b_at_boundary(self) -> None:
        assert compute_grade(70.0) == Grade.B

    def test_grade_b_below_a(self) -> None:
        assert compute_grade(84.9) == Grade.B

    def test_grade_c_at_boundary(self) -> None:
        assert compute_grade(55.0) == Grade.C

    def test_grade_d_at_boundary(self) -> None:
        assert compute_grade(40.0) == Grade.D

    def test_grade_f_below_d(self) -> None:
        assert compute_grade(39.9) == Grade.F

    def test_grade_f_at_zero(self) -> None:
        assert compute_grade(0.0) == Grade.F


class TestComputeGradeProperties:
    """Property-based tests for grade computation."""

    @given(st.floats(min_value=85.0, max_value=100.0))
    def test_high_scores_are_grade_a(self, score: float) -> None:
        assert compute_grade(score) == Grade.A

    @given(st.floats(min_value=70.0, max_value=84.99))
    def test_good_scores_are_grade_b(self, score: float) -> None:
        assert compute_grade(score) == Grade.B

    @given(st.floats(min_value=55.0, max_value=69.99))
    def test_mid_scores_are_grade_c(self, score: float) -> None:
        assert compute_grade(score) == Grade.C

    @given(st.floats(min_value=40.0, max_value=54.99))
    def test_low_scores_are_grade_d(self, score: float) -> None:
        assert compute_grade(score) == Grade.D

    @given(st.floats(min_value=0.0, max_value=39.99))
    def test_failing_scores_are_grade_f(self, score: float) -> None:
        assert compute_grade(score) == Grade.F

    @given(st.floats(min_value=0.0, max_value=100.0))
    def test_grade_is_always_valid(self, score: float) -> None:
        grade = compute_grade(score)
        assert grade in Grade

    @given(st.floats(min_value=0.0, max_value=100.0))
    def test_grade_is_deterministic(self, score: float) -> None:
        assert compute_grade(score) == compute_grade(score)


class TestCategoryResult:
    def test_empty_category_scores_zero(self) -> None:
        cat = CategoryResult(category_id="test", name="Test", weight=0.25)
        assert cat.score == 0.0
        assert cat.max_score == 0.0
        assert cat.percentage == 0.0

    def test_full_score_category(self) -> None:
        checks = [
            CheckResult(
                check_id="a",
                name="A",
                passed=True,
                score=10,
                max_points=10,
                evidence="ok",
                remediation="",
                source="test",
            ),
            CheckResult(
                check_id="b",
                name="B",
                passed=True,
                score=5,
                max_points=5,
                evidence="ok",
                remediation="",
                source="test",
            ),
        ]
        cat = CategoryResult(category_id="test", name="Test", weight=0.25, checks=checks)
        assert cat.score == 15.0
        assert cat.max_score == 15.0
        assert cat.percentage == 100.0
        assert cat.weighted_score == 25.0

    def test_partial_score_category(self) -> None:
        checks = [
            CheckResult(
                check_id="a",
                name="A",
                passed=True,
                score=10,
                max_points=10,
                evidence="ok",
                remediation="",
                source="test",
            ),
            CheckResult(
                check_id="b",
                name="B",
                passed=False,
                score=0,
                max_points=10,
                evidence="missing",
                remediation="fix it",
                source="test",
            ),
        ]
        cat = CategoryResult(category_id="test", name="Test", weight=0.20, checks=checks)
        assert cat.percentage == 50.0
        assert cat.weighted_score == 10.0


class TestCategoryResultProperties:
    """Property-based tests for category score math."""

    @given(
        st.floats(min_value=0.0, max_value=100.0),
        st.floats(min_value=0.0, max_value=100.0),
        st.floats(min_value=0.01, max_value=1.0),
    )
    def test_weighted_score_never_exceeds_weight_times_100(
        self,
        score: float,
        max_points: float,
        weight: float,
    ) -> None:
        if max_points < score:
            max_points = score
        check = CheckResult(
            check_id="x",
            name="X",
            passed=True,
            score=score,
            max_points=max_points,
            evidence="",
            remediation="",
            source="",
        )
        cat = CategoryResult(category_id="t", name="T", weight=weight, checks=[check])
        assert cat.weighted_score <= weight * 100 + 0.01  # float tolerance

    @given(st.floats(min_value=0.0, max_value=1.0))
    def test_empty_category_weighted_score_is_zero(self, weight: float) -> None:
        cat = CategoryResult(category_id="t", name="T", weight=weight)
        assert cat.weighted_score == 0.0


class TestAssessment:
    def test_overall_score_sums_weighted(self) -> None:
        check_pass = CheckResult(
            check_id="a",
            name="A",
            passed=True,
            score=10,
            max_points=10,
            evidence="ok",
            remediation="",
            source="test",
        )
        cat1 = CategoryResult(
            category_id="c1",
            name="C1",
            weight=0.5,
            checks=[check_pass],
        )
        cat2 = CategoryResult(
            category_id="c2",
            name="C2",
            weight=0.5,
            checks=[check_pass],
        )
        assessment = Assessment(
            repo_path="/tmp/test",
            repo_name="test",
            categories=[cat1, cat2],
        )
        assert assessment.overall_score == 100.0
        assert assessment.grade == Grade.A
        assert assessment.total_checks == 2
        assert assessment.passed_checks == 2
