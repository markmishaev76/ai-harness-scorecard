"""JSON report generator."""

from __future__ import annotations

import json

from ..models import Assessment


def render_json(assessment: Assessment) -> str:
    """Render a full assessment as JSON."""
    return json.dumps(_serialize(assessment), indent=2)


def _serialize(assessment: Assessment) -> dict:
    return {
        "repo_path": assessment.repo_path,
        "repo_name": assessment.repo_name,
        "timestamp": assessment.timestamp.isoformat(),
        "languages": assessment.languages,
        "overall_score": round(assessment.overall_score, 1),
        "grade": assessment.grade.value,
        "grade_description": assessment.grade_description,
        "total_checks": assessment.total_checks,
        "passed_checks": assessment.passed_checks,
        "categories": [_serialize_category(c) for c in assessment.categories],
    }


def _serialize_category(category) -> dict:
    return {
        "category_id": category.category_id,
        "name": category.name,
        "weight": category.weight,
        "score": round(category.score, 1),
        "max_score": round(category.max_score, 1),
        "percentage": round(category.percentage, 1),
        "checks": [_serialize_check(c) for c in category.checks],
    }


def _serialize_check(check) -> dict:
    return {
        "check_id": check.check_id,
        "name": check.name,
        "passed": check.passed,
        "score": round(check.score, 1),
        "max_points": round(check.max_points, 1),
        "evidence": check.evidence,
        "remediation": check.remediation,
        "source": check.source,
    }
