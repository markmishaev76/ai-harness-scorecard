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

## Practitioner Guides

### Simon Willison — "Agentic Engineering Patterns" (Feb–Mar 2026)

- **Type**: Evolving guide (11 chapters)
- **URL**: https://simonwillison.net/guides/agentic-engineering-patterns/
- **Relevance**: The most practical and grounded guide to working with coding agents, written from daily hands-on experience by the creator of Datasette. Directly validates and extends the scorecard's philosophy.
- **Key concepts**:
  - **"Shipping worse code is a choice"**: Code production cost is near-zero, so use the savings to pay down technical debt, not accumulate it. Refactoring tasks (splitting large files, renaming concepts, fixing API duplication) are ideal for background agents.
  - **#1 anti-pattern**: Filing PRs with unreviewed agent-generated code. Agents write convincing PR descriptions — review those too. Include evidence of manual testing.
  - **Red/green TDD**: Write the failing test, let the agent make it pass. Mechanical success criterion. Independently confirms the same pattern from Kent Beck and the consolidated guide.
  - **Agentic manual testing**: Never assume LLM-generated code works until it has been executed. Agents should test their own output.
  - **Compound engineering loop**: Retrospective after each AI project, document what worked, feed it forward. Maps to the DECISIONS.md and LESSONS.md patterns.
  - **"Code is cheap now"**: Things that used to be "not worth the effort" (prototyping alternatives, fixing naming inconsistencies) are now trivial. Use async agents (Gemini Jules, Codex web, Claude Code web) for background refactoring.
- **Checks supported**: `test_suite_exists`, `tests_blocking_ci`, `code_review_required`, `small_batch_enforcement`, `ai_usage_norms`, `multiple_approach_culture`

### Trail of Bits — "How We Made Trail of Bits AI-Native (So Far)" (Mar 2026)

