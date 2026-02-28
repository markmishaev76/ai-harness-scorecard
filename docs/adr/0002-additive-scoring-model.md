# ADR 0002: Additive Scoring Model

## Status

Accepted

## Context

Two scoring approaches were considered:

1. **Subtractive**: start at 100, deduct for missing practices
2. **Additive**: start at 0, add points for detected practices

## Decision

Use additive scoring. Each check contributes points when it passes. The total is normalized to a percentage per category, then weighted across categories.

## Rationale

- A Python-only repo should not be penalized for missing `cargo deny` (a Rust tool)
- Additive scoring naturally handles language-specific checks: inapplicable checks simply don't add points, rather than unfairly deducting
- Easier to extend: adding a new check doesn't change existing scores

## Consequences

- Maximum achievable score depends on which checks apply to the repo's languages
- A repo could theoretically score 100% while still having room to improve in areas not yet covered by checks
