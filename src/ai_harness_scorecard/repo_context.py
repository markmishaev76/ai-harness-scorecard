"""Repository context: pre-scanned file tree, language detection, and CI config access."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from .ci_parser import CIConfig, parse_ci_configs

LANGUAGE_INDICATORS: dict[str, list[str]] = {
    "rust": ["Cargo.toml"],
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"],
    "javascript": ["package.json"],
    "typescript": ["tsconfig.json"],
    "go": ["go.mod"],
    "java": [
        "pom.xml",
        "*/pom.xml",
        "build.gradle",
        "*/build.gradle",
        "build.gradle.kts",
        "*/build.gradle.kts",
    ],
    "ruby": ["Gemfile"],
    "csharp": ["*.csproj", "*.sln"],
    "swift": ["Package.swift"],
    "kotlin": ["build.gradle.kts", "*/build.gradle.kts"],
}

IGNORED_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        "target",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
        "vendor",
        ".bundle",
        ".cargo",
    }
)


@dataclass
class RepoContext:
    """Pre-scanned repository state used by all checks."""

    path: Path
    file_tree: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    ci_configs: list[CIConfig] = field(default_factory=list)
    scripts: dict[str, str] = field(default_factory=dict)

    @classmethod
    def build(cls, repo_path: str | Path) -> RepoContext:
        path = Path(repo_path).resolve()
        ctx = cls(path=path)
        ctx.file_tree = ctx._scan_file_tree()
        ctx.languages = ctx._detect_languages()
        ctx.ci_configs = parse_ci_configs(path)
        ctx.scripts = ctx._load_scripts()
        return ctx

    def has_file(self, *patterns: str) -> str | None:
        """Return first file matching any of the glob patterns, or None."""
        for pattern in patterns:
            for file_path in self.file_tree:
                if fnmatch(file_path.lower(), pattern.lower()):
                    return file_path
        return None

    def find_files(self, *patterns: str) -> list[str]:
        """Return all files matching any of the glob patterns."""
        matches = []
        for pattern in patterns:
            for file_path in self.file_tree:
                if fnmatch(file_path.lower(), pattern.lower()):
                    matches.append(file_path)
        return matches

    def has_dir(self, *patterns: str) -> str | None:
        """Return first existing directory matching a pattern, or None."""
        for pattern in patterns:
            target = self.path / pattern
            if target.is_dir():
                return pattern
        return None

    def read_file(self, relative_path: str) -> str | None:
        """Read file contents, returning None if not found."""
        full_path = self.path / relative_path
        if not full_path.is_file():
            return None
        try:
            return full_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def search_file(self, relative_path: str, pattern: str) -> bool:
        """Return True if the file contains a regex match."""
        content = self.read_file(relative_path)
        if content is None:
            return False
        return bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))

    def search_any_file(self, file_patterns: list[str], text_pattern: str) -> str | None:
        """Search multiple files for a text pattern. Return first matching file or None."""
        for file_pat in file_patterns:
            for file_path in self.file_tree:
                if fnmatch(file_path.lower(), file_pat.lower()) and self.search_file(
                    file_path, text_pattern
                ):
                    return file_path
        return None

    def ci_has_command(self, pattern: str) -> bool:
        """Return True if any CI job contains a command matching the pattern."""
        regex = re.compile(pattern, re.IGNORECASE)
        for ci in self.ci_configs:
            for job in ci.jobs:
                if self._matches_command(job.commands, regex):
                    return True
        return False

    def ci_has_blocking_command(self, pattern: str) -> bool:
        """Return True if a non-allow_failure CI job contains a matching command."""
        regex = re.compile(pattern, re.IGNORECASE)
        for ci in self.ci_configs:
            for job in ci.jobs:
                if not job.allow_failure and self._matches_command(job.commands, regex):
                    return True
        return False

    def _matches_command(self, commands: list[str], regex: re.Pattern[str]) -> bool:
        """Helper to match a regex against a list of commands, including script resolution."""
        for cmd in commands:
            if regex.search(cmd):
                return True
            resolved = self._resolve_script(cmd)
            if resolved and regex.search(resolved):
                return True
        return False

    def ci_has_scheduled_job(self) -> bool:
        return any(ci.has_schedule for ci in self.ci_configs)

    def ci_raw_content(self) -> str:
        """Concatenated raw CI config content for text-level searches."""
        return "\n".join(ci.raw_content for ci in self.ci_configs)

    def _load_scripts(self) -> dict[str, str]:
        """Load scripts from package.json if it exists."""
        content = self.read_file("package.json")
        if not content:
            return {}
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                scripts = data.get("scripts", {})
                if isinstance(scripts, dict):
                    return {k: str(v) for k, v in scripts.items()}
        except (json.JSONDecodeError, TypeError):
            pass
        return {}

    def _resolve_script(self, command: str) -> str | None:
        """
        Attempt to resolve a script name from an npm/yarn/pnpm/bun invocation.
        Example: 'npm run lint' -> returns the content of 'lint' script.
        """
        parts = command.split()
        if len(parts) < 2:
            return None

        pkg_manager = parts[0].lower()
        if pkg_manager not in ("npm", "yarn", "pnpm", "bun"):
            return None

        script_name = None
        if parts[1].lower() == "run":
            if len(parts) >= 3:
                script_name = parts[2]
        elif pkg_manager in ("yarn", "pnpm", "bun"):
            # yarn, pnpm, and bun allow omitting 'run' for custom scripts
            script_name = parts[1]

        if script_name and script_name in self.scripts:
            return self.scripts[script_name]

        return None

    def _scan_file_tree(self) -> list[str]:
        files: list[str] = []
        for root, dirs, filenames in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for filename in filenames:
                full = Path(root) / filename
                files.append(str(full.relative_to(self.path)))
        return sorted(files)

    def _detect_languages(self) -> list[str]:
        detected: list[str] = []
        for lang, indicators in LANGUAGE_INDICATORS.items():
            for indicator in indicators:
                if self.has_file(indicator):
                    detected.append(lang)
                    break
        return sorted(detected)
