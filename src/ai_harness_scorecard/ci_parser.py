"""Parse CI configuration files from different platforms into a unified model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pathlib import Path

import yaml

GITLAB_RESERVED_KEYS = frozenset(
    {
        "stages",
        "variables",
        "default",
        "include",
        "workflow",
        "image",
        "services",
        "before_script",
        "after_script",
        "cache",
        "artifacts",
        ".pre",
        ".post",
    }
)


@dataclass
class CIJob:
    """A single CI job with its commands and properties."""

    name: str
    commands: list[str] = field(default_factory=list)
    allow_failure: bool = False
    stage: str | None = None


@dataclass
class CIConfig:
    """Parsed CI configuration from one file."""

    ci_type: str
    jobs: list[CIJob] = field(default_factory=list)
    has_schedule: bool = False
    raw_content: str = ""


def parse_ci_configs(repo_path: Path) -> list[CIConfig]:
    """Discover and parse all CI config files in a repository."""
    configs: list[CIConfig] = []

    gitlab_ci = repo_path / ".gitlab-ci.yml"
    if gitlab_ci.is_file():
        config = _parse_gitlab_ci(gitlab_ci)
        if config:
            configs.append(config)

    github_workflows = repo_path / ".github" / "workflows"
    if github_workflows.is_dir():
        for suffix in ("*.yml", "*.yaml"):
            for workflow_file in sorted(github_workflows.glob(suffix)):
                config = _parse_github_actions(workflow_file)
                if config:
                    configs.append(config)

    return configs


def _parse_gitlab_ci(path: Path) -> CIConfig | None:
    raw, data = _load_yaml(path)
    if data is None:
        return None

    config = CIConfig(ci_type="gitlab", raw_content=raw)
    _detect_gitlab_schedule(data, config)

    for key, value in data.items():
        if key.startswith(".") or key in GITLAB_RESERVED_KEYS:
            continue
        if not isinstance(value, dict):
            continue

        config.jobs.append(
            CIJob(
                name=key,
                commands=_extract_gitlab_commands(value),
                allow_failure=bool(value.get("allow_failure", False)),
                stage=value.get("stage"),
            )
        )

    return config


def _detect_gitlab_schedule(data: dict[str, Any], config: CIConfig) -> None:
    for value in data.values():
        if not isinstance(value, dict):
            continue
        rules = value.get("rules", [])
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if isinstance(rule, dict):
                condition = str(rule.get("if", ""))
                if "schedule" in condition.lower():
                    config.has_schedule = True
                    return


def _extract_gitlab_commands(job_data: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    for key in ("before_script", "script", "after_script"):
        scripts = job_data.get(key, [])
        if isinstance(scripts, list):
            commands.extend(str(s) for s in scripts)
        elif isinstance(scripts, str):
            commands.append(scripts)
    return commands


def _parse_github_actions(path: Path) -> CIConfig | None:
    raw, data = _load_yaml(path)
    if data is None:
        return None

    config = CIConfig(ci_type="github", raw_content=raw)
    config.has_schedule = _is_github_scheduled(data)

    jobs_data = data.get("jobs", {})
    if not isinstance(jobs_data, dict):
        return config

    for job_name, job_data in jobs_data.items():
        if isinstance(job_data, dict):
            config.jobs.append(_create_github_job(job_name, job_data))

    return config


def _is_github_scheduled(data: dict[str, Any]) -> bool:
    # In some YAML parsers, 'on' is interpreted as True (boolean)
    on_triggers = data.get("on")
    if on_triggers is None:
        on_triggers = data.get(cast("str", True))

    return isinstance(on_triggers, dict) and "schedule" in on_triggers


def _create_github_job(name: str, data: dict[str, Any]) -> CIJob:
    commands: list[str] = []

    job_uses = data.get("uses")
    if isinstance(job_uses, str):
        commands.append(f"uses: {job_uses}")

    for step in data.get("steps", []):
        if not isinstance(step, dict):
            continue
        if "run" in step:
            commands.append(str(step["run"]))
        if "uses" in step:
            commands.append(f"uses: {step['uses']}")

    return CIJob(
        name=name,
        commands=commands,
        allow_failure=bool(data.get("continue-on-error", False)),
    )


def _load_yaml(path: Path) -> tuple[str, dict[str, Any] | None]:
    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return raw, data
        return raw, None
    except (yaml.YAMLError, OSError):
        return "", None
