# AI-Assisted Development Framework for Sec Section

**Audience**: Engineering leaders, EMs, and staff+ engineers in GitLab's Sec Section
**Status**: Draft — March 2026
**Companion**: [Consolidated Guide for Engineering Leaders](https://gitlab.com/groups/gitlab-org/-/work_items/20231#note_3148748215)

---

## Why This Document Exists

The consolidated guide covers the theory and research. This document translates it into a practical framework for the Sec Section specifically — covering our teams (Application Security Testing, Software Supply Chain Security, Security Risk Management), our codebases (Rails monolith, standalone analyzers, Go/Rust services), and our constraints (security-sensitive code, compliance requirements, customer-facing scanners).

Security code has a narrower margin for error than most. AI that's "80% correct" in a CRUD app is a minor annoyance. AI that's 80% correct in a vulnerability scanner is a customer-impacting bug. This framework accounts for that difference.

---

## Part 1: Where the Sec Section Sits Today

### Current State Assessment

Before adopting any practice, each team should self-assess on the autonomy spectrum:

| Level | Description | Sec Section Reality |
|---|---|---|
| Baseline | AI autocomplete, human writes everything | Most analyzer teams today |
| Pair | Human designs + reviews, agent codes | Some Rails monolith work |
| Conductor | Human steers single agent in tight loop | labkit-rs, artifact-registry-poc demos |
| Orchestrator | Human manages multiple async agents | Not yet, requires harness |
| Harness | Human sets architecture + quality bar | Target state for mature areas |

**Recommendation**: Most Sec teams should target the **Pair** level first, progressing to **Conductor** once guardrails are in place. Jumping to Orchestrator or Harness without the foundation produces unreliable security tooling.

### Sec-Specific Risks

| Risk | Why Sec Is Different | Mitigation |
|---|---|---|
| False negatives in scanners | AI-generated detection logic may miss vulnerability classes silently | Golden fixture testing against known-vulnerable repos |
| False positives in scanners | AI may broaden detection patterns without understanding precision trade-offs | Benchmark suites with precision/recall metrics |
| Compliance drift | AI may change audit event schemas, logging formats, or policy enforcement subtly | Contract tests for audit event structures |
| Credential handling | AI may log, expose, or mishandle secrets in scanner code | Dedicated security review skill (see Part 4) |
| Analyzer compatibility | Standalone analyzers must work across GitLab versions | MSRV/compatibility matrix testing (labkit-rs pattern) |

---

## Part 2: The Harness — What to Build

The harness is the infrastructure that makes AI agents produce reliable output. It has three components: constraints, context, and garbage collection.

### 2.1 Constraints (Enforce Mechanically)

These must be in CI, not in agent instructions. Agent memory is unreliable. CI is ground truth.

#### For Rails Monolith (Sec-owned code)

| Constraint | How to Enforce | Priority |
|---|---|---|
| Audit event schema stability | Contract tests that fail if event structure changes without migration | High |
| No raw SQL in new code | Custom RuboCop cop with remediation message | Medium |
| Policy enforcement layer boundaries | Structural tests: policy checks happen in service layer, never in controllers | High |
| Feature flag gating for all new functionality | CI check that new endpoints have feature flag references | Medium |
| CODEOWNERS coverage | CI check that all Sec-owned directories have CODEOWNERS entries | Low |

#### For Standalone Analyzers (Go, Rust, Python)

| Constraint | How to Enforce | Priority |
|---|---|---|
| Scanner output format stability | Golden fixture tests against known-vulnerable test repos | High |
| No network calls in unit tests | CI flag that fails if tests make outbound connections | Medium |
| Dependency license compliance | `cargo deny` / `license_finder` in CI | High |
| SAST/DAST result schema | JSON schema validation in CI against published schema | High |
| Minimum test coverage per package | Coverage gate in CI (suggest 70% for new code) | Medium |

#### For All Sec Repos

| Constraint | How to Enforce | Priority |
|---|---|---|
| Conventional commits | `commitlint` in CI (labkit-rs pattern) | Low |
| `AGENTS.md` / `CLAUDE.md` sync | `diff AGENTS.md CLAUDE.md` in CI (labkit-rs pattern) | Low |
| Pre-push checks documented | `.cursor/rules/` or equivalent with fmt/lint/test | Medium |
| No secrets in code | GitLab Secret Detection template in CI | High |
| Dependency vulnerability scanning | GitLab Dependency Scanning template in CI | High |

### 2.2 Context (What the Agent Needs to Know)

The guide's three-layer hierarchy, adapted for Sec:

#### Layer 1: Global (`~/.claude/CLAUDE.md` or `~/.cursor/rules/`)

Keep this short (~20 lines). Cross-project concerns only:
- GitLab CLI usage (`glab`)
- MCP server configuration
- Code quality standards (no narration comments, humanizer rules)
- Commit message format

**You already have this.** Your existing `~/.claude/CLAUDE.md` and Cursor rules cover this layer.

#### Layer 2: Project (`AGENTS.md` at repo root, ~50-100 lines)

This is the table of contents. It should point to structured docs, not contain them. Based on what worked in artifact-registry-poc and labkit-rs:

```
# {Project Name}

## What This Is
One paragraph. What the project does, who uses it, where it fits in GitLab.

## Architecture
See docs/ARCHITECTURE.md

## Commands
{build, test, lint — the 5 commands an agent needs}

## Conventions
- {Language-specific patterns}
- {Error handling approach}
- {Test structure}

## Documentation Index
| Doc | When to Read | When to Update |
|-----|--------------|----------------|
| docs/ARCHITECTURE.md | Understanding structure | Adding modules |
| docs/DECISIONS.md | Implementation decisions | Making non-trivial choices |
| docs/SECURITY.md | Auth, credential handling | Changing security boundaries |

## References
- {Link to design docs, epics, upstream specs}
```

#### Layer 3: Module (nested `AGENTS.md` in subdirectories, as needed)

Use sparingly. Only for modules with non-obvious conventions that differ from the project root.

### 2.3 Garbage Collection (Continuous Cleanup)

Instead of manual Friday cleanup, schedule agents to scan for:

| GC Task | Cadence | What It Produces |
|---|---|---|
| Stale TODO/FIXME scan | Weekly | Issue with list of stale items |
| Test coverage drift | Per-MR | Warning comment if coverage drops |
| Documentation freshness | Weekly | MR updating outdated doc references |
| Dependency update | Weekly (Renovate) | MR per dependency bump |
| Quality score update | Monthly | Updated QUALITY_SCORE.md |

**Start with what exists**: Renovate for dependency updates, GitLab SAST/DAST templates for security scanning. Add custom GC agents only after the basics are solid.

---

## Part 3: Testing Strategy for AI-Generated Code

This is the highest-leverage section. From the research: **never give an agent a feature without a failing test.**

### The Testing Pyramid for Sec

```
                    ┌─────────────┐
                    │   E2E with  │  ← Known-vulnerable repos
                    │   real scan │     Scanner accuracy tests
                    ├─────────────┤
                    │ Integration │  ← Schema contract tests
                    │   tests     │     Wire format golden fixtures
                    ├─────────────┤
                    │ Unit tests  │  ← Detection logic
                    │             │     Parser correctness
                    │             │     Policy evaluation
                    └─────────────┘
```

### Patterns to Adopt

| Pattern | When to Use | Sec Example |
|---|---|---|
| **Failing test first** | Always — before every AI implementation task | Write a test that detects CVE-2024-XXXX, then let the agent implement the detection rule |
| **Golden fixture testing** | Wire protocols, scanner output, audit events | Commit known-good scanner output as fixtures; CI verifies implementation matches |
| **Snapshot testing** | JSON output formats, log structures | `cargo-insta` (Rust), `approval_tests` (Ruby) for scanner report format |
| **Characterization tests** | Before any AI-assisted refactor | Wrap existing scanner behavior in tests before letting an agent refactor |
| **Contract tests** | Cross-service boundaries, schema stability | Audit event schema, analyzer report schema, API contracts |
| **Compatibility matrix testing** | Standalone analyzers | Test against multiple GitLab versions (labkit-rs MSRV pattern) |
| **Benchmark testing** | Performance-sensitive scanners | A/B comparison in CI, results posted to MR (labkit-rs pattern) |

### Test Deletion Protection

From Kent Beck's finding: AI agents delete tests to make them pass. Add a CI check:

```yaml
test-count-check:
  script:
    - CURRENT=$(grep -r "#\[test\]" --include="*.rs" -c | awk -F: '{s+=$2} END {print s}')
    - PREVIOUS=$(git stash list > /dev/null; git show HEAD~1:test-count.txt 2>/dev/null || echo 0)
    - |
      if [ "$CURRENT" -lt "$PREVIOUS" ]; then
        echo "Test count decreased from $PREVIOUS to $CURRENT. Justify or restore."
        exit 1
      fi
    - echo "$CURRENT" > test-count.txt
```

Adapt for your language. The point: test count should never decrease without explicit justification.

---

## Part 4: Guardrails Specific to Security Code

### 4.1 Agent Rules for Sec Code

Add these to your project-level `AGENTS.md` / `CLAUDE.md`:

```markdown
## Security Guardrails

### Credential Handling
- Never log credentials, tokens, or secrets — not even in debug logging
- Never include real credentials in test fixtures — use obviously fake values
- When handling user-provided credentials, encrypt at rest and decrypt only at use time
- If you need to add credential handling, stop and ask for a security review

### Scanner Accuracy
- Never broaden a detection pattern without adding a test for the new case
- Never narrow a detection pattern without documenting what is no longer detected
- Every detection rule must have at least one true-positive and one false-positive test
- When in doubt about detection accuracy, prefer false positives over false negatives

### Audit Events
- Never change audit event schema without a migration
- Audit event names are public API — treat them as such
- Every state-changing operation in policy enforcement must emit an audit event

### Dependency Management
- Never add a dependency without checking its license compatibility
- Prefer vendored/well-known dependencies over novel ones for security-critical code
- When AI suggests a library you haven't seen before, verify it exists and is maintained
```

### 4.2 Review Checklist for AI-Generated Security Code

When reviewing AI-generated MRs in Sec repos, check these beyond the standard review:

1. **Detection logic**: Does it handle edge cases in the vulnerability pattern? (malformed input, encoding variants, nested contexts)
2. **Taint propagation**: If this is SAST/DAST related, does the data flow analysis cover all sources and sinks?
3. **Scanner output**: Does the output match the published schema exactly? Run golden fixture tests.
4. **Error handling in scanners**: Does the scanner fail gracefully on malformed input, or does it crash? A crash in a customer's CI pipeline is a support escalation.
5. **Resource limits**: Does the AI-generated code have timeouts, memory limits, and file size limits for scanning? Unbounded resource consumption is a DoS vector.
6. **Backwards compatibility**: Does this change break existing integrations? Check schema versions.

### 4.3 Cognitive Bias Mitigations for Sec

The guide identifies 15 bias categories. These three matter most for security code:

| Bias | Sec-Specific Risk | Mitigation |
|---|---|---|
| **Automation bias** | Trusting AI-generated detection logic because "the AI knows security" | Every detection rule needs a manual review by someone who understands the vulnerability class |
| **Confirmation bias** | AI generates code that passes existing tests, but existing tests don't cover the edge case | Write adversarial tests: inputs designed to break the detection, not confirm it works |
| **Anchoring** | First AI suggestion for a scanner rule becomes the implementation without exploring alternatives | Generate 2-3 detection approaches before selecting. Compare precision/recall on test corpus. |

---

## Part 5: Implementation Roadmap

### Phase 0: Foundation (Week 1-2)

Every Sec team, regardless of current AI adoption level:

- [ ] **Audit your AGENTS.md / CLAUDE.md**: If over 100 lines or covering multiple concerns, restructure into the three-layer hierarchy
- [ ] **Add `AGENTS.md` / `CLAUDE.md` sync check to CI** (if using both tools)
- [ ] **Document the 5 commands**: build, test, lint, format, and any project-specific commands — in the agent instructions file
- [ ] **Write down current project state**: "Phase X is complete. Phase Y is next. Here are the open decisions." Agents can't infer this.
- [ ] **Verify your CI has**: SAST, Secret Detection, Dependency Scanning, and test coverage reporting

### Phase 1: Testing Harness (Week 3-4)

The highest-leverage investment:

- [ ] **Add golden fixture tests** for scanner output formats (at least one per analyzer)
- [ ] **Add contract tests** for audit event schemas your team owns
- [ ] **Add snapshot testing** for any JSON/structured output format
- [ ] **Add test count protection** to CI
- [ ] **Write characterization tests** for any code you plan to refactor with AI

### Phase 2: Architectural Constraints (Week 5-6)

Encode what the team already knows into mechanical enforcement:

- [ ] **Write `ARCHITECTURE.md`** following matklad's principles: short, focused on things unlikely to change, include a codemap, call out invariants as constraints
- [ ] **Add structural tests** for layer boundaries (e.g., "policy service never calls database directly")
- [ ] **Add custom linter rules** with remediation messages agents can read (RuboCop for Rails, clippy/dylint for Rust, golangci-lint for Go)
- [ ] **Create `DECISIONS.md`** and start recording non-trivial implementation decisions

### Phase 3: AI Integration (Week 7-8)

Now that the harness exists, safely increase AI involvement:

- [ ] **Add AI review as a CI stage** (labkit-rs pattern with `ai-review-bot`)
- [ ] **Add benchmark commenting on MRs** for performance-sensitive code
- [ ] **Create a QUALITY_SCORE.md** grading each module/team area
- [ ] **Define the team's AI stance**: What level of autonomy is appropriate? What requires human review? Where are the limits?

### Phase 4: Scale (Month 3+)

- [ ] **Schedule GC agents** for weekly scans (stale docs, pattern violations, quality score updates)
- [ ] **Move from Pair to Conductor** for well-harnessed areas
- [ ] **Share wins across teams**: Peer sharing is the strongest adoption driver (Uber finding)
- [ ] **Evaluate spec-driven development** for new features (spec-anchored level)

---

## Part 6: Quality Score Template for Sec

Maintain this in `docs/QUALITY_SCORE.md` and update monthly:

```markdown
# Quality Score — Sec Section

Last updated: YYYY-MM-DD

## Scoring
- A: Excellent — all checks pass, well-documented, tested, stable API
- B: Good — minor gaps, actively maintained
- C: Needs work — known gaps, improvement planned
- D: At risk — significant gaps, immediate attention needed

## Application Security Testing

| Module | Tests | Docs | API Stability | Scanner Accuracy | AI Readiness | Overall |
|--------|-------|------|---------------|-----------------|--------------|---------|
| SAST | | | | | | |
| DAST | | | | | | |
| Secret Detection | | | | | | |
| Composition Analysis | | | | | | |
| API Security | | | | | | |
| Vulnerability Research | | | | | | |

## Software Supply Chain Security

| Module | Tests | Docs | API Stability | Compliance Coverage | AI Readiness | Overall |
|--------|-------|------|---------------|--------------------|--------------|---------| 
| Compliance | | | | | | |
| Authorization | | | | | | |
| Authentication | | | | | | |
| Anti-abuse | | | | | | |

## Security Risk Management

| Module | Tests | Docs | API Stability | Policy Coverage | AI Readiness | Overall |
|--------|-------|------|---------------|----------------|--------------|---------| 
| Security Infrastructure | | | | | | |
| Security Insights | | | | | | |
| Security Policies | | | | | | |

## AI Readiness Criteria
- A: AGENTS.md exists, golden fixtures, contract tests, ARCHITECTURE.md, custom lints
- B: AGENTS.md exists, some golden fixtures, basic test coverage
- C: AGENTS.md exists, minimal testing specific to AI workflows
- D: No AI-specific infrastructure
```

---

## Part 7: Key Principles (Summary)

1. **Constraints are multipliers.** Once encoded in CI, they apply to every line of code, every agent session, every contributor. This matters more in security code than anywhere else.

2. **Never give an agent a feature without a failing test.** This is the single highest-leverage practice from all the research. For Sec: never give an agent a detection rule without a test case of the vulnerability.

3. **Fix the environment, not the prompt.** When an agent fails, the response is a new test, lint rule, doc, or type constraint — not a better prompt.

4. **AI amplifies what exists.** Teams with good CI, testing, and documentation will get more from AI. Teams with gaps will get those gaps amplified. Fix the foundation first.

5. **Security code has a narrower margin.** The "80% correct" problem is more dangerous in scanners, policy enforcement, and credential handling. The testing and review bar must be higher than for general application code.

6. **Author-reviewer separation is non-negotiable.** Never let the agent that wrote security code also approve it. This is structural protection, not process overhead.

7. **The repo is the single source of truth.** Everything the agent needs — architecture, decisions, quality scores, execution plans — lives in the repo. Slack discussions don't count. Google Docs don't count (for agents). If it's not committed, it doesn't exist.

---

## Appendix: Tools and References

### Internal References
- [labkit-rs](https://gitlab.com/gitlab-org/rust/labkit-rs) — Best-in-class example of AI-assisted Rust development at GitLab. CLAUDE.md/AGENTS.md sync, golden fixture testing, AI review in CI, benchmark commenting.
- [artifact-registry-poc](https://gitlab.com/jdrpereira/artifact-registry-poc) — 6-day PoC with zero human-written code. 64 recorded decisions, DECISIONS.md pattern, guardrail feedback loop.
- [ai-harness-scorecard](https://gitlab.com/markmishaev/ai-harness-scorecard) — Tool to grade repos on engineering safeguards for AI-assisted development.

### External References — Research and Strategy
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering) — Primary source on environment-first AI development
- [DORA 2025 Report](https://dora.dev/research/2025/dora-report) — AI amplifies existing strengths and weaknesses
- [Martin Fowler: Harness Engineering Analysis](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) — Critical analysis of verification gaps
- [Kent Beck on TDD + AI](https://newsletter.pragmaticengineer.com) — TDD as the safeguard against AI regressions
- [matklad: ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) — How to write architecture docs that agents can use
- [GitHub: How to write a great agents.md](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md/) — Analysis of 2,500+ repos
- [Uber: AI for Development](https://newsletter.pragmaticengineer.com/p/how-uber-uses-ai-for-development) — Parallel agent orchestration, MCP gateway, specialized AI tools at scale

### External References — Practitioner Guides and Tooling

#### [Simon Willison: Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/)

An evolving guide (11 chapters, started Feb 2026) from the creator of Datasette, documenting patterns for working with coding agents. Written from hands-on daily experience, not theory. Key chapters:

- **"AI should help us produce better code"** — The central argument: shipping worse code with agents is a choice. Code production cost is near-zero, so use the savings to pay down technical debt, not accumulate it. Refactoring tasks (splitting large files, renaming concepts, fixing API duplication) are ideal for background agents. Fire up an agent, tell it what to change, evaluate the PR.
- **"Anti-patterns: things to avoid"** — The #1 anti-pattern: filing PRs with code you haven't reviewed yourself. Agents write convincing PR descriptions — you need to review those too. A good agentic PR includes evidence you've tested it (screenshots, manual test notes, specific implementation comments).
- **"Writing code is cheap now"** — Code production costs dropping to near-zero disrupts traditional engineering intuitions about trade-offs. What used to be "not worth the effort" (fixing naming inconsistencies, splitting modules, prototyping alternatives) is now trivial to do.
- **"Red/green TDD"** — Write the failing test, let the agent make it pass. This gives the agent a mechanical success criterion. Same pattern as the consolidated guide, confirmed independently.
- **"Agentic manual testing"** — The defining characteristic of a coding agent is that it can execute the code it writes. Never assume LLM-generated code works until it has been executed. Agents should test their own output using Playwright or equivalent.
- **"Hoard things you know how to do"** — Document patterns and solutions you discover during agent work. They compound across future sessions.

**What to adopt**: The anti-pattern rule belongs in every Sec team's review guidelines. The compound engineering loop (retrospective after each AI project, document what worked) maps directly to the DECISIONS.md and LESSONS.md patterns.

#### [David Cramer / Sentry: Optimizing Content for Agents](https://cra.mr/optimizing-content-for-agents/)

Sentry's CTO on making web content agent-consumable. The core technique: **content negotiation**. When a request arrives with `Accept: text/markdown`, serve optimized markdown instead of HTML. Three optimizations:

1. **Docs** — Serve true markdown (massive token savings), strip browser-only elements (nav, JS), optimize index pages as sitemaps
2. **App UI** — When a headless bot hits the auth-required web UI, redirect to programmatic access (MCP server, CLI, API) instead of a useless login page
3. **Full content bootstrap** — For smaller projects, serve the entire content so an agent can ingest it in one request

**Why this matters for Sec**: Our security documentation, API specs, and scanner configuration guides should be agent-readable. If an agent building an integration can't parse our docs, it will hallucinate the API contract. Content negotiation (`Accept: text/markdown`) is a zero-cost way to make existing docs work for both humans and agents.

#### [Trail of Bits: How We Made Trail of Bits AI-Native (So Far)](https://github.com/trailofbits/publications/tree/master/presentations/How%20we%20made%20Trail%20of%20Bits%20AI-Native%20%28so%20far%29)

Presentation by Dan Guido (CEO, Trail of Bits) at [un]prompted conference, March 2026. Trail of Bits is a security auditing firm — their AI-native approach is directly relevant to Sec Section work.

**Core idea**: AI isn't a feature you adopt. It's a force that commoditizes effort and shortens the half-life of best practices. The strategy is a compounding operating system built from incentives, defaults, guardrails, and verification loops.

**Concrete artifacts**:
- **[trailofbits/claude-code-config](https://github.com/trailofbits/claude-code-config)** (1,585 stars) — Opinionated defaults for Claude Code. Key philosophy: minimize delay between intent and execution by skipping permission prompts, then rely on OS-level sandboxing and hooks as guardrails. Includes setup for security scanners, linters, and MCP servers.
- **[trailofbits/skills](https://github.com/trailofbits/skills)** (3,525 stars) — Skills for smart contract security, code auditing, malware analysis, vulnerability detection. These are reusable agent instructions for specific security domains.
- **[trailofbits/skills-curated](https://github.com/trailofbits/skills-curated)** — A vetted marketplace of community-reviewed skills. Addresses the trust problem: unreviewed skills could contain backdoors. Curated skills are reviewed before inclusion.

**What to adopt**: The skills approach maps directly to our Cursor skills and Claude Code skills. Trail of Bits proves that security-specific skills (vulnerability detection patterns, audit checklists, threat modeling) work in practice. Their `claude-code-config` repo is a good reference for standardizing team-wide Claude Code setups. The curated skills marketplace model is worth considering if we build Sec-specific skills.

#### [BMad Method (BMAD-METHOD)](https://github.com/bmad-code-org/BMAD-METHOD)

An open-source AI-driven agile development framework (40.6k stars, 5k forks). Provides structured workflows for the full development lifecycle using AI agents.

**Key concepts**:
- **Scale-Domain-Adaptive** — Automatically adjusts planning depth based on project complexity (bug fix vs. enterprise system)
- **12+ specialized agents** — PM, Architect, Developer, UX, Scrum Master, each with domain expertise. Matches the Uber pattern of specialized agents over general-purpose ones.
- **Party Mode** — Bring multiple agent personas into one session to collaborate and discuss trade-offs. Essentially multi-agent orchestration within a single context.
- **BMad Help** — An always-available skill that tells you "what's next" at any point in the workflow
- **Modules**: Core method (34+ workflows), Test Architect (risk-based test strategy), Builder (create custom agents), Game Dev Studio, Creative Intelligence Suite

**What to adopt**: The scale-adaptive concept is relevant. Not every Sec task needs the same level of planning. A bug fix in a scanner should skip the full spec-driven workflow. A new detection engine needs the full treatment. BMad's approach of auto-detecting complexity and adjusting process depth is worth studying. The `bmad-help` pattern (a meta-skill that guides the engineer through the process) could be useful for onboarding teams to AI-assisted development.

### External References — From simonwillison.net (March 2026)

Recent posts with direct relevance:

- **[Clinejection: Compromising Cline via Issue Triager](https://simonwillison.net/2026/Mar/6/#clinejection)** — A prompt injection attack against an AI-powered issue triage bot that led to a compromised npm package release. The attack chain: malicious issue title → prompt injection → `npm install` backdoored package → cache poisoning → stolen npm publishing secrets. Direct relevance for Sec: AI agents with write access to CI/CD are attack surface.
- **[Shopify/Liquid: 53% faster via autoresearch](https://simonwillison.net/2026/Mar/13/#shopifyliquid)** — Shopify CEO used an agent to run 120 automated experiments finding performance optimizations in a 20-year-old codebase. Key insight: a robust test suite (974 unit tests) is a "massive unlock" for agent work. Benchmarking scripts make "make it faster" an actionable agent goal. Directly applicable to scanner performance optimization.
- **[Perhaps not Boring Technology after all](https://simonwillison.net/2026/Mar/9/#perhaps-not-boring-technology-after-all)** — Addresses the concern that AI pushes toward common/popular tools. Willison argues agents actually make it easier to explore less common but better-fit tools through rapid prototyping.
