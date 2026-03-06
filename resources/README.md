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

### DORA 2025 Research Trilogy

- **Type**: Industry research (3-part series)
- **URLs**:
  - Impact of Generative AI in Software Development (March 2025)
  - State of AI-assisted Software Development (September 2025)
  - DORA AI Capabilities Model (December 2025)
- **Relevance**: Extends the main DORA report. The trilogy covers AI as an amplifier (magnifies existing strengths and weaknesses), trust gaps (only 3% of devs have "high trust" in AI output), and the finding that AI boosts throughput at the expense of stability without robust automated testing and fast feedback loops.

## Research Papers

### "AI Code in the Wild" — Yan et al. (Dec 2025)

- **Type**: Empirical study
- **URL**: https://arxiv.org/abs/2512.18567
- **Relevance**: First large-scale study of AI-generated code security in real-world projects. Analyzed top 1,000 GitHub repos and 7,000+ CVE-linked commits (2022–2025). Directly supports our AI safeguards and dependency auditing checks.
- **Key findings**:
  - Some CWE families are overrepresented in AI-tagged code
  - AI-induced vulnerabilities propagate through shared models, creating near-identical insecure templates across unrelated projects
  - AI concentrates in glue code, tests, and docs while core logic stays human-written
  - When code review is shallow, AI-introduced defects persist longer and spread to more files

### "Is It Safe?" — Vibe Coding Security Benchmark (ICLR 2026)

- **Type**: Research benchmark
- **URL**: https://openreview.net/forum?id=rs6rRCEixQ
- **Relevance**: Measured security of AI agent-generated code on real-world tasks. Directly motivates our `unsafe_code_policy` and `security_critical_marking` checks.
- **Key findings**:
  - 47.5% of Claude 4 Sonnet tasks were functionally correct, but only 8.25% were secure
  - Functional correctness and security are nearly independent properties in AI-generated code

### "An Empirical Evaluation of Property-Based Testing in Python" (OOPSLA 2025)

- **Type**: Academic study
- **URL**: https://cseweb.ucsd.edu/~mcoblenz/assets/pdf/OOPSLA_2025_PBT.pdf
- **Relevance**: Quantifies PBT effectiveness. Each property-based test finds ~50x as many mutations as the average unit test. Supports our `property_based_testing` check.
- **Key findings**:
  - 76% of mutations caught within the first 20 randomly generated inputs
  - Exception-checking, collection-inclusion, and type-verification tests are 19x more effective than other PBT test kinds

### "Property-Based Testing in Practice" — ICSE 2024

- **Type**: Academic study (practitioner interviews)
- **URL**: https://dl.acm.org/doi/10.1145/3597503.3639581
- **Relevance**: Qualitative research with experienced PBT practitioners (e.g., Jane Street). Identifies practical adoption barriers: writing properties and generators is hard, and evaluating PBT effectiveness is difficult.

### "A Comprehensive Study on LLMs for Mutation Testing" (2024)

- **Type**: Academic study
- **URL**: https://arxiv.org/html/2406.09843v4
- **Relevance**: LLM-generated mutants achieve 87.98% fault detection vs. 41.64% for rule-based methods. Supports our `mutation_testing` check and shows mutation testing is evolving alongside AI.

### "Architecture Decision Records in Practice" — ECSA 2024

- **Type**: Action research study
- **URL**: https://link.springer.com/chapter/10.1007/978-3-031-70797-1_22
- **Relevance**: Empirical evidence that ADRs improve documentation culture and knowledge transfer. Storage location (code-adjacent vs. central) strongly affects adoption. Supports our `adr_presence` check.

### "AI-Induced Supply-Chain Compromise: Slopsquatting" (2025)

- **Type**: Systematic review
- **URL**: https://www.researchsquare.com/article/rs-8007192/latest
- **Relevance**: 19.7% of LLM-recommended packages don't exist. Over 205,000 hallucinated package names identified across 576,000 code samples. Directly motivates our `dependency_auditing` check.
- **Key findings**:
  - Open-source models hallucinate package names 21.7% of the time vs. 5.2% for proprietary models
  - 43% of hallucinated names repeat across similar prompts, making them predictable attack targets
  - 38% inspired by real packages, 13% typos, 51% completely fabricated

