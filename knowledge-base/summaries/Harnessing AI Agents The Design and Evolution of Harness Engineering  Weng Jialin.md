# Harnessing AI Agents: The Design and Evolution of Harness Engineering — Weng Jialin

**Source:** [[raw/articles/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]]  
**Author:** Weng Jialin  
**Related:** [[summaries/AI Agents from First Principles]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]] · [[wiki/applications/agentic-patterns]] · [[wiki/applications/agent-harness]]

---

## Core Idea

**Agent = Model + Harness.** The model is the engine; the Harness is everything else — the orchestration loop, tool system, context management, sub-agent infrastructure, permissions, and error handling. Prompted by two source code leaks of Claude Code (April 2025, March 2026), the author conducts a horizontal analysis of seven open-source/leaked AI Agent projects to extract common patterns, differentiated designs, and enterprise-relevant innovations. A key finding: as models get stronger, Harness engineering shifts from capability-building to efficiency optimization — there is effective bidirectional feedback between model training and Harness design.

---

## The Seven Projects Analyzed

| Project | Language | Positioning | Model |
|---|---|---|---|
| Claude Code (2025.04) | TypeScript | Anthropic's official CLI Agent | Claude series |
| Claude Code (2026.03) | TypeScript | Evolved Claude Code | Claude series |
| Goose | Rust | Block's open-source CLI Agent | Multi-model |
| Kimi CLI | Python | Moonshot AI's official CLI Agent | Kimi series |
| Gemini CLI | TypeScript | Google's official CLI Agent | Gemini series |
| Hermes Agent | Python | NousResearch multi-platform Agent | Multi-model |
| PI Agent | TypeScript | Lightweight Agent framework | Multi-model |

---

## Harness Capability Dimensions

A mature Agent Harness covers nine dimensions:

| Capability Dimension | Description |
|---|---|
| **Main Loop (ReAct Loop)** | LLM call → tool execution → result feedback — the core orchestration heartbeat |
| **System Prompt** | Instruction assembly and dynamic injection to guide model behavior |
| **Tool System** | Tool definition, registration, execution, permission control |
| **Sub-Agent** | Task delegation, context isolation, parallel execution |
| **Context Management** | Token budget, automatic compression, summary generation |
| **Middleware / Hooks** | Interception and processing before/after LLM and tool calls |
| **Memory / State** | Session persistence, cross-session memory |
| **Permission System** | Approval and security control for tool execution |
| **Error Handling** | Retry, fallback, context overflow recovery |

---

## Main Loop (ReAct Loop) Comparison

All projects implement the ReAct (Reasoning + Acting) loop, but orchestration details vary substantially:

| Project | Loop Pattern | Tool Concurrency | Streaming Execution |
|---|---|---|---|
| Claude Code (2025) | Recursive calls | Read-only concurrent (max 10), write serial | No |
| Claude Code (2026) | while loop + state machine | Read/write partitioned (max 10) | **Yes** |
| Goose | while loop (max 1000 turns) | `select_all` parallel | Yes |
| Kimi CLI | while True + step iteration | Sequential only | No |
| Gemini CLI | while loop (max 30 turns, 10min timeout) | Via Scheduler | Yes |
| Hermes Agent | for turn in max_turns | Thread pool (128 workers) | No |
| PI Agent | Outer loop + inner tool loop | Parallel/serial modes | Yes |

**Most significant evolution — Claude Code 2025 → 2026:**

```
2025: Complete LLM response → parse tool_use → execute tools → recursive call
2026: Streaming LLM response → parse while streaming → execute while parsing → state machine drives next round
```

The **StreamingToolExecutor** starts executing tools as soon as their parameters are parsed in the stream — reducing end-to-end latency dramatically for multi-tool calls. Goose's Rust async + Tokio `select_all` achieves true parallel execution with `CancellationToken` for graceful cancellation.

---

## System Prompt Design

