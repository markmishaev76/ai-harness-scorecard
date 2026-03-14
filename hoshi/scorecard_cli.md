# Scorecard CLI Behavior

The ai-harness-scorecard CLI should assess a repository and produce
a graded report. Running it on the current repo (which has strong
safeguards) should produce a passing grade.

1. Run the scorecard assess command on the current directory.
2. It should exit successfully.
3. The output should contain a grade (A, B, C, D, or F).
4. The output should mention all 5 check categories.
5. Running with --format json should produce valid JSON output.

<!-- hoshi:spec -->

## Scenario: Assess produces a grade

- When we run command `uv run ai-harness-scorecard assess . --format markdown`
- Then exit code is `0`
- Then stdout contains `Grade`
- Then stdout contains `Architectural Documentation`
- Then stdout contains `Mechanical Constraints`
- Then stdout contains `Testing & Stability`
- Then stdout contains `Review & Drift Prevention`
- Then stdout contains `AI-Specific Safeguards`

## Scenario: Assess produces valid JSON

- When we run command `uv run ai-harness-scorecard assess . --format json`
- Then exit code is `0`
- Then stdout contains `overall_score`
- Then stdout contains `categories`