### "Using ADRs in Open Source Projects" — IEEE TSE 2023

- **Type**: Mining software repositories study
- **URL**: https://ieeexplore.ieee.org/document/10155430/
- **Relevance**: Large-scale study of ADR adoption on GitHub. Markdown-based ADRs integrate well into developer toolchains. Supports our `adr_presence` and `architecture_doc` checks.

### GitHub Copilot Productivity Research — Microsoft Research (2024)

- **Type**: Field experiment
- **URL**: https://www.microsoft.com/en-us/research/publication/the-impact-of-ai-on-developer-productivity-evidence-from-github-copilot/
- **Relevance**: Nearly 2,000 developers at Microsoft and Accenture completed 7.5–21.8% more PRs per week with Copilot. Tasks completed up to 55% faster. Code passed 53.2% more unit tests. Context for why guardrails matter: more code shipped faster means more surface area for defects.

### "Quality Gatekeepers" — Code Review Bots Study (2022)

- **Type**: Empirical study
- **URL**: https://link.springer.com/article/10.1007/s10664-022-10130-9
- **Relevance**: Bot adoption increased merged PRs but decreased developer-to-developer communication. Automated code review tools reduced defect density by 15–30%. Supports our `automated_review` and `code_review_required` checks.

### CodePulse 2025 Engineering Benchmarks

- **Type**: Industry analysis
- **URL**: https://codepulsehq.com/research/code-review-study-2025
- **Relevance**: Analysis of 802,979 merged PRs. Self-merge rate: 71%. 90% of large PRs (1000+ lines) ship without review. Directly motivates our `code_review_required` and `small_batch_enforcement` checks.

### "Bugs That Survive Continuous Fuzzing" — GitHub Security (2025)

- **Type**: Engineering analysis
- **URL**: https://github.blog/security/vulnerability-research/bugs-that-survive-the-heat-of-continuous-fuzzing/
- **Relevance**: Even projects fuzzed for 7+ years harbor serious vulnerabilities. GStreamer: 7 years of fuzzing, only 19% code coverage. Fuzzing requires active human oversight. Supports our `fuzz_testing` check and shows that presence alone is insufficient.

## Blog Posts & Articles

### "How to Kill the Code Review" — Latent Space (Mar 2026)

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

### Simon Willison — "Automated Tests Are Essential for LLM Code" (May 2025)

- **Type**: Blog post
- **URL**: https://simonwillison.net/2025/May/28/automated-tests
- **Relevance**: Willison attributes his success with LLMs to having automated tests on nearly all his code. Tests "massively derisk" LLM use by enabling verification and iterative refactoring. Supports our `test_suite_exists` and `tests_blocking_ci` checks.

### Simon Willison — "Using LLMs for Code" (Mar 2025)

- **Type**: Blog post
- **URL**: https://simonwillison.net/2025/Mar/11/using-llms-for-code
- **Relevance**: Practical guide to LLM-assisted development. Treats LLMs as "an over-confident pair programming assistant" that amplifies existing expertise. Core message: "You have to test what it writes."

### Simon Willison — "The Five Levels" (Jan 2026)

- **Type**: Blog post
- **URL**: https://simonwillison.net/2026/Jan/28/the-five-levels/
- **Relevance**: Taxonomy of AI coding autonomy from "spicy autocomplete" to "dark factory." Each level requires progressively stronger guardrails. Directly maps to the scorecard's philosophy of mechanical constraints.

### Simon Willison — "Tips for Getting Coding Agents to Write Good Tests" (Jan 2026)

- **Type**: Blog post
- **URL**: https://simonwillison.net/2026/Jan/26/tests/
- **Relevance**: Practical advice for having AI agents produce useful tests. Recommends agents imitate existing test patterns in the codebase and use project-specific fixtures.

### Google Engineering Practices Documentation

- **Type**: Engineering guidelines
- **URL**: https://google.github.io/eng-practices/
- **Relevance**: Google's code review standards. Reviewers should approve once a change improves overall code health, even if imperfect. Covers review comments, small CLs, and CL descriptions. Supports our `code_review_required` and `small_batch_enforcement` checks.

