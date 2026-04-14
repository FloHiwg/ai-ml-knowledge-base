# Agent Harness Engineering

**Related:** [[applications/agentic-patterns]] · [[applications/prompt-injection]] · [[applications/guardrails]] · [[inference/prompting-and-reasoning]]  
**Sources:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]] · [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]] · [[summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]] · [[summaries/AINews Is Harness Engineering real - Latent.Space]] · [[summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]]

---

## Big Model vs. Big Harness

A live debate (as of early 2026) about where the primary leverage in agent engineering lies. See [[summaries/AINews Is Harness Engineering real - Latent.Space]] for a full synthesis.

**Big Model position:** Harnesses are temporary scaffolding that better models will make obsolete. The Bitter Lesson (see [[concepts/scaling-and-the-bitter-lesson]]) predicts this. Evidence: reasoning models (o1, R1) eliminated entire classes of agentic scaffolding that previously existed to simulate chain-of-thought. METR found Claude Code and Codex don't beat a basic scaffold. Scale AI SWE-Atlas data shows harness effects are within margin of error and model-specific. Claude Code team: "all the secret sauce is in the model — this is the thinnest possible wrapper."

**Big Harness position:** The harness is the product. The irreducible core loop — `while (model returns tool calls): execute → capture → append → call` — is simple, but the leverage above that loop is real. Pi blog showed dramatic improvements across 15 models by optimizing the harness alone. Cursor's $50B valuation is market evidence. Jerry Liu: "the biggest barrier to getting value from AI is your own ability to context and workflow engineer the models."

**Resolution:** Neither side is disinterested. The practical synthesis: harness complexity that compensates for current model limitations is a candidate for obsolescence; harness complexity that expresses model capability more fully has durable value. New model capabilities expose new application domains, which create new harness requirements — the layer evolves rather than disappears.

---

## What Is a Harness?

**Agent = Model + Harness.** The Harness is all engineering infrastructure beyond the model itself — the orchestration loop, tool system, context management, sub-agent infrastructure, permissions, middleware, and error handling. If the model is the engine, the Harness is the chassis, drivetrain, and cockpit.

Harness engineering is not a one-time static design. It co-evolves with model capability: as models grow stronger, prompts become simpler and the engineering focus shifts to efficiency optimization — cache utilization, concurrency, and compression granularity.

---

## Capability Dimensions

| Dimension | What it covers |
|---|---|
| **Main Loop (ReAct Loop)** | LLM call → tool execution → result feedback — the core orchestration heartbeat |
| **System Prompt** | Instruction assembly and dynamic injection; caching strategies |
| **Tool System** | Tool registration, execution, result handling, lazy loading, MCP integration |
| **Sub-Agent** | Task delegation, context isolation, parallel execution, anti-recursion |
| **Context Management** | Token budget, automatic compression, summary generation |
| **Middleware / Hooks** | Interception before/after LLM calls and tool calls; extensibility |
| **Memory / State** | Session persistence, cross-session memory |
| **Permission System** | Approval and security control for tool execution |
| **Error Handling** | Retry, fallback, context overflow recovery |

---

## ReAct Loop Patterns

All mature agents implement the ReAct loop. Key variations:

| Approach | Example | Notes |
|---|---|---|
| Recursive calls | Claude Code 2025 | Simple but hard to control; no streaming |
| while loop + state machine | Claude Code 2026 | Controllable; enables streaming tool execution |
| while loop (bounded) | Goose (max 1000), Gemini CLI (max 30, 10min timeout) | Prevents runaway loops |
| Outer + inner loop | PI Agent | Outer handles follow-ups, inner handles tool calls |

### Streaming Tool Execution

The most significant latency optimization: tools begin executing as soon as their parameters are parsed from the LLM's streaming output, rather than waiting for the complete response.

```
2025 pattern: Complete LLM response → parse tool_use → execute tools → next iteration
2026 pattern: Streaming response → parse while receiving → execute while parsing → state machine drives next round
```

With 3 concurrent tool calls, the first tool can start immediately when its parameters are complete — not after all three are fully generated. Introduced in Claude Code 2026; also used by Goose (Rust async/Tokio `select_all`) and Gemini CLI.

---

## Context Management Strategies

Long-running agents accumulate tool calls, results, and conversation history that quickly exhaust the context window. Strategies range from simple to complex:

