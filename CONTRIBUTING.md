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

See [ARCHITECTURE.md](ARCHITECTURE.md) for the module layout and [AGENTS.md](AGENTS.md) for naming conventions.
