# Building Multi-Agent Systems (Part 3) - by Shrivu Shankar

**Source:** [[raw/articles/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]]
**Author:** Shrivu Shankar
**Related:** [[summaries/Andrej Karpathy — AGI is still a decade away]] · [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

As of January 2026, multi-agent architecture has converged toward a single dominant pattern: a Planner + Execution Agent loop, with dynamically spawned Task Agents, all grounded in an ephemeral VM sandbox. The most effective agents solve *non-coding* problems by writing code. Bespoke, domain-specific harnesses are giving way to domain-agnostic implementations (e.g., the Agents SDK / Claude Code), with specialization pushed into context engineering rather than hardcoded architecture.

---

## What Has Changed (vs. Prior Phases)

| Phase | Architecture style | Key shift |
|---|---|---|
| Dec 2024 (Part 1) | Domain-specific multi-agent assemblies | Hand-crafted specialist subagents; fragile chains |
| Jul 2025 (Part 2) | Orchestrator + worker; scripting emerging | "Lead-Specialist" pattern; first scripting signs |
| Jan 2026 (Part 3) | Planner + Execution + Task agents; sandbox default | Code-first; domain-agnostic harness; context engineering |

**What stayed the same:** tool-use LLMs, multi-agent decomposition for complexity, long-horizon task execution.

**What changed:**
- **Context engineering** replaces prompt/tool/harness engineering as the primary steering mechanism
- **Sandboxes (VM) are now the default** — agents need a safe environment to execute dynamically generated code
- **Programmatic tool calling** — agents write scripts that call tools in loops/batches, rather than making individual API calls
- **Domain-agnostic harnesses** — wrapping a generic implementation (Agents SDK) beats maintaining custom loops for 90% of use cases

---

## The Three-Agent Architecture

Modern multi-agent systems converge to three roles, with no manual domain-boundary definitions:

### Plan Agent
- Tasked with discovery, planning, and process optimization only
- Performs just enough research to produce a problem map with specific pointers/definitions
- Hands off to the Execution Agent with clear context pointers

### Execution Agent
- Receives the plan and *builds* the solution
- Loads context from planner-provided pointers, writes scripts to manipulate that context, and self-verifies
- Does not require domain-specific configuration — generalist by design

### Task Agent
- Transient sub-agent invoked dynamically by Planner or Execution Agent
- Handles parallel or isolated sub-operations (e.g., "explorer" for the planner, "do operation on chunk X/10" for execution)
- Launched as a tool call with a dynamically generated subtask prompt — ephemeral by design

This replaces the older "Lead-Specialist" pattern where engineers manually defined domain boundaries for every subagent.

---

## Agent VMs (Sandbox Environment)

Agents receive an ephemeral VM to manage file-system context and execute dynamically generated code.

### Core VM Tools (standard across SDKs)

| Tool | Purpose |
|---|---|
| **Bash** | Run arbitrary shell commands; assumes standard Unix tools pre-installed (python3, find, etc.) |
| **Read/Write/Edit** | File system operations; Edit via `replace(in_file, old, new)` format is more reliable than line-based edits |
| **Glob/Grep/LS** | File system exploration; token-optimized aliases for common operations; cross-platform compatibility |

Implementation notes: handle bash timeouts, truncate large reads before they fill the context window, guard against unintentional file edits.

### Custom Tool Types

**API Tools** — programmatic tool calling design:
- Simple REST-style wrappers for CRUD operations on a data source (e.g., `read_item(id)`)
- Agent composes them inside scripts → large surface area exposed without burning context tokens on always-attached definitions
- Solves the "MCP assumes tools handle retrieval" problem

**Mount Tools** — bulk context injection:
- Copy and transform an external data source into files in the VM (e.g., `mount_salesforce_accounts()` writes JSON/Markdown to `./salesforce/accounts/`)
- Agent works with files directly; never needs to page through API responses one-by-one

### Script-Friendly Capabilities

Because the agent can write code, you provide primitives rather than purpose-built tools:
- Build PowerPoint/PDFs via Python libraries (`python-pptx`), then lint programmatically
- Give raw binaries (PDFs, images) + pre-installed libraries (`pdf-decode`, OCR); agent extracts what it needs
- Represent complex objects as searchable text files (e.g., GitHub PR as `./pr/<id>/change.patch` + `./pr/<id>/metadata.json`)
- Use a "fake" git repo in the VM to simulate draft/publish workflows
- Seed the VM with reusable Bash/Python script templates — a dynamic runtime skill library

---

## Context Engineering

Context engineering is the new primary lever for adapting a generic harness to a specific product domain. Three strategies:

### 1. Progressive Disclosure
Start with a minimal system prompt; the agent accumulates information only as needed via tool calls.
- Tool outputs include just-in-time usage docs when the agent fails
- README.md in the VM root lists capabilities; specific guides (e.g., `docs/database_guide.md`) are read on demand

### 2. Context Indirection
The agent acts on context *without loading it into the context window*:
- Agent writes a `grep`/`awk` script to find relevant lines in a 500 MB log rather than reading the whole file
- "Blind reads": harness intercepts reads to placeholder paths (`./articles/<topic>.txt`), performs a search, and populates the file just-in-time

### 3. Simplification (Exploit Model Priors)
Reduce novel context by mapping internal concepts onto things the model already knows:
- Wrap a complex internal graph DB in a `networkx`-compatible interface — zero-shot performance is far higher
- Auto-convert legacy XML/custom configs to YAML/JSON on read; convert back on save

---

## Managing Long-Running Tasks: TODOs, Reminders, Compaction

Context decay is real over thousands of tokens. Three techniques maintain focus:

**Todos** — persistent task list (often seeded by the planner). Primary function: re-inject remaining goals at the *end* of the context window where the model pays most attention.

**Reminders** — harness injects context dynamically at the end of tool results or user messages, triggered by heuristics (e.g., "10 tool calls since last reminder about X" or "prompt contains keyword Y").

**Automated Compaction** — when context window fills, a separate LLM call summarizes the history and "reboots" the agent from that summary. Works better when tied to explicit checkpoints in the input plan.

---

## Agent Architecture Health Check

Signs your agent needs a refactor:

| Symptom | Fix |
|---|---|
| Custom domain-specific harness hardcoded to your product | Refactor to domain-agnostic harness; delegate domain logic to context + tools |
| Prompts cluttered with verbose tool definitions and subagent instructions | Move logic into "Skills" (markdown guides) the agent discovers progressively |
| Sprawling library of specific tools (`resize_image`, `convert_csv`, `filter_logs`) | Delete them — if the agent has a sandbox, it can write scripts instead |

---

## Open Questions (as of Jan 2026)

- **Sandbox security**: Arbitrary code execution + internet access + sensitive data = unsolved exfiltration/destruction risks
- **Cost of autonomy**: VM runtime + thousands of tool loops cost more than inference alone; is the saved human time worth it?
- **Lifespan of context engineering**: Will models + cheap context windows make filesystem organization obsolete in 6 months?

---

## Key Takeaways

- The 2026 agentic meta: Planner + Execution Agent + ephemeral Task Agents, all in a VM sandbox
- Solve non-coding problems by writing code — sandboxes are no longer optional
- Three agent roles replace the zoo of named specialists; generalist harnesses beat bespoke ones for 90% of use cases
- Tool design splits into API tools (programmatic composition) and Mount tools (bulk file injection)
- Context engineering — progressive disclosure, indirection, simplification — is the new primary steering mechanism
- TODOs, reminders, and compaction are the three pillars of long-context focus management
- If your agent was built before mid-2025, it's probably due for a rewrite, not a retrofit
