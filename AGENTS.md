# AI Agent Instructions for ai-harness-scorecard

## Project Context

A Python CLI tool that grades Git repositories on engineering safeguards for safe AI-assisted development. Scans files and CI configs to produce a scored report across 5 categories (31 checks).

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for module layout and dependency rules.

Key constraint: checks must be deterministic. No LLM calls, no network requests, no randomness. Two runs on the same repo must produce the same score.

## Code Style

- Python 3.12+, type hints on all function signatures
- Formatting: `ruff format` (100 char line length)
- Linting: `ruff check` with rules E, F, W, I, N, UP, B, A, SIM, TCH
- Type checking: `mypy --strict`
- Use `from __future__ import annotations` in every module

## Adding a Check

1. Create a class in `src/ai_harness_scorecard/checks/<category>.py` inheriting from `BaseCheck`
2. Set `check_id`, `name`, `description`, `max_points`, and `source`
3. Implement `run(context: RepoContext) -> CheckResult`
4. Use `pass_result()`, `fail_result()`, or `partial_result()` helpers
5. Add the instance to the module's `*_CHECKS` list
6. The scanner picks it up automatically

## Error Handling

- Use explicit return types. Prefer `CheckResult` over raising exceptions in checks.
- Never use bare `except:`. Always catch specific exceptions.
- File I/O in checks should handle missing files gracefully (the repo under scan may lack any file).

## Testing

- Every check needs at least one test for pass and one for fail
- Use `tmp_path` fixtures to create minimal repo structures
- Property-based tests use `hypothesis` for fuzz-like input generation
- Run: `pytest --cov=ai_harness_scorecard`

## Naming

- Check classes: `<Thing>Check` (e.g., `LinterEnforcementCheck`)
- Check IDs: `category.snake_case` (e.g., `constraints.linter_enforcement`)
- Test files: `test_<module>.py`
- Test functions: `test_<check_id>_pass`, `test_<check_id>_fail`
