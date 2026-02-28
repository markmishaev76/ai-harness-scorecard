# AI Harness Scorecard

Grade any Git repository on its engineering safeguards for safe AI-assisted development.

Not "is this repo ready for agents?" but rather: **"will the code agents produce here be reliable?"**

Based on research from [DORA 2025](https://dora.dev/research/2025/dora-report), [OpenAI's Harness Engineering](https://openai.com/index/harness-engineering), [SlopCodeBench](https://snorkelai.com/slopcodebench), and [Kent Beck's testing principles](https://newsletter.pragmaticengineer.com/p/tdd-ai-agents-and-coding-with-kent). See the full analysis: [The Engineering Leader's Uncomfortable Truth About AI-Assisted Development](https://mark-mishaev.medium.com/the-engineering-leaders-uncomfortable-truth-about-ai-assisted-development-0e9a7c4b3eda).

## Quick Start

```bash
# Install
pip install ai-harness-scorecard

# Assess current repo
ai-harness-scorecard assess .

# Assess another repo
ai-harness-scorecard assess /path/to/repo

# Markdown report
ai-harness-scorecard assess . --format markdown -o report.md

# JSON for CI integration
ai-harness-scorecard assess . --format json
```

## What It Checks

Five categories, 31 checks, each grounded in published research:

### 1. Architectural Documentation (20%)
Architecture docs, agent instructions, ADRs, module boundary constraints, API documentation.

### 2. Mechanical Constraints (25%)
CI pipeline, linter/formatter enforcement, type safety, dependency auditing, conventional commits, unsafe code policies.

### 3. Testing & Stability (25%)
Test suite in CI, feature matrix testing, code coverage, mutation testing, property-based testing, fuzz testing, contract tests, blocking test jobs.

### 4. Review & Drift Prevention (15%)
Code review enforcement, scheduled CI, stale doc detection, PR/MR templates, automated review bots, doc sync checks.

### 5. AI-Specific Safeguards (15%)
AI usage norms, small batch enforcement, design-before-code culture, error handling policies, security-critical path marking.

## Grading

| Grade | Score | Meaning |
|-------|-------|---------|
| **A** | 85-100 | Strong harness. AI-generated code has robust mechanical safeguards |
| **B** | 70-84 | Good foundation. Some gaps in enforcement or feedback loops |
| **C** | 55-69 | Basic practices present but insufficient for safe AI scaling |
| **D** | 40-54 | Significant gaps. AI code likely accumulating undetected debt |
| **F** | 0-39 | No meaningful harness. AI output is essentially unaudited |

## Example Output

```
Grade: B  (74.2/100)
Good foundation. Some gaps in enforcement or feedback loops.

         Category Scores
┌──────────────────────────┬────────┬───────┬────────┐
│ Category                 │ Weight │ Score │ Checks │
├──────────────────────────┼────────┼───────┼────────┤
│ Architectural Docs       │    20% │   60% │    3/5 │
│ Mechanical Constraints   │    25% │   91% │    6/7 │
│ Testing & Stability      │    25% │   72% │    5/8 │
│ Review & Drift           │    15% │   60% │    3/6 │
│ AI-Specific Safeguards   │    15% │   67% │    3/5 │
└──────────────────────────┴────────┴───────┴────────┘
```

## Platform Support

Works on any cloned Git repository (GitHub, GitLab, Bitbucket, self-hosted). Most checks are file-based and platform-independent.

For platform-specific checks (branch protection, required reviewers), future versions will support:

```bash
# GitHub
ai-harness-scorecard assess github:owner/repo

# GitLab
ai-harness-scorecard assess gitlab:group/project
```

## Design Principles

1. **Deterministic.** No LLM dependency. Two runs on the same repo produce the same score.
2. **Language-aware.** Checks adapt to Rust, Python, TypeScript, Go, Java, etc.
3. **Additive scoring.** Each check contributes points. Missing an inapplicable check doesn't penalize.
4. **Research-grounded.** Every check maps back to a specific study or published best practice.

## Development

```bash
# Clone
git clone https://github.com/markmishaev/ai-harness-scorecard
cd ai-harness-scorecard

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/
```

## License

MIT
