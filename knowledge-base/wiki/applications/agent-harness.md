# Agent Harness Engineering

**Related:** [[applications/agentic-patterns]] · [[applications/prompt-injection]] · [[applications/guardrails]] · [[inference/prompting-and-reasoning]]  
**Sources:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]]

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

Anthropic's Managed Agents packages a complete Agent as a cloud API service — an upgrade from Claude Code Skills (file-distributed domain prompts + scripts) to Agent-level encapsulation.

Compared to similar platforms (Google AI Studio, Dify, LangSmith Studio), Managed Agents is backed by the mature Claude Code Harness engineering (streaming tool execution, 5-layer compression, Fork SubAgent) plus Anthropic's model-Harness co-optimization expertise.
