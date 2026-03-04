# Resources & Knowledge Base

References, research, and articles that inform the scorecard's checks and scoring philosophy.

Each check in the scorecard cites a `source` field linking back to one of these references. This folder collects the primary sources so contributors can understand the reasoning behind each check.

## Core References

### DORA 2025 Report

- **Type**: Industry research report
- **URL**: https://dora.dev/research/2025/
- **Relevance**: Foundational data on CI/CD practices, stability metrics, working in small batches, and the impact of AI on software delivery. Cited by 9 checks across 4 categories.
- **Key findings used**:
  - Teams with CI pipelines and blocking tests have higher deployment frequency
  - Working in small batches (small PRs) correlates with lower change failure rate
  - AI-accessible documentation improves onboarding and reduces context-switching
  - Scheduled CI catches drift that event-driven CI misses
  - Clear organizational stance on AI use correlates with responsible adoption

### OpenAI Harness Engineering (2026)

- **Type**: Engineering blog post
- **URL**: https://openai.com/index/harness-engineering/
- **Relevance**: The primary inspiration for this tool. Describes how OpenAI structures engineering to make AI-assisted development safe. Cited by 8 checks.
- **Key concepts used**:
  - Mechanical constraints (linters, formatters, type checks) as non-negotiable CI gates
  - Separation of authoring and reviewing agents/humans
  - Garbage collection agents that detect and fix quality drift
  - Curated knowledge bases (ARCHITECTURE.md, AGENTS.md) for AI context
  - Agent instructions as first-class project artifacts

### SlopCodeBench

- **Type**: Research benchmark
- **URL**: https://huggingface.co/blog/slopcodebench
- **Relevance**: Benchmark measuring subtle correctness issues in AI-generated code. Code that "appears correct but is unreliable." Cited by 2 checks.
- **Key concepts used**:
  - AI-generated code often passes superficial review but fails under edge cases
  - Type safety prevents a class of subtle errors specific to AI-generated code
  - Mutation testing catches tests that pass without verifying behavior

### matklad ARCHITECTURE.md Guide

- **Type**: Blog post / convention proposal
- **URL**: https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html
- **Relevance**: The original proposal for ARCHITECTURE.md files. Argues that high-level architecture docs are more valuable than inline comments. Cited by 2 checks.
- **Key concepts used**:
  - Every project should have an ARCHITECTURE.md describing the high-level structure
  - Constraints are best documented as absences ("we don't do X because...")
  - Module boundary documentation reduces onboarding time

## Blog Posts & Articles

### "How to Kill the Code Review" - Latent Space (Mar 2026)

- **Type**: Industry opinion / analysis
- **URL**: https://www.latent.space/p/reviews-dead
- **Relevance**: Argues that as AI-generated code scales, deterministic guardrails (exactly what this scorecard measures) become more important than manual review. Proposes a 5-layer trust model.
- **Key concepts**:
  - Teams with high AI adoption merge 98% more PRs but review time increases 91%
  - Swiss cheese model: stack imperfect filters until holes don't align
  - Deterministic guardrails (tests, types, linters) replace opinion-based review
  - Human value moves upstream to specs and acceptance criteria
  - Permission systems and adversarial verification as architectural decisions

### The 80% Problem in AI-Generated Code

- **Relevance**: The observation that AI gets ~80% of code right but the remaining 20% contains subtle bugs, security issues, and missing edge cases. Cited by 3 checks (unsafe code policy, fuzz testing, security infrastructure).
- **Key concepts used**:
  - AI-generated code needs stronger safety nets, not weaker ones
  - Security infrastructure (audit tools, SAST) catches what AI misses
  - Fuzz testing finds edge cases AI doesn't consider

### Cognitive Offloading Guardrails

- **Relevance**: When developers rely on AI, they offload cognitive work and may miss errors they'd normally catch. Guardrails compensate for reduced human attention. Cited by 1 check.
- **Key concepts used**:
  - Multiple approach culture (ADRs, RFCs) forces evaluation of alternatives
  - Error handling policies prevent AI from generating optimistic-path-only code

## Books & Foundational Ideas

### Kent Beck - Test-Driven Development

- **Relevance**: "The test defines what correct means." Tests are not just verification; they're specification. Cited by 1 check.
- **Applied as**: `TestSuiteExistsCheck` awards points for tests that are both present and executed in CI.

## How Sources Map to Checks

| Source | Checks citing it |
|--------|-----------------|
| DORA 2025 Report | `ci_pipeline_exists`, `adr_presence`, `api_contracts`, `feature_matrix_testing`, `coverage_measurement`, `tests_blocking_ci`, `scheduled_ci`, `mr_template`, `ai_usage_norms`, `small_batch_enforcement` |
| OpenAI Harness Engineering | `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `contract_tests`, `code_review_required`, `stale_doc_detection`, `automated_review`, `doc_sync_check` |
| SlopCodeBench | `type_safety`, `mutation_testing` |
| matklad ARCHITECTURE.md | `architecture_doc`, `module_boundary_docs` |
| Blog: 80% problem | `unsafe_code_policy`, `fuzz_testing`, `security_critical_marking` |
| Blog: cognitive offloading | `multiple_approach_culture` |
| Blog: AI agents and testing | `error_handling_policy` |
| Blog: security infrastructure | `dependency_auditing` |
| Blog: edge cases in AI code | `property_based_testing` |
| Kent Beck | `test_suite_exists` |

## Contributing

Found a relevant paper, blog post, or report? Add it here following the format above. Good candidates:
- Research on AI code generation quality and failure modes
- Industry reports on CI/CD and DevOps practices
- Engineering blog posts about AI-assisted development guardrails
- Benchmarks measuring AI-generated code reliability