### "AI Slopageddon" — InfoQ (Feb 2026)

- **Type**: Industry reporting
- **URL**: https://www.infoq.com/news/2026/02/ai-floods-close-projects/
- **Relevance**: Major open-source projects (cURL, Ghostty, tldraw) closing doors to AI-generated contributions due to quality problems. Documents the real-world cost of AI code without guardrails.

### Anthropic — Claude Code Best Practices

- **Type**: Engineering documentation
- **URL**: https://docs.anthropic.com/en/docs/claude-code/best-practices
- **Relevance**: Anthropic's own guidance says verification (tests, linters, visual comparisons) is the "highest-leverage practice" for reliable AI coding results. Aligns directly with the scorecard's approach.

### Anthropic — Framework for Safe and Trustworthy Agents (Aug 2025)

- **Type**: Research framework
- **URL**: https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents
- **Relevance**: Emphasizes keeping humans in control, transparency in agent behavior, and customizable oversight. Supports our `agent_instructions` and `ai_usage_norms` checks.

### Microsoft Nudge Study — Accelerating Code Reviews (2024)

- **Type**: Industry research
- **URL**: https://reviewnudgebot.com/blog/how-to-accelerate-code-reviews-with-nudges-insights-from-microsofts-study/
- **Relevance**: Analysis of 22,875 PRs. Automated nudges achieved 60% reduction in PR completion times across 8,000+ repos. Supports our `code_review_required` and `automated_review` checks.

### Geoffrey Huntley — "Ralph Wiggum as a Software Engineer" (Jul 2025)

- **Type**: Blog post / technique description
- **URL**: https://ghuntley.com/ralph/
- **Relevance**: Documents the "Ralph" technique for autonomous AI coding — a bash loop (`while :; do cat PROMPT.md | claude-code ; done`) that runs an AI agent continuously on a single repo. Used to build a production-grade programming language from scratch. Key insights for our scorecard:
  - **Back pressure is everything**: Type systems, static analyzers, security scanners, and tests act as gates that reject invalid code generation each loop. The faster the wheel turns, the more important mechanical constraints become.
  - **Specs drive everything**: Specification files (one per feature) are fed to the agent every loop, functioning as the deterministic contract. This maps directly to our `agent_instructions` and design-before-code checks.
  - **AGENT.md as living context**: The agent updates its own instructions file with learned build commands and patterns. Supports our `agent_instructions` check rationale.
  - **Tests capture reasoning**: When the agent writes tests, it documents *why* the test exists — leaving notes for future iterations that won't have the original reasoning in context.
  - **Greenfield-only caveat**: "There's no way in heck would I use Ralph in an existing code base." This validates that existing repos need stronger safeguards (what we measure) for AI to work safely.
  - Real-world outcome: a $50K USD contract delivered for $297 in AI compute costs.

### Kief Morris — "Humans and Agents in Software Engineering Loops" (Mar 2026)

- **Type**: Blog post (Martin Fowler / Thoughtworks)
- **URL**: https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html
- **Relevance**: Defines three positions for humans in AI-assisted development and introduces the "agentic flywheel" concept. Directly validates the scorecard's design philosophy and suggests new check directions.
- **Key concepts**:
  - **On the loop > in the loop**: Instead of reviewing every line agents produce, build and maintain the harness that controls them. When output is bad, fix the system, not the artifact.
  - **Internal quality still matters**: LLMs work faster and spiral less in clean codebases. Mechanical constraints (what we measure) reduce cost and time even when agents write all the code.
  - **Harness = specs + quality checks + workflow guidance**: The exact combination our 5 categories measure. The article gives this collection a name and a framework.
  - **Agentic flywheel**: Agents evaluating loop performance and recommending harness improvements. The harness becomes self-improving when fed test results, pipeline metrics, and production data.
  - **Shift left for agents**: Agents produce better code when they can gauge quality themselves (tests, lints, type checks) rather than relying on humans to check after.
  - **Multiple how-loop levels**: Outer loops (feature), middle loops (stories), inner loops (code). Each needs its own validation. Richer feedback loops produce better outcomes.

### Ars Contexta — Memory Infrastructure for Claude Code

