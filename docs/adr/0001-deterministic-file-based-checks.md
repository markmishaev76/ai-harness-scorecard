# ADR 0001: Deterministic File-Based Checks

## Status

Accepted

## Context

We need to decide how checks assess repositories. Options considered:

1. **LLM-based analysis**: use an AI model to read code and judge quality
2. **API-based checks**: query GitHub/GitLab APIs for branch protection, CI status, etc.
3. **File-based pattern matching**: scan local files for presence of configs, patterns, and CI commands

## Decision

All checks are deterministic file-based pattern matching. No LLM dependency, no mandatory API access.

## Rationale

- **Reproducibility**: two runs on the same repo produce the same score. LLM outputs vary.
- **Speed**: file scanning completes in under a second. API calls add latency and rate limits.
- **Offline**: works on any cloned repo without tokens or network access.
- **CI-friendly**: runs in any CI environment without special permissions.

API-based checks (branch protection, required reviewers) are planned as optional enhancements when tokens are provided, but the core score is always file-based.

## Consequences

- Some checks cannot verify enforcement (e.g., we can detect a CODEOWNERS file but not whether GitHub actually enforces it)
- Scores may slightly undercount repos that enforce policies through platform settings rather than config files
