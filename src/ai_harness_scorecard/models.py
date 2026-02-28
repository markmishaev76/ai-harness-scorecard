"""Core data models for assessment results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Grade(Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


GRADE_THRESHOLDS = {
    Grade.A: 85,
    Grade.B: 70,
    Grade.C: 55,
    Grade.D: 40,
    Grade.F: 0,
}

GRADE_DESCRIPTIONS = {
    Grade.A: "Strong harness. AI-generated code has robust mechanical safeguards.",
    Grade.B: "Good foundation. Some gaps in enforcement or feedback loops.",
    Grade.C: "Basic practices present but insufficient for safe AI scaling.",
    Grade.D: "Significant gaps. AI code likely accumulating undetected debt.",
    Grade.F: "No meaningful harness. AI output is essentially unaudited.",
}


def compute_grade(score: float) -> Grade:
    for grade in (Grade.A, Grade.B, Grade.C, Grade.D):
        if score >= GRADE_THRESHOLDS[grade]:
            return grade
    return Grade.F


@dataclass
class CheckResult:
    """Result of a single assessment check."""

    check_id: str
    name: str
    passed: bool
    score: float
    max_points: float
    evidence: str
    remediation: str
    source: str


@dataclass
class CategoryResult:
    """Aggregated results for one scoring category."""

    category_id: str
    name: str
    weight: float
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        return sum(c.score for c in self.checks)

    @property
    def max_score(self) -> float:
        return sum(c.max_points for c in self.checks)

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100

    @property
    def weighted_score(self) -> float:
        return self.percentage * self.weight


@dataclass
class Assessment:
    """Complete assessment of a repository."""

    repo_path: str
    repo_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    categories: list[CategoryResult] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        return sum(c.weighted_score for c in self.categories)

    @property
    def grade(self) -> Grade:
        return compute_grade(self.overall_score)

    @property
    def grade_description(self) -> str:
        return GRADE_DESCRIPTIONS[self.grade]

    @property
    def total_checks(self) -> int:
        return sum(len(c.checks) for c in self.categories)

    @property
    def passed_checks(self) -> int:
        return sum(1 for c in self.categories for ch in c.checks if ch.passed)
