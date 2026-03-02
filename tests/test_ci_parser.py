"""Tests for CI configuration parsing."""

from __future__ import annotations

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
