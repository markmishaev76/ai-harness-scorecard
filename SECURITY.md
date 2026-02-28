# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly or use GitHub's private vulnerability reporting feature
3. Include a description of the vulnerability, steps to reproduce, and potential impact
4. You should receive a response within 72 hours

## Security Considerations

This tool reads and analyzes repository contents. It does not:
- Execute any code from scanned repositories
- Make network requests during assessment (all checks are local file analysis)
- Store or transmit repository contents

### Security-Critical Paths

- `src/ai_harness_scorecard/repo_context.py` - reads files from the scanned repo. Path traversal must be prevented.
- `src/ai_harness_scorecard/ci_parser.py` - parses YAML files. Uses `yaml.safe_load` only (never `yaml.load`).
- `action.yml` - runs in GitHub Actions with `contents: write` permission. The commit step only touches `scorecard-badge.json`.

## Static Analysis

This project runs `bandit` (Python security linter) in CI on every push.
