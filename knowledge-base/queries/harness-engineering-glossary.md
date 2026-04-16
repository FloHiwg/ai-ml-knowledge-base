# Harness Engineering: Key Concepts and Definitions

**Query:** What are all the concepts and ideas related to harness engineering, with short definitions?

---

## Answer

Coverage is spread across several articles. The primary sources are:

- **Primary source:** [[../summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]]
- **Primary source:** [[../summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]]
- **Also covers:** [[../summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]]
- **Also covers:** [[../summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]]
- **Also covers:** [[../summaries/AINews Is Harness Engineering real - Latent.Space]]

---

## Core Harness Concepts

| Concept | Definition |
|---|---|
| **Agent Harness** | All engineering infrastructure surrounding the LLM: orchestration loop, tool system, context management, sub-agent architecture, permissions, and error handling. If the model is the engine, the harness is the chassis and drivetrain. |
| **Big Model vs. Big Harness Debate** | Industry debate over the durability of harness engineering. "Big Model" view: harnesses are temporary scaffolding made obsolete by better models. "Big Harness" view: the harness is the core product and optimizing it provides durable value by fully expressing the model's capabilities. |
| **Instruction Budget** | The finite token allocation available for instructions (tool definitions, agentfile rules, system prompt). When the budget shrinks too far, reasoning quality degrades — the agent enters the "dumb zone." |

---

## Orchestration and Execution

| Concept | Definition |
|---|---|
| **ReAct Loop** | The core orchestration heartbeat: LLM call → tool execution → result feedback → repeat. |
| **Streaming Tool Execution** | Latency optimization where a tool begins executing the moment its parameters are parsed from the LLM's streaming output, without waiting for the full response to complete. |
| **Lazy Loading (ToolSearch)** | Context-saving technique where the agent searches a tool index by keyword and only loads a tool's full schema into context when it actually needs to use it. |
| **Hook Systems** | Mechanisms that intercept the agent's process before or after LLM calls and tool executions, adding control flow, observability, and extensibility without modifying core logic. |

---

## Context and Memory Management

| Concept | Definition |
|---|---|
| **Context Compression** | Strategies for preventing long-running agents from exhausting their context window, including "read-time projection" (Context Collapse) — dynamically generating compressed views of history without modifying original messages. |
| **D-Mail Time Travel** | Context management approach for exploratory tasks where the agent rolls its context back to a previous checkpoint, discarding dead-end paths and preventing failed attempts from contaminating future reasoning. |
| **Context Firewalls** | Using sub-agents to combat context rot: the sub-agent receives a fresh, highly relevant context window and returns only concise pointers (e.g. file citations) to the parent, keeping the parent's context clean. |

---

## Sub-Agent Architectures

| Concept | Definition |
|---|---|
| **Independent Context Sub-Agents** | Sub-agents that start completely fresh with their own isolated message history. Clean context, but cannot reuse the parent's prompt cache. |
| **Fork Sub-Agents** | Sub-agents that fork directly from the parent's context, sharing the full context prefix. Maximizes prompt cache reuse and significantly reduces API costs for concurrent sub-agents. |
| **Blocked Tool Delegation** | Explicit security constraints on sub-agents (whitelist-open, blacklist-deny) that prohibit risky actions such as recursive delegation or writing to shared memory. |

---

## Security and Infrastructure

| Concept | Definition |
|---|---|
| **MCP (Model Context Protocol)** | Standard protocol for integrating external tool surfaces, resources, and prompts across platforms. |
| **Meta-Harness / Managed Agents** | "OS-style" architecture that virtualizes agent components into three decoupled interfaces — Session, Harness/Brain, Sandbox/Hands — so implementations can be independently swapped or rebooted. |
| **The Pet Problem vs. Cattle Sandboxes** | Critique of bundled harness/sandbox/session designs ("pets") that are fragile and hard to recover. Decoupled designs make the execution environment ("hands") disposable and replaceable ("cattle"). |
| **Structural Credential Isolation** | Security pattern that keeps auth credentials out of the execution sandbox entirely via a vault and proxy. Ensures a prompt-injected agent cannot exfiltrate the underlying credentials. |

---

## Agent-First Development

| Concept | Definition |
|---|---|
| **Repository as System of Record** | Principle that anything an agent cannot access in-context (knowledge in Slack, Google Docs, etc.) effectively doesn't exist. All knowledge must be stored as versioned, repository-local artifacts. |
| **Garbage Collection Agents** | Recurring background agents that combat drift in autonomous systems by scanning for deviations, updating quality grades, and opening automated refactoring PRs to pay down technical debt. |

---

## Relevant Wiki Coverage

- [[../wiki/applications/agent-harness]] — Full reference page covering orchestration, tool systems, context management, sub-agent architectures, security patterns, and agent-first development
- [[../wiki/applications/agentic-patterns]] — Higher-level agentic patterns including MCP, memory, and tool use
- [[../wiki/applications/prompt-injection]] — Prompt injection attacks and the architectural defenses (including structural credential isolation)
