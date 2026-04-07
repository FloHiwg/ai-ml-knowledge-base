# Agentic Patterns

**Related:** [[applications/rag]] · [[inference/prompting-and-reasoning]]  
**Sources:** [[manual/ML AI Engineering Cheat Sheet]]

---

## What Is an Agent?

An LLM agent is an LLM embedded in a control loop — it can take actions, observe results, and iterate. The model's outputs are not just text but decisions that affect state in external systems.

---

## Core Agentic Patterns

### Prompt Chaining

Break a complex task into sequential steps. Each step's output becomes the next step's input. Reduces hallucination and improves reliability by keeping each LLM call focused.

```
Step 1: Research → Step 2: Outline → Step 3: Draft → Step 4: Review
```

### Routing

Classify an input and direct it to the right handler:
- **LLM-based routing:** Use a small LLM to classify intent
- **Embedding-based routing:** Cosine similarity to known task descriptions
- **Rule-based routing:** Pattern matching
- **ML model routing:** Trained classifier

### Parallelization

Launch multiple agents simultaneously (like threading), collect and merge results. Improves throughput and reduces latency for independent subtasks.

### Reflection

```
Execute → Critique → Reflect → Iterate
```

Separate the concerns of execution and evaluation. A critic agent reviews the output of an actor agent and provides feedback for revision. Substantially improves output quality on complex tasks.

### Tool Use

LLMs can call external tools — search engines, APIs, code interpreters, databases. When the LLM needs information or capabilities beyond its internal knowledge, tools extend its reach.

**Process:**
1. Tool definitions provided in system prompt
2. LLM decides to call a tool and generates a function call
3. Tool executes (third-party service or local function)
4. Output returned to LLM as context
5. LLM generates final response

### Planning

For requests too complex for a single action: generate a plan first, then execute step by step. A todo list or scratchpad helps maintain state across steps. Prompting the model to plan before acting triggers an internal reasoning phase.

### Multi-Agent Collaboration

Multiple specialized agents working together:

**Interaction patterns:**
- Sequential handoff — agent A passes result to agent B
- Parallel processing — multiple agents on independent subtasks
- Debate and consensus — different agents provide viewpoints, one synthesizes
- Hierarchical — supervisor coordinates and delegates
- Expert team — collaboration of specialists
- Critic-reviewer — one group produces, another critiques

**Communication structures:**
- Network — every agent can communicate with every other
- Supervisor (star) — one orchestrator coordinates
- Hierarchical — multi-layer supervision

---

## Memory

| Type | Scope | Implementation |
|---|---|---|
| **Short-term** | Within a session | Context window |
| **Long-term** | Across sessions | External memory bank (vector DB, etc.) |

Skills (modular capabilities loaded on demand) prevent cluttering the context window with instructions for capabilities that aren't needed for the current task.

---

## Protocols

### MCP — Model Context Protocol

Standardizes how models interact with tools and external resources. Key concepts:
- **Tools** — callable methods
- **Resources** — shared state referenced in prompts
- **Prompt templates** — reusable prompt structures
- **Catalog** — list of tools with descriptions and parameter schemas

Especially valuable when tools come from different teams or third-party providers.

### A2A — Agent-to-Agent Protocol

Defines how agents discover and communicate with each other.

**Core actors:** User → A2A Client → A2A Server (agent)

**Agent Card:** JSON description of the agent (authentication, capabilities, skills). Enables:
- **Registry-based discovery** — agents list themselves in shared registries
- **Well-known endpoints** — standard URL for fetching the agent card
- **Direct configuration** — for closed/private systems

**Communication:** Asynchronous tasks using JSON-RPC 2.0. Interaction modes: request/response (polling) or SSE (streaming). TLS by design for secure inter-agent communication.

---

## Human-in-the-Loop

A human reviews intermediate or final results at defined checkpoints — either at fixed points in the pipeline or on-demand when the model flags uncertainty. Necessary for high-stakes decisions, irreversible actions, or tasks requiring external execution.

---

## Failure Handling

- **Exception detection:** Monitor for errors and log them
- **Retries with backoff:** Retry transient failures
- **State recovery:** Return to a clean, uncorrupted state after failure
- **Goal monitoring:** Let the agent evaluate its own output against SMART objectives (specific, measurable, achievable, relevant, time-bound)