- **Type**: Conference presentation + open-source tooling
- **URL**: https://github.com/trailofbits/publications/tree/master/presentations/How%20we%20made%20Trail%20of%20Bits%20AI-Native%20%28so%20far%29
- **Relevance**: Dan Guido (CEO, Trail of Bits) at [un]prompted conference. Trail of Bits is a security auditing firm — their AI-native strategy is directly applicable to security-focused development. Provides concrete artifacts, not just philosophy.
- **Key concepts**:
  - **Compounding operating system**: AI isn't a feature you adopt. Build from incentives, defaults, guardrails, and verification loops that let humans and agents ship high-rigor work at higher throughput.
  - **[claude-code-config](https://github.com/trailofbits/claude-code-config)** (1,585 stars): Opinionated Claude Code defaults. Skip permission prompts, rely on OS-level sandboxing + hooks. Includes security scanners, linters, MCP servers.
  - **[trailofbits/skills](https://github.com/trailofbits/skills)** (3,525 stars): Reusable agent instructions for smart contract security, code auditing, malware analysis, vulnerability detection.
  - **[trailofbits/skills-curated](https://github.com/trailofbits/skills-curated)**: Vetted marketplace of community-reviewed skills. Addresses the trust problem — unreviewed skills could contain backdoors.
  - **Verification loops**: When discovery (finding issues) becomes abundant via AI, the value shifts to verification rigor. Pricing, staffing, and delivery models change.
- **Checks supported**: `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `type_safety`, `ai_usage_norms`, `security_critical_marking`

### BMad Method — BMAD-METHOD (2025–2026)

- **Type**: Open-source AI-driven agile framework (40.6k stars, 5k forks)
- **URL**: https://github.com/bmad-code-org/BMAD-METHOD
- **Relevance**: The most popular structured framework for AI-assisted agile development. Provides concrete workflow patterns for the full development lifecycle.
- **Key concepts**:
  - **Scale-Domain-Adaptive**: Automatically adjusts planning depth based on project complexity. A bug fix skips the full spec workflow; a new system gets the full treatment. Relevant to how teams calibrate AI guardrail depth.
  - **12+ specialized agents**: PM, Architect, Developer, UX, Scrum Master, each with domain expertise. Matches Uber's pattern of specialized over general-purpose agents.
  - **Party Mode**: Multiple agent personas collaborate in one session, discussing trade-offs. Multi-agent orchestration within a single context.
  - **BMad Help**: A meta-skill that tells you "what's next" at any point. Useful for onboarding teams to structured AI-assisted workflows.
  - **Modules**: Core method (34+ workflows), Test Architect (risk-based test strategy), Builder (create custom agents).
- **Checks supported**: `agent_instructions`, `multiple_approach_culture`, `ai_usage_norms`

## Blog Posts & Articles

### David Cramer / Sentry — "Optimizing Content for Agents" (Mar 2026)

- **Type**: Engineering blog post
- **URL**: https://cra.mr/optimizing-content-for-agents/
- **Relevance**: Sentry's CTO on making web content consumable by AI agents. Demonstrates that documentation needs to be agent-readable, not just human-readable — directly relevant to why `architecture_doc` and `agent_instructions` checks matter.
- **Key concepts**:
  - **Content negotiation**: When `Accept: text/markdown`, serve optimized markdown instead of HTML. Massive token savings and improved accuracy for agents.
  - **Docs optimization**: Serve true markdown, strip browser-only elements, optimize index pages as sitemaps.
  - **App UI redirect**: When a headless agent hits auth-required web UI, redirect to programmatic access (MCP server, CLI, API) instead of a useless login page.
  - **Full content bootstrap**: For smaller projects, serve the entire content so an agent can ingest it in one request.
- **Checks supported**: `architecture_doc`, `agent_instructions`, `api_contracts`

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

### Simon Willison — "Clinejection: Prompt Injection via Issue Triager" (Mar 2026)

- **Type**: Blog post / security analysis
- **URL**: https://simonwillison.net/2026/Mar/6/#clinejection
- **Relevance**: Documents a prompt injection attack against an AI-powered issue triage bot that led to a compromised npm package release (`cline@2.3.0`). AI agents with CI/CD write access are attack surface.
- **Key findings**:
  - Attack chain: malicious issue title → prompt injection → `npm install` backdoored package → cache poisoning → stolen npm publishing secrets
  - GitHub Actions caches can share the same name across different workflows, enabling cross-workflow cache poisoning
  - AI agents that run on untrusted input (issue titles, PR descriptions) with tool access are inherently vulnerable to injection
- **Checks supported**: `security_critical_marking`, `ai_usage_norms`, `ci_pipeline_exists`

### Simon Willison — "Shopify/Liquid: 53% Faster via Autoresearch" (Mar 2026)

- **Type**: Blog post / case study
- **URL**: https://simonwillison.net/2026/Mar/13/#shopifyliquid
- **Relevance**: Shopify CEO used an agent to run 120 automated experiments finding performance optimizations in a 20-year-old codebase (974 unit tests). Demonstrates that robust test suites are the primary unlock for agent-driven optimization. Benchmarking scripts make "make it faster" an actionable agent goal.
- **Key findings**:
  - 53% improvement on benchmarks from 93 commits via ~120 automated experiments
  - A robust test suite is a "massive unlock" for agent-driven work
  - The autoresearch pattern (brainstorm improvements, experiment one at a time) is effective for optimization
  - CEOs and people in high-interruption roles can productively work with code again via agents
- **Checks supported**: `test_suite_exists`, `tests_blocking_ci`, `coverage_measurement`

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
| Willison: Agentic Engineering Patterns | `test_suite_exists`, `tests_blocking_ci`, `code_review_required`, `small_batch_enforcement`, `ai_usage_norms`, `multiple_approach_culture` |
| Trail of Bits: AI-Native (Guido) | `agent_instructions`, `linter_enforcement`, `formatter_enforcement`, `type_safety`, `ai_usage_norms`, `security_critical_marking` |
| BMad Method (BMAD-METHOD) | `agent_instructions`, `multiple_approach_culture`, `ai_usage_norms` |
| Cramer: Optimizing Content for Agents | `architecture_doc`, `agent_instructions`, `api_contracts` |
| Willison: Clinejection analysis | `security_critical_marking`, `ai_usage_norms`, `ci_pipeline_exists` |
| Willison: Shopify autoresearch | `test_suite_exists`, `tests_blocking_ci`, `coverage_measurement` |

## Contributing

Found a relevant paper, blog post, or report? Add it here following the format above. Good candidates:
- Research on AI code generation quality and failure modes
- Industry reports on CI/CD and DevOps practices
- Engineering blog posts about AI-assisted development guardrails
- Benchmarks measuring AI-generated code reliability
- Security research on supply chain attacks and AI-specific vulnerabilities
- Conference talks and videos on testing, observability, and software quality