### 5-Layer Compression (Claude Code 2026)

The most mature production design — layers from lightweight to emergency:

```
1. Snip (HISTORY_SNIP)       — delete old messages, preserve protected tail
2. Microcompact               — deduplicate cached tool results by tool_use_id
3. Autocompact                — LLM summary compresses history
                                circuit breaker: stops after 3 consecutive failures
4. Reactive Compact           — responds to API prompt-too-long errors; emergency compress + retry
5. Context Collapse           — message groups → summaries; read-time projection (non-destructive)
```

Key properties:
- **Circuit breaker**: stops automatic compression after 3 failures, preventing infinite loops
- **Read-time projection** (Context Collapse): doesn't modify original messages — dynamically generates compressed views on read, preserving backtrack possibility

### Other Approaches

| Approach | Used by | Key property |
|---|---|---|
| LLM summary + tool-pair batches | Goose | Trigger at 80% context |
| Structured summaries (Goal/Progress/Decisions/Files/Next Steps) | Hermes Agent | Iterative updates preserve core info across multiple compression cycles |
| D-Mail time travel | Kimi CLI | Checkpoint rollback — rolls context back to a prior state, discarding dead-end paths |
| Reverse token budget + truncation | Gemini CLI | Trigger at 50% model limit |
| `transformContext` hook | PI Agent | Fully app-layer; maximum flexibility |

**D-Mail** is particularly valuable for exploratory tasks: if approach A fails, the agent rolls back to the branching point rather than contaminating subsequent context with failed attempts.

---

## Sub-Agent Architectures

Sub-agents show the greatest variation and best reflect architectural philosophy:

### Independent Context (Claude Code 2025, Goose, Hermes Agent)

Each sub-agent starts fresh with its own message history. Simple and isolated but doesn't share parent context — no prompt cache reuse.

### Fork Sub-Agent (Claude Code 2026)

Sub-agents fork from the parent's context instead of starting from scratch:

```
Parent assistant message (containing multiple tool_use)
  ↓ Build fork child messages:
  [Full history | assistant(all tool_use) | user(placeholder results + subtask instructions)]
  ↓ Only the last text block differs across sub-agents
  ↓ → maximize prompt cache hits across concurrent sub-agents
  ↓ Anti-recursion: <fork_boilerplate> tag detection prevents sub-agents from forking again
```

Multiple concurrent sub-agents share the vast majority of the context prefix — maximizing API prompt cache reuse and dramatically reducing costs. Structured output format (Scope, Result, Key files, Files changed, Issues) enables the parent to efficiently integrate results.

### Blocked Tool Delegation (Hermes Agent)

`DELEGATE_BLOCKED_TOOLS` explicitly prohibits: recursive delegation, user interaction, writing to shared memory, cross-platform side effects. "Whitelist-open, blacklist-deny" achieves secure isolation in enterprise scenarios.

---

## Tool System Design

### Result Handling

Long tool results (e.g., a database query returning thousands of rows) bloat the context window. Claude Code 2026's approach:

```
Tool returns very long result
  ↓ Exceeds per-message token budget?
  ↓ Yes → save to temp file, return summary + file path
  ↓ Agent reads file on demand for full results
```

### Lazy Loading (ToolSearch)

When tool count grows from ~18 to ~40, loading all tool schemas permanently wastes context. ToolSearch + `defer_loading`:
- Tools are indexed by `searchHint` keywords
- Agent searches for the tool it needs, then loads its schema
- Infrequently used tools never occupy context

### MCP

MCP (Model Context Protocol) is the de facto standard for extending tool surfaces. All major Harnesses except PI Agent support it. Depth varies:
- **Goose**: Rust `rmcp` — full protocol including resources, prompts, sampling
- **Hermes Agent**: supports server-initiated MCP sampling (LLM callbacks)
- **Kimi CLI**: supports MCP OAuth authentication

