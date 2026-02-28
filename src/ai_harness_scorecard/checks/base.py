"""Base class for all assessment checks."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import CheckResult
from ..repo_context import RepoContext


class BaseCheck(ABC):
    """A single assessable practice with a point value and research citation."""

    check_id: str
    name: str
    description: str
    max_points: float
    source: str

    @abstractmethod
    def run(self, context: RepoContext) -> CheckResult: ...

    def pass_result(self, evidence: str) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            passed=True,
            score=self.max_points,
            max_points=self.max_points,
            evidence=evidence,
            remediation="",
            source=self.source,
        )

    def fail_result(self, evidence: str, remediation: str) -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            passed=False,
            score=0.0,
            max_points=self.max_points,
            evidence=evidence,
            remediation=remediation,
            source=self.source,
        )

    def partial_result(self, score: float, evidence: str, remediation: str = "") -> CheckResult:
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            passed=score > 0,
            score=min(score, self.max_points),
            max_points=self.max_points,
            evidence=evidence,
            remediation=remediation,
            source=self.source,
        )
