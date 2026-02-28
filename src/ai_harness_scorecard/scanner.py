"""Orchestrates all checks and produces an Assessment."""

from __future__ import annotations

from pathlib import Path

from .checks import ALL_CHECKS
from .models import Assessment, CategoryResult
from .repo_context import RepoContext

CATEGORY_CONFIG = {
    "documentation": ("Architectural Documentation", 0.20),
    "constraints": ("Mechanical Constraints", 0.25),
    "testing": ("Testing & Stability", 0.25),
    "review": ("Review & Drift Prevention", 0.15),
    "ai_safeguards": ("AI-Specific Safeguards", 0.15),
}


def assess_repo(repo_path: str | Path) -> Assessment:
    """Run all checks against a repository and return the full assessment."""
    path = Path(repo_path).resolve()
    context = RepoContext.build(path)

    categories = []
    for category_id, checks in ALL_CHECKS.items():
        name, weight = CATEGORY_CONFIG[category_id]
        result = CategoryResult(
            category_id=category_id,
            name=name,
            weight=weight,
        )
        for check in checks:
            result.checks.append(check.run(context))
        categories.append(result)

    return Assessment(
        repo_path=str(path),
        repo_name=path.name,
        categories=categories,
        languages=context.languages,
    )
