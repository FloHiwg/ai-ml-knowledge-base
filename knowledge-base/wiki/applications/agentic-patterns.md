# Agentic Patterns

**Related:** [[applications/rag]] · [[applications/prompt-injection]] · [[inference/prompting-and-reasoning]] · [[concepts/agi-and-intelligence]]  
**Sources:** [[manual/ML AI Engineering Cheat Sheet]] · [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]] · [[summaries/AI Agents from First Principles]] · [[summaries/Prompt injection What's the worst that can happen]] · [[summaries/Teaching Language Models to use Tools]]

---

## What Is an Agent?

An LLM agent is an LLM embedded in a control loop — it can take actions, observe results, and iterate. The model's outputs are not just text but decisions that affect state in external systems.

### The Agent Spectrum (Level 0–3)

Agents exist on a spectrum — the term covers a wide range of systems. All of the following qualify as "agents":

| Level | Description | Key property |
|---|---|---|
| **Level 0** | Standard LLM + optional CoT/reasoning | Relies on parametric knowledge; single-step output |
| **Level 1** | Tool-use LLM | Delegates sub-tasks to external APIs; addresses hallucination and knowledge cutoff |
| **Level 2** | Problem decomposition (ReAct-style) | Sequential, stateful problem solving; introduces control flow to inference |
| **Level 3** | Increasing autonomy | Takes real-world actions; runs asynchronously without human prompting |

The key bottleneck is not capability but **reliability** — sequential agent pipelines fail catastrophically if any step goes wrong. Production agents need more "nines of reliability."

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

**Why tools beat fine-tuning for specific capabilities:** A calculator that is always correct is more reliable than a fine-tuned LLM that is usually correct at arithmetic. Tools address knowledge cutoffs, arithmetic errors, temporal blindness, and hallucination more directly than training.

### Teaching Tool Use: Toolformer

Toolformer (Schick et al. 2023) introduced a self-supervised approach to fine-tune LLMs for tool use without human-annotated data:

1. **Generate candidates**: use the model's in-context learning ability + a few examples per tool to insert candidate API calls into a large text corpus
2. **Filter**: keep only API calls that lower cross-entropy loss on subsequent tokens (i.e., the tool response genuinely helps predict what follows)
3. **Fine-tune** on the filtered dataset using standard next-token prediction

Key finding: **more tool calls ≠ better performance** — the filtering step is essential to calibrate *when* to call tools, not just *how*. Toolformer (6B GPT-J) outperforms GPT-3 (175B) on several factual and math benchmarks while preserving its general LM capability.

**Evolution toward prompt-based tool use:** As instruction following improved, explicit fine-tuning for tool use became unnecessary. GPT-4 plugins require only a textual description + API schema — the model infers when and how to call the tool via in-context learning. This is the approach standardized by MCP.

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

### Human Memory → LLM Mapping

| Human memory | LLM equivalent |
|---|---|
| **Sensory** | Embedding representations of raw inputs |
| **Short-term / Working** | In-context learning — finite, restricted by context window |
| **Long-term** | External vector store with fast retrieval (MIPS) |

Skills (modular capabilities loaded on demand) prevent cluttering the context window with instructions for capabilities that aren't needed for the current task.

### ANN Algorithms for External Memory (MIPS)

External memory retrieval is Maximum Inner-Product Search (MIPS) over embeddings. All practical systems use Approximate Nearest Neighbors (ANN):

| Algorithm | Key idea |
|---|---|
| **LSH** | Hash similar inputs to same buckets |
| **ANNOY** | Random projection trees; binary trees splitting the space |
| **HNSW** | Hierarchical small-world graphs; upper layers = shortcuts, lower = refinement |
| **FAISS** | Vector quantization into clusters; coarse then fine search |
| **ScaNN** | Anisotropic quantization preserving inner-product distance specifically |

HNSW and FAISS are the most widely used in production vector DBs (Weaviate, Chroma, pgvector).

### Reflexion: Self-Improvement via Memory

Reflexion (Shinn & Labash 2023) stores reflection traces in working memory to let agents learn from failures across episodes:
1. Agent acts and receives a binary reward signal
2. Heuristic detects failure: *inefficient planning* (too long, no success) or *hallucination* (identical actions → same observation)
3. LLM generates a reflection from (failed trajectory, ideal reflection) examples
4. Reflection stored in working memory (up to 3 entries) and used as context in next attempt

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

---

## Security: Prompt Injection

The primary security concern for tool-using agents is **prompt injection** — untrusted content (user input, emails, web pages, documents) that contains instructions the LLM follows, overriding the intended system behavior.

Severity scales directly with agent capability:
- **Read-only app** → low risk (attacker tricks output shown to themselves)
- **Agent with tool access** → can exfiltrate data, send emails, run queries on behalf of the user
- **Multi-plugin agent** → cross-plugin chains: Plugin A reads injected content, Plugin B executes the attack

**Indirect prompt injection** (Kai Greshake) is the most insidious variant: injections hidden in content the agent reads as part of normal operation (web pages, emails), not from the user directly. Demonstrated against Bing Chat — a hidden instruction on a webpage gave the agent a "secret agenda."

No 100% reliable defense exists. Practical mitigations:
1. Prompt visibility: show users what's being concatenated before actions are taken
2. Human-in-the-loop confirmation before any consequential action
3. Principle of least privilege: grant only needed tool permissions
4. Developer education: assume prompt injection is possible; design for it

See [[applications/prompt-injection]] for the full reference page.

---

## Fundamental Challenges

Three challenges identified in foundational agent work (Weng 2023) that remain relevant:

1. **Finite context length** — limits history, detailed instructions, and API call context. Vector retrieval helps but lacks the representational power of full attention.
2. **Long-horizon planning** — LLMs struggle to adjust plans on unexpected errors; less robust than humans at trial-and-error over extended tasks.
3. **Natural language interface reliability** — formatting errors, occasional refusal; much agent code centers on parsing model output reliably.

The 2026 architecture (below) progressively addresses these via sandboxes, context engineering, and compaction.

---

## 2026 Architecture: Planner + Execution + Task Agents

As of early 2026, multi-agent systems have converged toward three generalist roles (replacing hand-crafted specialist agents):

| Role | Responsibility |
|---|---|
| **Plan Agent** | Discovery and problem mapping only; produces pointers/definitions for the Execution Agent |
| **Execution Agent** | Receives plan, loads context, writes scripts, self-verifies; domain-agnostic |
| **Task Agent** | Ephemeral sub-agent launched dynamically as a tool call for parallel or isolated sub-operations |

The old "Lead-Specialist" pattern (named domain experts defined by engineers) is being replaced by this generalist loop. Domain logic moves into context engineering, not agent definitions.

### Agent VM Sandboxes

Agents now routinely get an ephemeral VM. This enables the "code-first" paradigm: **solve non-coding problems by writing code** (e.g., analyze a spreadsheet by writing a Python script rather than reading it row-by-row cell-by-cell).

**Standard VM tool set:**

| Tool | Purpose |
|---|---|
| **Bash** | Arbitrary shell execution; standard Unix tools pre-installed |
| **Read/Write/Edit** | File system ops; `replace(in_file, old, new)` edits more reliable than line-based |
| **Glob/Grep/LS** | Token-optimized file exploration |

**Custom tool types:**
- *API tools*: simple CRUD wrappers composed inside agent scripts — expose large surface area without burning context tokens on always-attached definitions
- *Mount tools*: bulk context injection — copy external data sources into VM files (e.g., `mount_salesforce_accounts()` → `./salesforce/accounts/*.json`)

### Context Engineering

Context engineering has become the primary steering mechanism for generic harnesses. Three strategies:

1. **Progressive disclosure** — minimal system prompt; agent accumulates context through tool calls. Tool errors return inline docs. Capability guides live in the file system, read on demand.
2. **Context indirection** — agent acts on context without loading it into the window. Writes grep/awk scripts instead of reading large files. Harness can intercept reads to placeholder paths and populate them just-in-time.
3. **Simplification** — map novel internal systems onto model priors. Wrap graph DBs in `networkx`-compatible interfaces. Auto-convert legacy XML to YAML on read.

### Long-Context Focus Management

Over thousands of tokens, context decay is real. Three techniques maintain coherence:

- **Todos** — persistent task list re-injected at the *end* of context (where the model pays most attention)
- **Reminders** — harness appends hints to tool results based on heuristics (n tool calls since last reminder, keyword in prompt)
- **Automated compaction** — when context fills, a separate LLM call summarizes history and reboots the agent from that summary; works best with plan checkpoints