| Project | Assembly Method | Prompt Cache | Special Design |
|---|---|---|---|
| Claude Code (2025) | Multi-segment + `<context>` tags | Ephemeral cache control | Separate agent/main prompt sets |
| Claude Code (2026) | **Section registry + caching** | Fork sub-agents share rendered bytes | `systemPromptSection()` on-demand compute + cache |
| Goose | Jinja2 templates + Builder | None | Template variable injection |
| Kimi CLI | Jinja2 templates + substitution | Persisted after first run | Sub-agents reuse persisted prompts |
| Gemini CLI | Modular Builder | None | `renderFinalShell()` wrapper |
| Hermes Agent | 8-layer pipeline assembly | Via session ID | **Prompt injection detection** |
| PI Agent | Raw strings | Via provider session | Fully delegated to app layer |

**Claude Code (2026) section registry**: registers cacheable sections via `systemPromptSection(name, compute)` — each part independently updated and cached, avoiding unnecessary cache invalidation. Fork sub-agents receive the parent's rendered system prompt bytes directly, maximizing cache reuse and reducing sub-agent API costs.

**Hermes Agent** is the only project with Harness-level prompt injection protection — scans context files for patterns such as "ignore instructions," invisible Unicode characters, HTML comment injection, and curl exfiltration attempts.

---

## Tool System

| Project | Tool Count | MCP Support | Tool Result Handling | Lazy Loading |
|---|---|---|---|---|
| Claude Code (2025) | ~18 | Yes | Direct return | No |
| Claude Code (2026) | ~40 | Yes | **Large results → disk + on-demand read** | **Yes (ToolSearch)** |
| Goose | ~20+ | Yes (rmcp) | Large response handling | No |
| Kimi CLI | ~15 + MCP | Yes (fastmcp) | Direct return | MCP tools lazy-loaded |
| Gemini CLI | ~18 + MCP | Yes | Large output truncated + saved to file | Wildcard matching |
| Hermes Agent | ~40+ | Yes (self-impl) | `max_result_size_chars` limit | No |
| PI Agent | App-layer defined | No | Structured `details` data | No |

**Claude Code (2026) tool result optimization:**
```
Tool returns very long result
  ↓ Exceeds per-message token budget?
  ↓ Yes → save to temp file, return summary + file path
  ↓ Agent reads file on demand for full results
```

**ToolSearch + defer_loading**: Tools are indexed by `searchHint` keywords; infrequently used tools are lazy-loaded on demand. Critical when tool count grows from 18 to 40 — prevents schema bloat in context.

**MCP de facto standard**: All except PI Agent support MCP. Goose uses Rust `rmcp` for full protocol (resources, prompts, sampling); Hermes supports server-initiated MCP sampling; Kimi CLI supports MCP OAuth.

---

## Sub-Agent Design

| Project | Model | Context Isolation | Parallel | Recursion Depth |
|---|---|---|---|---|
| Claude Code (2025) | SubAgent as a Tool | Independent message history | No | Unlimited |
| Claude Code (2026) | **Fork SubAgent** | Shared parent context + isolated execution | **Yes** | Anti-recursive fork |
| Goose | `summon` tool | Independent session | No | Non-recursive |
| Kimi CLI | Agent tool + background tasks | Persisted state + independent context | Via background tasks | Not limited |
| Gemini CLI | `LocalSubagentInvocation` | Independent Registry | Yes | Supported |
| Hermes Agent | `delegate_tool` | Fully isolated | Max 3 concurrent | MAX_DEPTH=2 |
| PI Agent | No built-in | — | — | — |

**Claude Code (2026) Fork SubAgent — key architectural innovation:**

```
Parent agent's assistant message (multiple tool_use)
  ↓ Build fork child messages:
  [Full history, assistant(all tool_use), user(placeholder results + subtask instructions)]
  ↓ Only the last text block differs → maximize prompt cache hits
  ↓ Anti-recursion: <fork_boilerplate> tag detection prevents sub-agents from forking again
```

Multiple concurrent sub-agents share the vast majority of context prefix — only task instructions differ at the end. Maximizes API prompt cache utilization, dramatically reducing sub-agent costs.

**Hermes Agent `delegate_tool`** uses `DELEGATE_BLOCKED_TOOLS` — explicitly prohibiting recursive delegation, user interaction, writing to shared memory, and cross-platform side effects. "Whitelist-open, blacklist-deny" provides secure isolation for enterprise use.

---

## Context Management

