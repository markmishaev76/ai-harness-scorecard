"""Check implementations for each scoring category."""

from .ai_safeguards import AI_SAFEGUARD_CHECKS
from .constraints import CONSTRAINT_CHECKS
from .documentation import DOCUMENTATION_CHECKS
from .review import REVIEW_CHECKS
from .testing import TESTING_CHECKS

ALL_CHECKS = {
    "documentation": DOCUMENTATION_CHECKS,
    "constraints": CONSTRAINT_CHECKS,
    "testing": TESTING_CHECKS,
    "review": REVIEW_CHECKS,
    "ai_safeguards": AI_SAFEGUARD_CHECKS,
}

__all__ = [
    "ALL_CHECKS",
    "DOCUMENTATION_CHECKS",
    "CONSTRAINT_CHECKS",
    "TESTING_CHECKS",
    "REVIEW_CHECKS",
    "AI_SAFEGUARD_CHECKS",
]
