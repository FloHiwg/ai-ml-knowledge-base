# Harness Engineering: Leveraging Codex in an Agent-First World — OpenAI

**Source:** [[raw/articles/Harness engineering leveraging Codex in an agent-first world  OpenAI]]
**Author:** OpenAI (Codex team)
**Related:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]] · [[summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]] · [[summaries/AINews Is Harness Engineering real - Latent.Space]] · [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]]

---

## Core Idea

OpenAI's Codex team built and shipped a real internal product over five months with **0 lines of manually-written code** — a million lines of code, ~1,500 PRs, generated entirely by Codex agents directed by 3–7 engineers. The central lesson: when agents do the coding, the engineer's job shifts entirely to **designing environments, specifying intent, and building feedback loops**. The discipline shows up in the scaffolding, not the code.

---

## Scale and Throughput

| Metric | Value |
|---|---|
| Development period | 5 months (starting August 2025) |
| Total lines of code | ~1 million |
| Pull requests merged | ~1,500 |
| Team size | 3 engineers (grew to 7) |
| Average throughput | 3.5 PRs per engineer per day |
| Speed vs. hand-written | ~10× faster estimated |
| Throughput trend | Increased as team grew |

The product shipped to internal daily users and external alpha testers. Everything was agent-generated: application logic, tests, CI configuration, documentation, observability, and internal tooling.

---

## Redefining the Engineer's Role

Early progress was slower than expected — not because the model was incapable, but because the environment was underspecified. The agent lacked the tools, abstractions, and structure to make progress toward high-level goals.

The engineer's job became asking: **"What capability is missing, and how do we make it both legible and enforceable for the agent?"** The workflow: describe a task, run the agent, let it open a PR, then have it review its own changes (locally and in the cloud), respond to feedback, and iterate until all agent reviewers are satisfied — a self-contained loop.

**Humans never wrote code.** This was an explicit constraint, used to force the team to build leverage rather than take shortcuts.

---

## Increasing Application Legibility

A key insight: **anything the agent can't access in-context effectively doesn't exist.** Knowledge in Google Docs, chat threads, or people's heads is illegible to the system. Only repository-local, versioned artifacts are accessible.

Investments to make the application legible to Codex:

| Capability | How it was built |
|---|---|
| **Per-worktree app instances** | App bootable per git worktree so Codex can launch one instance per change |
| **Browser automation** | Chrome DevTools Protocol wired into agent runtime; skills for DOM snapshots, screenshots, navigation |
| **Observability** | Ephemeral local observability stack per worktree; Codex can query logs (LogQL) and metrics (PromQL) |
| **UI validation** | Codex can record videos demonstrating bugs and fixes, validate changes by driving the application directly |

This enabled prompts like "ensure service startup completes in under 800ms" or "no span in these four critical user journeys exceeds two seconds" to become tractable. Single Codex runs routinely run for 6+ hours.

---

## Repository as System of Record

Context management is the primary challenge for large-scale agent work. The key principle: **give the agent a map, not a 1,000-page instruction manual.**

Problems with monolithic instruction files:
- Context is a scarce resource — a giant file crowds out task, code, and docs
- "When everything is important, nothing is" — agents pattern-match locally instead of navigating intentionally
- Documentation rots instantly in a high-velocity codebase
- Impossible to verify mechanically

### Solution: AGENTS.md as Table of Contents

`AGENTS.md` (~100 lines) serves only as a **map with pointers**. The actual knowledge lives in a structured `docs/` directory:

- Design documentation: catalogued with verification status and agent-first operating principles
- Architecture documentation: top-level map of domains and package layering
- Quality document: grades each product domain and architectural layer, tracks gaps over time
- Plans as first-class artifacts: ephemeral lightweight plans for small changes; execution plans with progress/decision logs checked into the repo for complex work; active plans, completed plans, and known technical debt all versioned and co-located

**Mechanical enforcement:** dedicated linters and CI jobs validate that the knowledge base is up to date, cross-linked, and structured correctly. A recurring "doc-gardening" agent scans for stale documentation and opens fix-up PRs.

---

## Enforcing Architecture and Taste

Documentation alone doesn't keep an agent-generated codebase coherent. The principle: **enforce invariants, not implementations.**

### Rigid Architectural Model

Each business domain is divided into fixed layers with strictly validated dependency directions:

```
Within a domain: Types → Config → Repo → Service → Runtime → UI
Cross-cutting concerns (auth, connectors, telemetry, feature flags): enter only via Providers
Everything else: disallowed and enforced mechanically
```

Enforced via custom linters (themselves Codex-generated) and structural tests. Error messages in custom lints are written to inject remediation instructions into agent context.

This architecture — typically postponed until hundreds of engineers — becomes an **early prerequisite** with agents: constraints are what allows speed without decay.

### Taste Invariants

Statically enforced: structured logging, naming conventions for schemas/types, file size limits, platform-specific reliability requirements. The resulting code doesn't always match human stylistic preferences — that's acceptable, as long as output is correct, maintainable, and legible to future agent runs.

Human taste is fed back continuously: review comments and bugs become documentation updates or tooling rules. When documentation falls short, rules are promoted into code.

### "Boring Technology" Preference

Technologies described as "boring" tend to be easier for agents to model: composable, stable APIs, well-represented in training data. In some cases, it was cheaper to have the agent reimplement a small subset of a library's functionality than to work around opaque upstream behavior — e.g., a custom `map-with-concurrency` helper with 100% test coverage rather than `p-limit`, tightly integrated with their OpenTelemetry instrumentation.

---

## Merge Philosophy Under High Throughput

High agent throughput inverts conventional merge norms:

- Minimal blocking merge gates — corrections are cheap, waiting is expensive
- Short-lived pull requests
- Test flakes addressed with follow-up runs rather than blocking progress
- Almost all review effort pushed to agent-to-agent

This would be irresponsible in a low-throughput environment. At 3.5 PRs/engineer/day, it is often the right tradeoff.

---

## Entropy and Garbage Collection

Full agent autonomy introduces a novel problem: Codex replicates patterns that exist in the repository — including uneven or suboptimal ones. Over time, this leads to drift.

Initial approach: humans spent every Friday (20% of the week) cleaning up "AI slop." That didn't scale.

### Solution: Golden Principles + Recurring Cleanup Agents

"Golden principles" are opinionated, mechanical rules encoded into the repository:
1. Prefer shared utility packages over hand-rolled helpers to keep invariants centralized
2. Don't probe data "YOLO-style" — validate boundaries or rely on typed SDKs

On a regular cadence, background Codex tasks scan for deviations, update quality grades, and open targeted refactoring PRs. Most can be reviewed in under a minute and automerged.

This functions like **garbage collection**: technical debt is paid down continuously in small increments rather than compounding. Human taste is captured once, then enforced continuously on every line of code.

---

## End-to-End Autonomy Milestone

After encoding the full development loop (testing, validation, review, feedback handling, recovery), the system crossed a threshold where a single prompt can drive an entire feature end-to-end:

1. Validate current codebase state
2. Reproduce a reported bug
3. Record a video demonstrating the failure
4. Implement a fix
5. Validate the fix by driving the application
6. Record a video demonstrating the resolution
7. Open a PR
8. Respond to agent and human feedback
9. Detect and remediate build failures
10. Escalate to a human only when judgment is required
11. Merge the change

This level of autonomy is **repository-specific** — it depends on the specific structure and tooling built over five months. It should not be assumed to generalize without similar investment.

---

## Key Takeaways

- **Humans steer; agents execute.** The engineer's job becomes environment design, intent specification, and feedback loop construction — not writing code.
- **Agent legibility is the primary investment.** Anything the agent can't access in-context doesn't exist. Push all relevant knowledge into the repo as versioned artifacts.
- **AGENTS.md as map, not manual.** Short, stable, pointer-based. Deep context lives in a structured docs/ directory with mechanical freshness enforcement.
- **Enforce invariants mechanically, not stylistically.** Rigid architectural models and custom lints allow agents to ship fast without causing decay. Error messages should inject remediation instructions.
- **Garbage collection is a first-class process.** Encode golden principles once; run background agents continuously to enforce them. 20% cleanup Fridays do not scale.
- **"Boring" technology beats complex libraries for agent legibility.** Composable, stable APIs are easier for agents to model; reimplementation of small subsets is sometimes cheaper than dealing with opaque upstream behavior.
- **High throughput inverts merge norms.** At agent-scale PR volume, speed > blocking — corrections are cheap, waiting is expensive.
- **Throughput increases with team growth** — the leverage compounds, unlike traditional engineering where adding engineers adds coordination costs.