- **Type**: Tool / Claude Code plugin
- **URL**: https://github.com/agenticnotetaking/arscontexta
- **Relevance**: Claude Code plugin (2,000+ stars) that generates persistent knowledge systems from conversation. Creates markdown-based vaults with wiki-linked notes forming a traversable knowledge graph. Uses a three-space architecture: `self/` (agent persistent mind), `notes/` (knowledge graph), `ops/` (operations). The derivation-based approach (not templating) generates a custom cognitive architecture from 2-4 conversation turns. Relevant to our `agent_instructions` and `architecture_doc` checks — demonstrates that AI agents need structured, persistent context to maintain quality across sessions.

## Videos & Talks

### Charity Majors — "Observability & Testing in Production" (2024)

- **Type**: Conference talk / podcast
- **URLs**:
  - Talk: https://www.youtube.com/watch?v=97YRxrKNLP0
  - GOTO 2024: https://www.youtube.com/watch?v=1PJM8p-RMsY
- **Relevance**: Argues that staging environments cannot replicate real-world conditions. Teams need guardrails (feature flags, instrumentation, observability) in production. Relevant to our coverage and CI checks.

### Kent Beck — "Tidy First?" Talk (2023)

- **Type**: Conference talk
- **URL**: https://www.youtube.com/watch?v=XmsyvStDuqI
- **Relevance**: Beck presents the case for small, safe refactorings ("tidyings") that improve readability without changing behavior. Directly relates to small batch enforcement and the value of incremental improvement over big-bang rewrites.

## Frameworks & Specifications

### SLSA — Supply-chain Levels for Software Artifacts

- **Type**: Security framework (OpenSSF)
- **URL**: https://slsa.dev/
- **Relevance**: Defines 4 levels of build security (L0–L3) covering provenance, signed builds, and hardened platforms. Supports our `ci_pipeline_exists` and `dependency_auditing` checks by providing a maturity model for build security.

### CycloneDX / SPDX — Software Bill of Materials Standards

- **Type**: Specifications (OWASP / Linux Foundation)
- **URLs**:
  - CycloneDX: https://cyclonedx.org/
  - SPDX: https://spdx.dev/
- **Relevance**: Machine-readable inventories of software components and dependencies. Enable automated vulnerability scanning and license compliance. Context for our `dependency_auditing` check.

### Conventional Commits Specification

- **Type**: Specification
- **URL**: https://www.conventionalcommits.org/
- **Relevance**: Structured commit messages (`feat:`, `fix:`, `BREAKING CHANGE:`) enable automated changelogs, semantic versioning, and release management. Supports our `conventional_commits` check.

## Books & Foundational Ideas

### Kent Beck — "Test-Driven Development" (2002)

- **Relevance**: "The test defines what correct means." Tests are not just verification; they're specification. Cited by 1 check.
- **Applied as**: `TestSuiteExistsCheck` awards points for tests that are both present and executed in CI.

### Kent Beck — "Tidy First?" (2023)

