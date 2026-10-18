"""Tests for CI configuration parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from ai_harness_scorecard.ci_parser import parse_ci_configs


def test_parse_github_actions_with_uses(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)

    ci_content = """
name: CI
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Snyk Scan
        uses: snyk/actions/maven@master
        with:
          args: --severity-threshold=high
      - name: Run audit
        run: ./mvnw audit
"""
    (workflow_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    configs = parse_ci_configs(tmp_path)
    assert len(configs) == 1
    assert configs[0].ci_type == "github"

    job = configs[0].jobs[0]
    assert job.name == "security"
    assert "uses: actions/checkout@v4" in job.commands
    assert "uses: snyk/actions/maven@master" in job.commands
    assert "./mvnw audit" in job.commands


def test_parse_github_actions_tracks_blocking_steps_and_action_inputs_pass(
    tmp_path: Path,
) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    ci_content = """\
name: CI
jobs:
  duplication:
    runs-on: ubuntu-latest
    steps:
      - uses: kucherenko/jscpd@v5
        with:
          threshold: 5
      - run: echo advisory
        continue-on-error: true
"""
    (workflow_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    job = parse_ci_configs(tmp_path)[0].jobs[0]

    assert job.blocking_commands == ["uses: kucherenko/jscpd@v5\nwith.threshold: 5"]


def test_parse_github_actions_continue_on_error_values(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    ci_content = """\
name: CI
jobs:
  quoted-false:
    continue-on-error: "false"
    steps:
      - run: ruff check .
        continue-on-error: "false"
  expression:
    continue-on-error: ${{ github.event_name == 'schedule' }}
    steps:
      - run: pip-audit
        continue-on-error: ${{ github.event_name == 'schedule' }}
  explicit-true:
    continue-on-error: true
    steps:
      - run: pytest
  true-step:
    steps:
      - run: jscpd --threshold 5 src
        continue-on-error: true
"""
    (workflow_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    jobs = {job.name: job for job in parse_ci_configs(tmp_path)[0].jobs}

    assert jobs["quoted-false"].allow_failure is False
    assert jobs["quoted-false"].blocking_commands == ["ruff check ."]
    assert jobs["expression"].allow_failure is False
    assert jobs["expression"].blocking_commands == ["pip-audit"]
    assert jobs["explicit-true"].allow_failure is True
    assert jobs["true-step"].blocking_commands == []


def test_parse_github_actions_schedule(tmp_path: Path) -> None:
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)

    ci_content = """
on:
  schedule:
    - cron: '0 0 * * *'
jobs:
  test:
    steps:
      - run: echo "hello"
"""
    (workflow_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    configs = parse_ci_configs(tmp_path)
    assert len(configs) == 1
    assert configs[0].has_schedule is True


def test_parse_github_actions_reusable_workflow_job(tmp_path: Path) -> None:
    """Job-level uses: (reusable workflow call) should appear in commands."""
    workflow_dir = tmp_path / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)

    ci_content = """\
name: Call reusable
jobs:
  call-shared-lint:
    uses: org/repo/.github/workflows/lint.yml@main
    with:
      foo: bar
"""
    (workflow_dir / "ci.yml").write_text(ci_content, encoding="utf-8")

    configs = parse_ci_configs(tmp_path)
    assert len(configs) == 1

    job = configs[0].jobs[0]
    assert job.name == "call-shared-lint"
    assert "uses: org/repo/.github/workflows/lint.yml@main" in job.commands
