# Design Patterns for Securing LLM Agents against Prompt Injections

**Source:** [[raw/articles/Design Patterns for Securing LLM Agents against Prompt Injections]]
**Author:** Simon Willison's commentary on the paper by Beurer-Kellner et al. (2025), from IBM, Invariant Labs, ETH Zurich, Google, Microsoft
**Related:** [[summaries/Prompt injection What's the worst that can happen]] · [[summaries/AI Agents from First Principles]] · [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]]

---

## Core Idea

General-purpose LLM agents cannot provide meaningful security guarantees against prompt injection as long as they are built on current language models. The productive question is not "how do we solve prompt injection" but "what kinds of constrained agents can we build today that do useful work while resisting injection?" The paper proposes six design patterns that trade agent capability for security — each pattern imposes intentional constraints that make it structurally impossible for injected content to trigger harmful actions.

---

## The Foundational Principle

> "Once an LLM agent has ingested untrusted input, it must be constrained so that it is *impossible* for that input to trigger any consequential actions."

The paper frames prompt injection as a **taint propagation problem**: any agent exposure to potentially malicious tokens taints that entire execution context. An attacker who can inject tokens gains effective control over both text output and all subsequent tool calls. This means:

- Restricted agents must not invoke tools that can break system integrity or confidentiality
- Agent outputs must not pose downstream risks (data exfiltration, manipulation of future agent behavior)

---

## The Six Design Patterns

### 1. Action-Selector Pattern

**Constraint:** The agent can trigger external actions but **cannot receive or act on any feedback** from those actions.

Operates as an "LLM-modulated switch statement": user input → LLM selects an action from a fixed set → action fires → execution stops. No content flows back into the LLM context.

- **Security:** Immune to injection via tool responses (there are none)
- **Trade-off:** Very limited — cannot perform tasks requiring iterative reasoning over retrieved content
- **Use cases:** Simple routing, navigation triggers, display commands

### 2. Plan-Then-Execute Pattern

**Constraint:** All tool calls are planned **before** any exposure to untrusted content. Tool outputs can flow back in, but cannot influence which actions are taken.

Example: "Send today's schedule to John Doe" → planning phase generates `calendar.read()` then `email.write(..., john.doe@company.com)` with a fixed recipient. The calendar output (which could be malicious) can only corrupt the email *body*, not the recipient or the sequence of actions.

- **Security:** Injection can corrupt content within planned actions, but cannot add or change the actions themselves
- **Trade-off:** Cannot react to retrieved data to make new planning decisions
- **Use cases:** Multi-step workflows with predetermined structure

### 3. LLM Map-Reduce Pattern

**Constraint:** A coordinator never sees untrusted content directly. Sub-agents are exposed to untrusted content but return only **constrained outputs** (e.g., boolean, structured label) that are safely aggregated.

Example: find invoices matching criteria → each file processed by a quarantined sub-agent that returns `true/false` → coordinator aggregates and sends relevant files.

- **Security:** Injection can only influence the constrained boolean/label output; cannot escape into the coordinator's reasoning
- **Trade-off:** Sub-agent output must be semantically constrained; complex information cannot flow through
- **Use cases:** Classification, filtering, relevance scoring over untrusted documents

### 4. Dual LLM Pattern

**Constraint:** A **privileged LLM** orchestrates; a **quarantined LLM** handles untrusted content. The quarantined LLM returns only **symbolic variables** (e.g., `$VAR1` representing a summarized page) — the privileged LLM can reference these without being exposed to the underlying tainted content.

Origin: Simon Willison (April 2023); also influenced the CaMeL paper.

```
User → Privileged LLM → Quarantined LLM (reads untrusted content)
                      ↓                         ↓
                   Actions                  $VAR1 = result
                      ←─────────────────────────
```

- **Security:** Privileged LLM has zero exposure to tainted content; symbolic variables are passed by reference
- **Trade-off:** Complexity of two-LLM architecture; privileged LLM must never be shown variable contents directly

### 5. Code-Then-Execute Pattern (CaMeL)

**Constraint:** The privileged LLM generates **code in a sandboxed DSL** rather than making direct tool calls. The DSL is designed for full data flow analysis — tainted data is marked and tracked through the entire execution.

Described in DeepMind's CaMeL paper (2025). An evolution of the Dual LLM pattern that replaces symbolic variables with a formal data flow graph, enabling provable taint tracking.

- **Security:** Any data derived from untrusted sources is permanently marked as tainted; provably cannot escape the sandbox to trigger actions on unmarked channels
- **Trade-off:** Requires a custom DSL and runtime; complex to implement
- **Use cases:** High-security agents where formal guarantees are required

### 6. Context-Minimization Pattern

**Constraint:** Remove unnecessary or potentially dangerous context (including the original user prompt) from the LLM's context window **before** processing results.

Example: User asks for a quote (possibly injecting a discount request) → translated into a structured DB query → DB results returned without the original user prompt → agent responds based only on the clean DB results.

- **Security:** Injection must survive a strict format conversion (e.g., structured query) to have any effect; unlikely if formatting requirements are tight
- **Trade-off:** Utility reduced if original context is needed for nuanced response
- **Use cases:** Customer service bots, structured data retrieval systems

---

## Design Pattern Comparison

| Pattern | Agent reads untrusted content? | Can untrusted content change actions? | Complexity |
|---|---|---|---|
| **Action-Selector** | No | No | Low |
| **Plan-Then-Execute** | After planning | No (only content within planned actions) | Medium |
| **Map-Reduce** | Yes (sub-agent) | No (constrained output) | Medium |
| **Dual LLM** | Yes (quarantined) | No (symbolic variables only) | High |
| **Code-Then-Execute** | Yes (quarantined) | No (taint tracked in DSL) | Very High |
| **Context-Minimization** | Filtered | Unlikely (format conversion) | Low–Medium |

---

## Case Studies (10 total)

The paper applies the patterns to concrete agent types, each with detailed threat models:

- OS Assistant, SQL Agent, Email & Calendar Assistant, Customer Service Chatbot, Booking Assistant, Product Recommender, Resume Screening Assistant, Medication Leaflet Chatbot, Medical Diagnosis Chatbot, **Software Engineering Agent**

The **SQL Agent** case study (3 pages) is particularly detailed — an LLM with SQL and Python execution access is a high-risk environment. The **Software Engineering Agent** case study illustrates using a quarantined LLM to convert untrusted external documentation into a strictly formatted API description (method names ≤ 30 chars) before the privileged agent sees it.

---

## Key Takeaways

- General-purpose agents cannot be secured against prompt injection with current LLMs; the only reliable path is **constraining agent capabilities**
- The core principle: after ingesting any untrusted input, the agent must be structurally unable to trigger consequential actions based on that input
- Six patterns exist on a spectrum from least capable / most secure (Action-Selector) to most capable / hardest to secure (Code-Then-Execute)
- Dual LLM and Code-Then-Execute are the most powerful patterns — quarantine all untrusted-content handling to a restricted sub-agent, never expose the orchestrator
- Plan-Then-Execute is a practical middle ground: pre-determine all action targets before reading any untrusted content
- Map-Reduce enables processing large corpora of untrusted documents safely by constraining output to booleans/labels
- Context-Minimization is a cheap but partial mitigation: converting prompts to structured queries discards most injection payloads
- These are architectural constraints, not filters — they work by making injection *structurally impossible* for certain attack vectors, not by detecting and blocking attacks