| Project | Auto Compression | Strategy | Trigger | Special |
|---|---|---|---|---|
| Claude Code (2025) | No (manual `/compact`) | LLM summary | User-triggered | Prompt caching |
| Claude Code (2026) | **Yes (5 layers)** | Multi-layer progressive | Token threshold + API error | **Circuit breaker** |
| Goose | Yes | LLM summary + tool-pair batches | 80% context | Continuation messages |
| Kimi CLI | Yes | LLM summary + checkpoint | Ratio threshold | **D-Mail time travel** |
| Gemini CLI | Yes | Reverse token budget + truncation | 50% model limit | Large output → file |
| Hermes Agent | Yes | Structured LLM summary | 50% context window | Cheaper model for summaries |
| PI Agent | No (via hook) | App-layer | App decision | `transformContext` hook |

**Claude Code (2026) 5-layer context compression:**
```
1. Snip (HISTORY_SNIP)       — delete old messages, preserve protected tail
2. Microcompact               — deduplicate cached tool results by tool_use_id
3. Autocompact                — LLM summary; circuit breaker stops after 3 consecutive failures
4. Reactive Compact           — responds to API prompt-too-long errors; emergency compression + retry
5. Context Collapse           — message groups → summaries; read-time projection (doesn't modify originals)
```
Circuit breaker prevents infinite loops from compression failures. Context Collapse's read-time projection preserves backtrack possibility.

**Kimi CLI D-Mail (time travel)**: Creates checkpoints at each step; `SendDMail` tool rolls back context to a prior checkpoint — ideal for exploratory tasks where a dead-end path should be discarded without forward contamination.

**Hermes Agent structured summaries**: Summaries are structured (Goal, Progress, Decisions, Files, Next Steps) and iteratively updated — preserving core information across multiple compression cycles.

---

## Middleware, Hooks, and Permissions

### Hook Systems

| Project | Tool Hooks | LLM Hooks | User Configurable |
|---|---|---|---|
| Claude Code (2025) | Permission checks, input validation | Binary feedback | No |
| Claude Code (2026) | Pre/Post ToolUse + Failure | Post-Sampling + Stop Hooks | Partial |
| Goose | **5 Inspectors in series** | No | No |
| Kimi CLI | PreToolUse/PostToolUse/Failure | Notification | **Yes (Wire)** |
| Gemini CLI | BeforeToolSelection | BeforeModel/AfterModel/PreCompress | **Yes** |
| Hermes Agent | tool_progress/start/complete | thinking/stream_delta | Via plugins |
| PI Agent | beforeToolCall/afterToolCall | None | Yes |

**Goose Inspector pipeline** (security-oriented):
```
Tool request → SecurityInspector (pattern matching)
             → EgressInspector (network egress validation)
             → AdversaryInspector (LLM adversarial review)
             → PermissionInspector (permission check)
             → RepetitionInspector (loop detection)
             → approved / needs_approval / denied
```
`AdversaryInspector` uses a second LLM to review tool calls for adversarial behavior. `RepetitionInspector` detects repeated identical operations (prevents infinite loops).

### Permission Systems

| Project | Model | Special Design |
|---|---|---|
| Claude Code (2026) | Rule engine + classifier | **Bash command speculative classification, safe commands auto-approved** |
| Goose | GooseMode tiers (Auto/SmartApprove/Approve/Chat) | SmartApprove uses LLM to judge read-only vs. side-effect operations |
| Gemini CLI | Policy Engine | Tool name wildcards + parameter regex + annotation matching + sub-agent scope |
| Kimi CLI | ApprovalState | YOLO mode + unified approval runtime |

**Claude Code (2026) BASH_CLASSIFIER**: speculatively classifies Bash commands, auto-approves high-confidence safe commands (`ls`, `cat`), reducing user friction. Principle: security mechanisms should not become a burden on user experience.

**Gemini CLI Policy Engine**: finest-grained permission config — tool name (exact/wildcard/MCP pattern), parameter regex, annotation matching, sub-agent scope. Best for enterprise strict-security scenarios.

---

## Error Handling

| Project | Retry Strategy | Context Overflow Recovery | Special |
|---|---|---|---|
| Claude Code (2025) | Exponential backoff (max 10) | Error message prompt | Retry-After header |
| Claude Code (2026) | Same | **Reactive Compact + auto compression** | **Circuit breaker** |
| Goose | Exponential backoff | Auto compression (max 2) | Credits exhausted URL |
| Kimi CLI | tenacity exponential backoff (max 5) | Auto compression + connection recovery | **D-Mail rollback** |
| Gemini CLI | Timeout + grace period (60s) | Compression | Last chance turn |
| Hermes Agent | **Error classifier** | Compression + model fallback | **15 error types + recovery strategies** |
| PI Agent | App layer | App layer | Errors as stream events |

