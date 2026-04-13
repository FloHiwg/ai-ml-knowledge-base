# AI Agents from First Principles

**Source:** [[raw/articles/AI Agents from First Principles]]
**Author:** Cameron R. Wolfe, Ph.D.
**Related:** [[summaries/LLM Powered Autonomous Agents  Lil'Log]] · [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

A ground-up framework for understanding AI agents — starting from a standard text-to-text LLM and showing how each capability addition (tool use, reasoning, iterative planning, autonomy) incrementally creates a more agentic system. Provides both the formal ReAct policy framework and a practical Level 0–3 spectrum for classifying agent systems by capability.

---

## Building Blocks: LLMs → Agents

### Tool Usage

**Two approaches to teaching tool use:**

| Approach | Method | Trade-off |
|---|---|---|
| **Finetuning** (early) | Curate training examples with function calls in the token stream | High human effort; limited to fixed tool set |
| **Prompt-based** (modern) | Provide tool schemas as context; LLM uses ICL to call tools | Low effort; scales to hundreds/thousands of tools |

**Tool call execution flow:**
1. LLM generates a tool call token sequence
2. Stop generation; parse tool name + parameters
3. Call the tool
4. Inject tool response back into token stream
5. Resume generation

**MCP (Model Context Protocol)**: Anthropic's standard for connecting LLMs to external tools. Standardizes the format for tool/resource integrations; developers create pre-built "MCP servers" any LLM can connect to. Key insight: as agents need more tools, standardized integration becomes essential.

**Limitation of tool use alone**: Effectiveness is bounded by the LLM's reasoning capability. The LLM must decompose problems, choose the right tool, and format calls correctly — all demanding strong orchestration ability.

### Reasoning Models

Standard CoT prompting reveals that LLMs are better at reasoning than initially thought — generating a rationale before the answer substantially improves performance. But CoT is static; it doesn't adapt to problem difficulty.

**Reasoning models** (RLVR-trained) change this: they generate variable-length chains of thought before answering, exhibiting backtracking, self-refinement, and dynamic adaptation. Harder problems get longer CoTs. See [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]] for details.

Key implication for agents: a sufficiently capable reasoning LLM can decompose problems, plan, and adapt — this is the foundation of agentic behavior.

---

## The ReAct Framework

### Formal Policy Definition

At each timestep `t`, the agent receives an observation `o_t` from the environment. A **policy** `π` maps the full context (concatenated prior observations and actions) to the next action `a_t`:

```
context = [o_1, a_1, o_2, a_2, ..., o_t]
a_t = π(context)   # deterministic or stochastic
```

The loop continues until a terminal action is reached.

**ReAct's key addition**: expands the action space `A` to include language. The agent can output a *thought* as an action — "thinking" is a first-class action. Formally:

```
A = {discrete_actions} ∪ {language_thoughts}
```

This means the agent can choose to reason in free-form natural language before (or instead of) taking a concrete external action.

### The Thought/Action/Observation Loop

```
Thought: I need to find X...
Action: Search[X]
Observation: [search results]
Thought: The results show Y, so next I need to...
Action: Lookup[Y]
Observation: [lookup results]
Thought: Now I have enough to answer.
Action: Finish[answer]
```

Agents are guided by in-context examples of human-crafted problem-solving trajectories. The frequency of thoughts can be:
- **Fixed** (one thought per action) — for reasoning-heavy tasks
- **Sparse / agent-determined** — for decision-making tasks with many actions

### Benchmarks and Performance

Two use-case categories in [1]:
1. **Knowledge-intensive reasoning**: HotpotQA (multi-hop QA), FEVER (fact verification) — Wikipedia API as action space
2. **Decision making**: ALFWorld (simulated household navigation), WebShop (autonomous shopping)

Results:
- ReAct > Act-only (no thoughts) — reasoning traces are critical
- CoT outperforms ReAct in some cases (less hallucination-prone settings); ReAct wins when external grounding is needed
- ReAct agents are brittle — non-informative retrieved content can cause failure

### ReAct + CoT Backoff Strategies

ReAct and CoT are complementary:
- **ReAct → CoT**: default to CoT if ReAct fails after N steps
- **CoT → ReAct**: take several CoT samples; use ReAct if answers disagree

Either direction improves overall problem-solving capability.

---

## The Agent Spectrum: Level 0–3

A taxonomy for classifying agent systems by capability level:

| Level | Description | Key property |
|---|---|---|
| **Level 0** | Standard LLM (+ optional CoT/reasoning) | Relies on parametric knowledge only; single-step output |
| **Level 1** | Tool-use LLM | Can delegate sub-tasks to external APIs; mitigates hallucination and knowledge cutoff |
| **Level 2** | Problem decomposition (ReAct-style) | Sequential, stateful problem solving; introduces control flow to inference |
| **Level 3** | Increasing autonomy | Takes concrete real-world actions; can run asynchronously without human prompting |

Key insight: "The simplest way to view the starting points for language model-based agents is any tool-use language model. The spectrum of agents increases in complexity from here." — Nathan Lambert

All of these fall under the umbrella of "agent" — the term covers a wide range. The spectrum framing avoids the definitional confusion that plagues the field.

---

## Prior Agent Work (Historical Context)

| System | Key idea | Limitation vs. ReAct |
|---|---|---|
| **Inner Monologue (IM)** | LLM generates plans and monitors task execution via environment feedback (robotics) | Thoughts are constrained by environment feedback; no free-form reasoning |
| **WebGPT** | GPT-3 + text-based web browser for QA; preferred over humans in >50% of cases | Requires large finetuning dataset via behavior cloning |
| **Gato** | Single generalist agent across Atari, robotics, image captioning, etc. | Also trained via massive imitation learning dataset |
| **RAP** | LLM builds reasoning tree explored via MCTS; LLM serves as both agent and world model | Text-only reasoning; not a general problem-solving framework |

RAP is notable: the LLM is used both to generate candidate reasoning steps and to evaluate them (as a reward/world model), then MCTS selects the high-reward path.

---

## The Future: Nines of Reliability

> "The thing holding agents back was the extra nines of reliability… that's the way you would still describe the way in which these software agents aren't able to do a full day of work, but are able to help you out with a couple minutes."

Sequential agent systems fail catastrophically if any single step goes wrong. Reliability — not capability — is the limiting factor for production agents. Research directions addressing this:
- Better evaluation frameworks for agents
- Multi-agent systems (parallelism + specialization)
- Finetuning agent systems for specialized domains

---

## Key Takeaways

- Agents exist on a spectrum from tool-use LLMs (Level 1) to fully autonomous systems (Level 3) — all are legitimately "agents"
- ReAct formalizes the agent as a **policy** mapping context to actions, with language thoughts as first-class actions
- ReAct > Act-only; CoT wins in low-hallucination settings; backoff strategies combining both outperform either alone
- MCP standardizes the tool integration layer — as agents need more tools, this becomes critical infrastructure
- Reasoning models are the capability foundation of agents: variable-length CoT, backtracking, self-refinement
- The key bottleneck is not capability but **reliability** — agents need more "nines" before they can own full workdays
- RAP (MCTS + LLM world model) is an alternative planning strategy for text-based reasoning problems
