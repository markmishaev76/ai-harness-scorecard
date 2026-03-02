# Contributing to AI Harness Scorecard

## Development Setup

```bash
git clone https://github.com/markmishaev76/ai-harness-scorecard
cd ai-harness-scorecard
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest --cov=ai_harness_scorecard --cov-report=term-missing
```

## Code Quality

All of these run in CI and must pass before merge:

```bash
ruff check src/ tests/          # lint
ruff format --check src/ tests/ # format
mypy src/                       # type check
bandit -r src/ -c pyproject.toml # security lint
pip-audit                       # dependency audit
```

## AI Usage Norms

AI-assisted code is welcome, but must meet the same standards as hand-written code:

1. **Review required**: all AI-generated code must be reviewed by a human before merge. The reviewer is responsible for correctness, not the AI.
2. **Tests first**: every new check needs tests (pass case + fail case) before the implementation is considered complete. Write or verify tests manually.
3. **No blind acceptance**: if an AI suggests a change you don't fully understand, don't merge it. Ask questions or rewrite.
4. **Small PRs**: keep pull requests focused. One check or one feature per PR. Large AI-generated PRs are hard to review and more likely to contain subtle issues.

## Pull Request Guidelines

### Size

Keep PRs small and focused:
- One check per PR
- One feature per PR
- Refactors separate from behavior changes

PRs over 400 lines of diff should be split unless there's a clear reason not to.

### Process

1. **Design first for non-trivial changes**: if the change adds a new category, changes scoring logic, or modifies the data model, open an issue or create a design doc in `docs/designs/` before writing code.
2. Fork the repo and create a feature branch
3. Write tests before or alongside implementation
4. Ensure CI passes (`ruff`, `mypy`, `bandit`, `pytest`)
5. Open a PR using the template

### Commit Messages

Use [conventional commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(checks): add dependency license check
fix(ci_parser): handle empty GitHub Actions files
docs: update ARCHITECTURE.md with new module
test: add property-based tests for grade computation
```

## Error Handling Policy

- Check `run()` methods must never raise exceptions. Return `fail_result()` with a descriptive message instead.
- File reads in checks should catch `OSError` and return a fail result.
- Use `yaml.safe_load` exclusively (never `yaml.load` or `yaml.unsafe_load`).
- Avoid bare `except:`. Always catch specific exception types.

## Adding a New Check

The Scorecard evaluates repositories using a suite of "Checks". Each check is responsible for a single best practice, such as verifying the presence of a license, checking for CI/CD pipelines, or ensuring security scanners are configured.

To add a new check, you'll need to write a class that inherits from `BaseCheck`, implement the required `run` method, and register your check in the appropriate module.

### 1. The `BaseCheck` Interface

All checks must subclass `ai_harness_scorecard.checks.base.BaseCheck`. When writing a check, you need to define several class-level attributes:

- `check_id`: A unique string identifier using `category.snake_case` (e.g., `"documentation.readme_presence"`).
- `name`: A short, descriptive name (e.g., `"Required Documentation"`).
- `description`: A detailed explanation of what the check verifies.
- `max_points`: The maximum score a repository can earn for this check (usually `10.0`).
- `source`: A reference to the standard or best practice this check enforces (e.g., `"OWASP Top 10"`, `"DORA Metrics"`).

### 2. The `run` Method and `RepoContext`

The core logic of your check goes into the `run(self, context: RepoContext) -> CheckResult` method.

The `RepoContext` object provides pre-scanned information about the repository, making checks fast and easy to write. Some of the most useful methods on `RepoContext` include:
- **File Search**:
  - `context.has_file("README.md", "readme.txt")`: Returns the path if any of the globs exist.
  - `context.find_files("*.py")`: Returns all matching files.
  - `context.has_dir(".github/workflows")`: Returns the directory path if it exists.
- **Content Search**:
  - `context.read_file(path)`: Returns the file's content as a string, or `None` if it cannot be read.
  - `context.search_file(path, regex_pattern)`: Returns `True` if the regex matches within the file.
- **CI Configuration**:
  - `context.ci_has_command("pytest")`: Returns `True` if any CI job runs `pytest`.
  - `context.ci_has_blocking_command("bandit")`: Returns `True` if the command runs in a job that is *not* allowed to fail.

### 3. Returning a `CheckResult`

Your `run` method **must never raise exceptions**. Instead, it should always return a `CheckResult` using one of the helper methods provided by `BaseCheck`:

- `self.pass_result(evidence="Found README.md")`: Used when the practice is perfectly followed.
- `self.fail_result(evidence="No lockfile found", remediation="Run pip freeze > requirements.txt")`: Used when the practice is not followed at all.
- `self.partial_result(score=5.0, evidence="Found some docs, but missing API reference", remediation="...")`: Used when the practice is partially followed.

> [!NOTE]
> File reads in checks should gracefully handle missing or binary files. The `context.read_file()` method automatically returns `None` if a file is not readable, which you should handle by returning a `fail_result` or `partial_result`.

### 4. Code Example: A Dummy Check

Here is a simple example of a check that ensures a project has a `README` file:

```python
from ai_harness_scorecard.checks.base import BaseCheck
from ai_harness_scorecard.models import CheckResult
from ai_harness_scorecard.repo_context import RepoContext

class ReadmeCheck(BaseCheck):
    check_id = "documentation.readme_presence"
    name = "Project README"
    description = "Checks that the repository has a comprehensive README file."
    max_points = 10.0
    source = "General Best Practices"

    def run(self, context: RepoContext) -> CheckResult:
        # Check if any readme-like file exists
        readme_path = context.has_file("README.md", "README.rst", "readme.txt")
        
        if not readme_path:
            return self.fail_result(
                evidence="No README file found.",
                remediation="Create a README.md file at the root of the repository describing the project."
            )
            
        return self.pass_result(
            evidence=f"Found README at {readme_path}."
        )
```

### 5. Registering the Check

Checks are grouped into categories like `documentation`, `testing`, `security`, etc., which are defined in `src/ai_harness_scorecard/checks/`. 

To make the scanner aware of your new check, you must instantiate it and add it to the exported list of checks at the bottom of the relevant category module:

```python
# src/ai_harness_scorecard/checks/documentation.py

# ... existing checks ...

# Instantiate your check
YOUR_NEW_CHECK = ReadmeCheck()

# Add it to the module's exported list
DOCUMENTATION_CHECKS = [
    EXISTING_CHECK,
    YOUR_NEW_CHECK,
]
```

The `scanner.py` orchestrator automatically imports all these lists, so no further registration is needed!

---

For architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md). For agent naming conventions, see [AGENTS.md](AGENTS.md).