**Hermes Agent error classifier** — 15 `FailoverReason` types:
```yaml
ClassifiedError:
  reason: FailoverReason  # auth, billing, rate_limit, overloaded, context_overflow...
  retryable: bool
  should_compress: bool
  should_rotate_credential: bool
  should_fallback: bool
```
Separates "what went wrong" from "how to recover" — better observability and recovery than simple try-catch + retry.

---

## Model–Harness Co-Evolution

The Claude Code 2025 → 2026 evolution shows the bidirectional feedback pattern:

| Dimension | 2025 | 2026 | Direction |
|---|---|---|---|
| Main loop | Recursive async generator | State machine + while loop | More controllable |
| Tool execution | Execute after complete response | **Streaming execute-while-receiving** | Lower latency |
| Context compression | Manual `/compact` | **5-layer auto compression** | More reliable |
| Sub-agent | AgentTool (independent context) | **Fork SubAgent (shared cache)** | Lower cost |
| Tool results | Direct return | **Large results to disk + on-demand** | More context-efficient |
| Tool loading | Full loading | **Lazy loading + ToolSearch** | More context-efficient |
| Permissions | Simple whitelist | **Rule engine + Bash classifier** | Less intrusive |

As models grow stronger, prompts become simpler, and engineering focus shifts toward efficiency (cache, concurrency, compression granularity).

---

## Managed Agents: Next Distribution Paradigm

Anthropic's Claude Managed Agents packages a complete Agent as a cloud service exposed via API — an upgrade from Claude Code Skills (domain prompts + scripts in file form) to true Agent-level encapsulation.

Comparison:
- **Google AI Studio**: custom agents confined to its platform; no API-level flexibility
- **Dify Agent mode**: similar concept but less refined customization; no optimized Harness
- **LangSmith Studio**: closest equivalent — both elevate agent deployment to platform-level service

Key advantage: backed by mature Claude Code Harness engineering (streaming execution, 5-layer compression, Fork SubAgent) and Anthropic's model-Harness co-optimization expertise.

---

## Security Depth Ranking

```
PI Agent         ████░░░░░░  (beforeToolCall hook)
Claude Code '25  ██████░░░░  (permission whitelist + command parsing)
Kimi CLI         ██████░░░░  (approval system + YOLO mode)
Hermes Agent     ███████░░░  (toolset filtering + prompt injection detection)
Claude Code '26  ████████░░  (rule engine + Bash classifier)
Gemini CLI       ████████░░  (Policy Engine + Hook system)
Goose            ██████████  (5-layer Inspector + LLM adversarial review)
```

---

## Key Takeaways

- **Harness is half the agent**: model capability alone doesn't determine agent effectiveness — the orchestration, tool, context, and security infrastructure matter equally
- **ReAct loop is universal**: every project follows LLM → tool → result → next round; streaming execution (Claude Code 2026, Goose, Gemini CLI) reduces latency significantly
- **Streaming tool execution** (Claude Code 2026) is a major latency innovation: tools start executing during LLM streaming output, not after full response
- **Fork SubAgent** (Claude Code 2026) maximizes prompt cache reuse across concurrent sub-agents by sharing the context prefix — dramatically reducing API costs
- **5-layer context compression** (Claude Code 2026) is the most mature production strategy: lightweight to heavyweight, routine to emergency, with circuit breaker to prevent infinite loops
- **MCP is de facto standard**: all projects except PI Agent support it; only depth of implementation varies
- **Security depth varies widely**: Goose's 5-layer Inspector (including LLM adversarial review) sets the benchmark; Hermes Agent's prompt injection detection fills a gap no other project addresses at Harness level
- **D-Mail time travel** (Kimi CLI) is a unique innovation for exploratory tasks: checkpoint rollback avoids forward-contamination from failed approaches
- **Managed Agents** represent the next distribution paradigm: Agent-as-a-service via API, backed by mature Harness engineering