- **Type**: Book (O'Reilly)
- **Relevance**: Small, safe refactorings that improve readability without changing behavior. Covers coupling, cohesion, and the economics of design decisions. Supports our philosophy that incremental quality improvements (what the scorecard encourages) compound over time.

### Nicole Forsgren, Jez Humble, Gene Kim — "Accelerate" (2018)

- **Type**: Book (IT Revolution Press), Shingo Award winner
- **Relevance**: Four years of statistical research that produced the DORA metrics (deployment frequency, lead time, change failure rate, MTTR). The scientific foundation behind multiple scorecard categories. Every CI-related check traces back to findings in this book.

### Dave Farley — "Modern Software Engineering" (2021)

- **Type**: Book (Addison-Wesley)
- **Relevance**: Unified, scientific approach to software development. Distills the discipline into learning/exploration and managing complexity. Advocates empiricism, fast feedback, and incremental progress. Supports the scorecard's overall design philosophy.

### Dave Farley & Jez Humble — "Continuous Delivery" (2010)

- **Type**: Book (Addison-Wesley), Jolt Award winner
- **Relevance**: The foundational text on CI/CD pipelines, deployment automation, and build reliability. Directly supports our `ci_pipeline_exists`, `tests_blocking_ci`, and `scheduled_ci` checks.

## How Sources Map to Checks

| Source | Checks citing it |
|--------|-----------------|
| DORA 2025 Report | `ci_pipeline_exists`, `adr_presence`, `api_contracts`, `feature_matrix_testing`, `coverage_measurement`, `tests_blocking_ci`, `scheduled_ci`, `mr_template`, `ai_usage_norms`, `small_batch_enforcement` |
| OpenAI Harness Engineering | `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `contract_tests`, `code_review_required`, `stale_doc_detection`, `automated_review`, `doc_sync_check` |
| SlopCodeBench | `type_safety`, `mutation_testing` |
| matklad ARCHITECTURE.md | `architecture_doc`, `module_boundary_docs` |
| Accelerate (Forsgren et al.) | `ci_pipeline_exists`, `tests_blocking_ci`, `scheduled_ci`, `coverage_measurement` |
| Continuous Delivery (Farley & Humble) | `ci_pipeline_exists`, `tests_blocking_ci`, `scheduled_ci` |
| SLSA Framework | `ci_pipeline_exists`, `dependency_auditing` |
| CycloneDX / SPDX | `dependency_auditing` |
| Conventional Commits spec | `conventional_commits` |
| Paper: AI Code in the Wild | `dependency_auditing`, `code_review_required`, `unsafe_code_policy` |
| Paper: Vibe Coding Security (ICLR 2026) | `unsafe_code_policy`, `security_critical_marking` |
| Paper: PBT in Python (OOPSLA 2025) | `property_based_testing` |
| Paper: LLMs for Mutation Testing | `mutation_testing` |
| Paper: Slopsquatting | `dependency_auditing` |
| Paper: ADRs in Practice | `adr_presence` |
| Paper: Copilot Productivity | `test_suite_exists`, `tests_blocking_ci` |
| Paper: Quality Gatekeepers | `automated_review`, `code_review_required` |
| CodePulse 2025 Benchmarks | `code_review_required`, `small_batch_enforcement` |
| GitHub: Fuzzing Survivors | `fuzz_testing` |
| Simon Willison (testing + LLMs) | `test_suite_exists`, `tests_blocking_ci` |
| Simon Willison (five levels) | `agent_instructions`, `ai_usage_norms` |
| Google Engineering Practices | `code_review_required`, `small_batch_enforcement` |
| Anthropic (Claude best practices) | `agent_instructions`, `ai_usage_norms` |
| Anthropic (safe agents framework) | `agent_instructions`, `ai_usage_norms` |
| Microsoft Nudge Study | `code_review_required`, `automated_review` |
| Blog: 80% problem | `unsafe_code_policy`, `fuzz_testing`, `security_critical_marking` |
| Blog: cognitive offloading | `multiple_approach_culture` |
| Blog: AI agents and testing | `error_handling_policy` |
| Blog: security infrastructure | `dependency_auditing` |
| Blog: edge cases in AI code | `property_based_testing` |
| Blog: AI Slopageddon (InfoQ) | `ai_usage_norms`, `code_review_required` |
| Kent Beck (TDD) | `test_suite_exists` |
| Kent Beck (Tidy First?) | `small_batch_enforcement` |
| Dave Farley (Modern SE) | `ci_pipeline_exists`, `coverage_measurement` |
| Huntley: Ralph Wiggum technique | `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `type_safety`, `test_suite_exists`, `tests_blocking_ci` |
| Ars Contexta (memory plugin) | `agent_instructions`, `architecture_doc` |
| Morris: Humans & Agents (Fowler) | `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `type_safety`, `test_suite_exists`, `tests_blocking_ci`, `coverage_measurement`, `automated_review` |

## Contributing

Found a relevant paper, blog post, or report? Add it here following the format above. Good candidates:
- Research on AI code generation quality and failure modes
- Industry reports on CI/CD and DevOps practices
- Engineering blog posts about AI-assisted development guardrails
- Benchmarks measuring AI-generated code reliability
- Security research on supply chain attacks and AI-specific vulnerabilities
- Conference talks and videos on testing, observability, and software quality