See [[applications/agentic-patterns#Protocols]] for MCP/A2A protocol details.

---

## Security and Permission Systems

Security depth varies widely across implementations:

```
PI Agent         ████░░░░░░  beforeToolCall hook only
Claude Code '25  ██████░░░░  permission whitelist + command parsing
Kimi CLI         ██████░░░░  approval system + YOLO mode
Hermes Agent     ███████░░░  toolset filtering + prompt injection detection
Claude Code '26  ████████░░  rule engine + Bash classifier
Gemini CLI       ████████░░  Policy Engine + Hook system
Goose            ██████████  5-layer Inspector + LLM adversarial review
```

### Goose Inspector Pipeline

```
Tool request → SecurityInspector (pattern matching)
             → EgressInspector (network egress validation)
             → AdversaryInspector (LLM adversarial review — AI defending against AI)
             → PermissionInspector (permission check)
             → RepetitionInspector (loop detection)
             → approved / needs_approval / denied
```

`AdversaryInspector` uses a second LLM to review whether tool calls exhibit adversarial behavior. `RepetitionInspector` detects identical repeated operations to prevent resource-wasting infinite loops.

### Bash Classifier (Claude Code 2026)

Speculatively classifies Bash commands, auto-approving high-confidence safe commands (`ls`, `cat`). Design principle: **security mechanisms should not become a burden on user experience, otherwise users will choose to bypass them.**

### Gemini CLI Policy Engine

Finest-grained permission configuration: tool name (exact/wildcard/MCP pattern), parameter regex matching, tool annotation matching, sub-agent scope matching. Best for enterprise strict-security scenarios.

### Prompt Injection Detection (Hermes Agent)

The only project with Harness-level prompt injection protection. Scans context files before injection for patterns: "ignore instructions," invisible Unicode, HTML comment injection, curl exfiltration attempts. See [[applications/prompt-injection]] for broader context on injection attacks.

---

## Hook Systems

Hooks enable extensibility and observability without modifying core logic:

| Project | Notable Hook Design |
|---|---|
| Gemini CLI | Most complete: HookSystem + HookRegistry + HookRunner; BeforeModel can block/modify config/inject synthetic responses; AfterModel can modify responses |
| Kimi CLI | Wire subscription protocol — user-configurable hooks |
| Goose | 5 Inspectors in series (security pipeline) |
| PI Agent | Minimalist: 3 hooks only (`beforeToolCall`, `afterToolCall`, `transformContext`); all strategy decisions delegated to app layer |

---

## Error Handling

### Hermes Agent Error Classifier

15 `FailoverReason` types, each with a recovery strategy:

```yaml
ClassifiedError:
  reason: FailoverReason  # auth, billing, rate_limit, overloaded, context_overflow...
  retryable: bool
  should_compress: bool
  should_rotate_credential: bool
  should_fallback: bool
```

Separates "what went wrong" from "how to recover" — better observability and recovery than simple try-catch + retry.

### Standard Patterns

- **Exponential backoff**: used by Claude Code (max 10 retries), Goose, Kimi CLI (tenacity, max 5)
- **Retry-After header**: Claude Code respects API rate-limit headers
- **Model fallback**: Hermes Agent can switch to a cheaper/different model on failure
- **Last chance turn**: Gemini CLI's grace-period mechanism before timeout

---

## Product-Level vs. Framework-Level Design

| Positioning | Projects | Characteristics |
|---|---|---|
| **Product-level** | Claude Code, Goose, Kimi CLI, Gemini CLI, Hermes Agent | Rich built-in tools and strategies; ready out of the box |
| **Framework-level** | PI Agent | 3 core hooks + app-layer everything; maximum flexibility, maximum engineering burden |

PI Agent's "no built-in opinions" design is the right starting point for building lightweight, highly customizable Agent frameworks where the application owns all strategy decisions.

---

## Managed Agents: Agent-as-a-Service

Anthropic's Managed Agents is a hosted agent service built on an OS design principle: virtualize agent components into stable interfaces so implementations can be swapped as models improve. It is a **meta-harness** — opinionated about the interfaces around Claude, not about which harness runs behind them.

See [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]] for full detail.

### The Pet Problem and the Three-Interface Fix

The original single-container design bundled the harness, sandbox, and session together — creating a "pet" container that was fragile, hard to debug, and locked customers into Anthropic's network topology.

The solution decouples three interfaces:

| Interface | Role | Key operations |
|---|---|---|
| **Session** | Append-only durable event log, lives outside the harness | `getSession(id)`, `getEvents()`, `emitEvent(id, event)` |
| **Harness (Brain)** | Stateless orchestration loop; can crash and reboot cleanly | `wake(sessionId)` resumes from last event |
| **Sandbox (Hands)** | Execution environment; provisioned on demand via tool call | `provision({resources})`, `execute(name, input) → string` |

Each component becomes **cattle** — replaceable and independently survivable. A container failure is caught as a tool-call error; the harness provisions a fresh one. A harness crash loses nothing — a new harness wakes from the session log.

### Session as External Context Store

The session log is not Claude's context window — it is the durable ground truth. `getEvents()` supports positional slices:
- Pick up from the last read position
- Rewind to see the lead-up before a specific moment
- Re-read context before a consequential action

Events can be transformed in the harness before passing to Claude (prompt cache optimization, context trimming) without losing recoverability. This solves the core problem with irreversible context decisions (compaction, trimming): the session always has the full record.

### Structural Credential Isolation

In the coupled design, untrusted code ran in the same container as credentials — prompt injection could exfiltrate tokens and spawn unrestricted sessions. The structural fix keeps credentials out of the sandbox entirely:

| Pattern | Mechanism |
|---|---|
| **Auth bundled at init** | e.g., Git: access token clones the repo during sandbox init, wired into local git remote. `push`/`pull` work without the agent ever seeing the token. |
| **Vault + proxy** | MCP tools: OAuth tokens stored in a secure vault. Claude calls a dedicated proxy; the proxy fetches credentials and calls the external service. The harness never sees credentials. |

Narrow-scoping is an insufficient mitigation because it encodes assumptions about what Claude can't do — assumptions that go stale as models improve. Structural isolation remains secure regardless of capability.

### Performance: TTFT Gains from On-Demand Provisioning

Before decoupling, every session paid container setup cost upfront. After: containers provision only when needed via `execute()`. Inference starts as soon as the orchestration layer pulls pending events from the session log.

- **p50 TTFT dropped ~60%**
- **p95 TTFT dropped >90%**

### Many Brains, Many Hands

- **Many brains**: stateless harnesses scale horizontally; customers can run the harness in their own VPC without network peering
- **Many hands**: each sandbox is `execute(name, input) → string` — harness-agnostic as to whether the sandbox is a container, phone, or anything else; brains can reach multiple execution environments simultaneously and pass hands to one another

### Harness Staleness

A concrete example from the article: context-reset logic added for Claude Sonnet 4.5's "context anxiety" (premature task wrap-up near context limit) became dead weight on Claude Opus 4.5. Harness assumptions go stale. Managed Agents pushes assumptions into the swappable harness layer, not into durable infrastructure — matching the OS analogy where `read()` outlasted every disk technology it ever abstracted.

---

## Harness Engineering in Practice (HumanLayer)

See [[summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]] for a practitioner account. Key additions to the standard harness model:

### CLAUDE.md / AGENTS.md: The Cheapest Lever

Markdown files at the repo root, deterministically injected into the system prompt. Best practices distilled from the ETH Zurich study (138 agentfiles tested):

| Finding | Rule |
|---|---|
| LLM-generated files hurt performance (+20% cost) | Write by hand only |
| Human-written helped only ~4% | Every line must earn its place |
| Agents spent 14–22% more tokens on instructions, no improvement | Instruction budget is finite |
| Codebase overviews and directory listings didn't help | Agents discover structure themselves |

**Guidelines:** under 60 lines, universally applicable rules only, no complex conditionals, progressive disclosure rather than front-loaded content.

### The Instruction Budget

Every tool definition, agentfile line, and loaded skill consumes tokens from a finite budget. As the instruction budget shrinks, so does reasoning quality — the agent enters the "dumb zone." Three levers to stay within budget:

1. **Remove irrelevant tool definitions** — disconnect unused MCP servers; prefer CLIs over MCP for tools already well-represented in training data
2. **Progressive disclosure via skills** — load instructions on demand, not upfront
3. **Sub-agent isolation** — keep intermediate tool call noise out of the parent context

### Context-Efficient MCP Tool Wrapping

When only a subset of an MCP server's tools is used, replace it with a custom CLI that exposes only those operations, with example invocations in CLAUDE.md. HumanLayer replaced their Linear MCP server with a 6-command CLI wrapper, saving thousands of tokens per session.

### Sub-Agents as Context Firewalls

**Context rot** (Chroma research, 18 models tested): performance degrades as context length grows — even on simple tasks. When semantic similarity between query and relevant content is low, degradation is steeper. Distractor effects compound.

Sub-agents solve this structurally: each receives a fresh, small, high-relevance context window. Only the condensed result returns to the parent. Design principles:
- Return `filepath:line` citations rather than raw content — parent gets pointers, not noise
- Define scope clearly: what the sub-agent should do AND what it should NOT do
- Use cheaper models (Sonnet/Haiku) for sub-agents; Opus for the parent orchestrator

Good sub-agent tasks: codebase lookups, pattern analysis, request tracing, any research task with a simple answer but many intermediate steps.

### Hooks for Deterministic Control

Hooks add control flow that prompting alone cannot achieve reliably. Key design principle: **success is silent** — nothing enters the agent's context. Only failures produce output; exit code `2` re-engages the agent.

Common uses: auto-approve/deny tool calls based on expressive rules, run typecheck/build on stop and force the agent to fix errors, send Slack/PR notifications on completion.

### Back-Pressure: Verification Mechanisms

Agent success correlates strongly with the agent's ability to verify its own work. High-leverage investments: type checks, builds, unit/integration tests, coverage hooks. All must be context-efficient — swallow stdout on success, surface only errors. Running the full test suite and flooding the context with passing output causes task loss.

### Model Over-Fitting to Harness

Post-trained coding models can be over-fitted to their training harness. Terminal Bench 2.0: Claude Opus 4.6 ranks #33 in Claude Code (its training harness), but rises to #5 in a different harness. Default ≠ optimal.

---

## Agent-First Development: 0 Lines of Manual Code (OpenAI)

See [[summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]] for a case study of building a production product with Codex generating every line. Key lessons for harness design:

### Scale and What Changes

Over 5 months, a team of 3–7 engineers drove ~1,500 PRs (~3.5 PRs/engineer/day) to produce ~1M lines of code — ~10× the speed of hand-coding. As agent throughput increased, the bottleneck became **human QA capacity and environment legibility**, not model capability.

### Repository as System of Record

**Anything the agent can't access in-context effectively doesn't exist.** Knowledge in Slack, Google Docs, or people's heads is illegible to the system. All relevant knowledge must live as versioned, repository-local artifacts.

AGENTS.md (~100 lines) serves as a **table of contents**, not a manual. The actual knowledge lives in a structured `docs/` directory:
- Architecture docs: top-level domain and package-layer map
- Design docs: catalogued with verification status
- Quality grades: tracks coverage gaps by domain
- Plans as first-class artifacts: execution plans with progress/decision logs checked into the repo

**Mechanical freshness enforcement:** linters and CI jobs validate the knowledge base is cross-linked and up to date. A recurring doc-gardening agent opens fix-up PRs for stale documentation.

### Architectural Invariants Over Implementation Opinions

Agents are most effective in environments with strict boundaries and predictable structure. The solution: enforce dependency directions and layer boundaries mechanically (custom linters, structural tests), but leave implementation choices to the agent.

```
Within a domain: Types → Config → Repo → Service → Runtime → UI
Cross-cutting: Providers only
Everything else: mechanically disallowed
```

Error messages in custom lints are written to inject remediation instructions directly into agent context. This is typically architecture for hundreds-of-engineers teams; with agents it becomes an **early prerequisite**.

### Garbage Collection via Recurring Cleanup Agents

Full agent autonomy causes drift: the agent replicates patterns — including bad ones — at scale. Spending 20% of the week on manual cleanup doesn't scale.

**Solution:** encode "golden principles" once, then run background Codex tasks on a regular cadence to scan for deviations, update quality grades, and open targeted refactoring PRs. Most can be automerged in under a minute. Technical debt is paid down continuously rather than compounding.

### Application Legibility: Browser + Observability Access

Making the application itself legible to the agent enables a qualitatively different class of prompts:

| Capability | Method |
|---|---|
| UI validation | Chrome DevTools Protocol wired into agent runtime; DOM snapshots, screenshots, navigation |
| Bug reproduction | Per-worktree app instances; agent drives the UI directly |
| Performance prompts | Ephemeral observability stack per worktree; LogQL and PromQL queries |
| Proof of fix | Agent records videos of failure and resolution |

This enables prompts like "ensure service startup completes in under 800ms" — the agent can measure and verify directly.

### High-Throughput Merge Philosophy

At agent-scale PR volume, conventional blocking merge gates become counterproductive. Corrections are cheap; waiting is expensive. Minimal blocking gates, short-lived PRs, and flake tolerance are the right tradeoffs when throughput far exceeds human attention capacity.
