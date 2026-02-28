# Architecture

## Overview

`ai-harness-scorecard` is a CLI tool that assesses Git repositories against engineering best practices for safe AI-assisted development. It scans files, parses CI configs, and produces graded reports.

## Module Layout

```
src/ai_harness_scorecard/
├── cli.py           # Click CLI, terminal rendering with Rich
├── scanner.py       # Orchestrator: builds RepoContext, runs all checks, returns Assessment
├── models.py        # Data classes: Assessment, CategoryResult, CheckResult, Grade
├── repo_context.py  # Pre-scanned repo state: file tree, languages, CI config access
├── ci_parser.py     # Parse GitLab CI / GitHub Actions YAML into unified CIConfig model
├── checks/          # One module per category, each exporting a list of BaseCheck instances
│   ├── base.py
│   ├── documentation.py
│   ├── constraints.py
│   ├── testing.py
│   ├── review.py
│   └── ai_safeguards.py
├── reporters/       # Output formatters (Markdown, JSON)
│   ├── markdown.py
│   └── json_reporter.py
└── platforms/       # (Future) GitHub/GitLab API adapters for remote checks
```

## Dependency Rules

- `checks/` modules depend on `base.py`, `models.py`, and `repo_context.py`. They never depend on `cli.py`, `scanner.py`, or `reporters/`.
- `scanner.py` depends on `checks/`, `models.py`, and `repo_context.py`. It never depends on `cli.py` or `reporters/`.
- `reporters/` depend only on `models.py`. They never depend on `checks/` or `scanner.py`.
- `cli.py` depends on `scanner.py` and `reporters/`. It is the only module that uses Rich.
- `ci_parser.py` has no internal dependencies. `repo_context.py` is its only consumer.

## Data Flow

```
CLI (cli.py)
  └─> scanner.assess_repo(path)
        ├─> RepoContext.build(path)     # scan files, parse CI
        ├─> for each category:
        │     for each check:
        │       check.run(context) -> CheckResult
        └─> return Assessment
  └─> reporter.render(assessment) -> string output
```

## Adding a Check

1. Create a class in the appropriate `checks/*.py` file inheriting from `BaseCheck`
2. Set `check_id`, `name`, `description`, `max_points`, and `source`
3. Implement `run(context) -> CheckResult` using `pass_result()`, `fail_result()`, or `partial_result()`
4. Add the instance to the module's `*_CHECKS` list
5. The scanner picks it up automatically via `checks/__init__.py`

## Design Decisions

- **No LLM dependency**: all checks are deterministic pattern matching and file analysis. Reproducible, fast, CI-friendly.
- **Unified CI model**: different CI platforms (GitLab, GitHub Actions) are normalized into `CIConfig`/`CIJob` so checks don't need platform-specific logic.
- **Additive scoring**: checks add points, they don't subtract. A repo is never penalized for checks that don't apply to its language/platform.
