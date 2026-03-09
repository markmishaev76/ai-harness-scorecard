from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
import yaml

from ai_harness_scorecard.repo_context import RepoContext

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def repo_with_scripts(tmp_path: Path):
    """Create a temporary repo with a package.json containing scripts."""
    package_json = {
        "name": "test-repo",
        "scripts": {
            "lint": "eslint .",
            "test": "jest",
            "check": "ruff check ."
        }
    }
    (tmp_path / "package.json").write_text(json.dumps(package_json))
    return tmp_path


@pytest.mark.parametrize("pkg_manager_cmd", [
    "npm run lint",
    "yarn lint",
    "yarn run lint",
    "pnpm lint",
    "pnpm run lint",
    "bun lint",
    "bun run lint",
])
def test_script_resolution_pass(repo_with_scripts: Path, pkg_manager_cmd: str):
    """Test that various package manager invocations resolve correctly."""
    # Create CI config using the linter script
    ci_dir = repo_with_scripts / ".github" / "workflows"
    ci_dir.mkdir(parents=True)
    ci_config = {
        "name": "CI",
        "on": ["push"],
        "jobs": {
            "lint": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {"run": pkg_manager_cmd}
                ]
            }
        }
    }
    (ci_dir / "ci.yml").write_text(yaml.dump(ci_config))

    ctx = RepoContext.build(repo_with_scripts)

    # The linter pattern for eslint is just "eslint"
    assert ctx.ci_has_command("eslint") is True
    assert ctx.ci_has_blocking_command("eslint") is True


@pytest.mark.parametrize("pkg_manager_cmd", [
    "npm run other",
    "yarn other",
    "pnpm other",
    "bun run other",
])
def test_script_resolution_fail_missing_script(repo_with_scripts: Path, pkg_manager_cmd: str):
    """Test that resolution fails gracefully if the script is missing from package.json."""
    ci_dir = repo_with_scripts / ".github" / "workflows"
    ci_dir.mkdir(parents=True, exist_ok=True)
    ci_config = {
        "jobs": {"test": {"steps": [{"run": pkg_manager_cmd}]}}
    }
    (ci_dir / "ci.yml").write_text(yaml.dump(ci_config))

    ctx = RepoContext.build(repo_with_scripts)
    assert ctx.ci_has_command("eslint") is False


def test_script_resolution_blocking_vs_non_blocking(repo_with_scripts: Path):
    """Test blocking vs non-blocking script detection."""
    ci_dir = repo_with_scripts / ".github" / "workflows"
    ci_dir.mkdir(parents=True, exist_ok=True)
    ci_config = {
        "jobs": {
            "lint": {
                "continue-on-error": True,
                "steps": [{"run": "npm run lint"}]
            }
        }
    }
    (ci_dir / "ci.yml").write_text(yaml.dump(ci_config))

    ctx = RepoContext.build(repo_with_scripts)
    assert ctx.ci_has_command("eslint") is True
    assert ctx.ci_has_blocking_command("eslint") is False
