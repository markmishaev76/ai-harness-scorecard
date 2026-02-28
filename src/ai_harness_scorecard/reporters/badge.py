"""Shields.io endpoint badge JSON generator."""

from __future__ import annotations

import json

from ..models import Assessment, Grade

GRADE_COLORS = {
    Grade.A: "brightgreen",
    Grade.B: "blue",
    Grade.C: "yellow",
    Grade.D: "orange",
    Grade.F: "red",
}


def render_badge_json(assessment: Assessment) -> str:
    """Generate a shields.io endpoint badge JSON file.

    See https://shields.io/endpoint for the schema.
    """
    grade = assessment.grade
    score = assessment.overall_score

    return json.dumps(
        {
            "schemaVersion": 1,
            "label": "AI Harness Scorecard",
            "message": f"{grade.value} {score:.0f}/100",
            "color": GRADE_COLORS[grade],
            "namedLogo": "shield",
        },
        indent=2,
    )


def badge_url(
    owner: str,
    repo: str,
    branch: str = "main",
    file: str = "scorecard-badge.json",
) -> str:
    """Return the shields.io badge URL for a repo that has the badge JSON committed."""
    raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file}"
    encoded = raw.replace(":", "%3A").replace("/", "%2F")
    return f"https://img.shields.io/endpoint?url={encoded}"


def badge_markdown(
    owner: str,
    repo: str,
    branch: str = "main",
    file: str = "scorecard-badge.json",
) -> str:
    """Return full Markdown badge snippet ready to paste into a README."""
    url = badge_url(owner, repo, branch, file)
    link = f"https://github.com/{owner}/{repo}"
    return f"[![AI Harness Scorecard]({url})]({link})"
