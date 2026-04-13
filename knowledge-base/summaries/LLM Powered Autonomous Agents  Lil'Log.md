# LLM Powered Autonomous Agents  Lil'Log

**Source:** [[raw/articles/LLM Powered Autonomous Agents  Lil'Log]]
**Author:** Lilian Weng (Jun 2023)
**Related:** [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[summaries/Graph-Based Prompting and Reasoning with Language Models]]

---

## Core Idea

A foundational framework for LLM-powered autonomous agents: the LLM serves as the agent's "brain" orchestrating three key subsystems — Planning, Memory, and Tool Use. Written in June 2023, this article synthesizes the early wave of agent research (ReAct, Reflexion, Generative Agents, AutoGPT) and remains the canonical reference for the three-component agent model.

---

## Agent System Overview

```
LLM-Powered Agent = Planning + Memory + Tool Use
```

- **Planning**: decompose tasks, reflect on past actions, refine plans
- **Memory**: in-context (short-term) + external vector store (long-term)
- **Tool use**: external APIs for information, code execution, proprietary data

---

## Component 1: Planning

### Task Decomposition

**Chain of Thought (CoT)** — prompts the model to "think step by step", decomposing a task into manageable subtasks. The model uses more test-time compute. See [[wiki/inference/prompting-and-reasoning]].

**Tree of Thoughts (ToT)** — extends CoT into a tree: generates multiple thoughts at each step, searches via BFS/DFS, evaluates nodes with a classifier or majority vote. Enables backtracking.

**LLM+P** — outsources long-horizon planning to a classical PDDL planner:
1. LLM translates the problem into Problem PDDL
2. Classical planner generates a PDDL plan from Domain PDDL
3. LLM translates the plan back into natural language
Requires domain-specific PDDL; common in robotics but limited elsewhere.

### Self-Reflection

**ReAct** (Yao et al. 2023) — integrates reasoning and acting by extending the action space to include both task-specific discrete actions and natural language reasoning traces:

```
Thought: ...
Action: ...
Observation: ...
... (repeated)
```

Outperforms Act-only (no reasoning traces) on both knowledge-intensive tasks (HotpotQA, FEVER) and decision-making tasks (AlfWorld, WebShop).

**Reflexion** (Shinn & Labash 2023) — adds dynamic memory and self-reflection to enable iterative improvement:
- Standard RL setup with binary reward; action space augmented with language (like ReAct)
- After each action, compute heuristic h_t; optionally reset the environment to start a new trial
- Heuristic detects: *inefficient planning* (too long without success) or *hallucination* (consecutive identical actions → same observation)
- Self-reflection: LLM shown 2-shot examples of (failed trajectory, ideal reflection); reflections stored in working memory (up to 3) for future queries

**Chain of Hindsight (CoH)** (Liu et al. 2023) — finetunes the model to improve on its own outputs by presenting a sequence of past outputs annotated with human feedback, ranked by reward. Model learns to predict the best output `y_n` conditioned on the whole history of improving outputs.
- Regularization: maximizes log-likelihood on pretraining data to prevent overfitting
- Random masking of 0–5% of past tokens to prevent shortcut copying

**Algorithm Distillation (AD)** (Laskin et al. 2023) — applies CoH idea to RL: concatenates cross-episode learning histories and trains the model to predict the next action, effectively distilling an RL algorithm into the model's weights. Requires 2–4 episodes of context to learn near-optimal in-context RL.

---

## Component 2: Memory

### Human Memory Taxonomy Mapped to LLM Components

| Human memory type | LLM equivalent |
|---|---|
| **Sensory memory** | Embedding representations of raw inputs (text, image, etc.) |
| **Short-term / Working memory** | In-context learning — finite, restricted by context window |
| **Long-term memory** | External vector store with fast retrieval |

Long-term memory subtypes:
- *Explicit/declarative*: facts and events (episodic + semantic)
- *Implicit/procedural*: automatic skills and routines

### MIPS / ANN Algorithms for External Memory

External memory relies on Maximum Inner-Product Search (MIPS) over embeddings. Since exact search is slow at scale, all practical systems use Approximate Nearest Neighbors (ANN):

| Algorithm | Key idea |
|---|---|
| **LSH** (Locality-Sensitive Hashing) | Hash function maps similar inputs to same buckets; many fewer buckets than inputs |
| **ANNOY** (Approximate Nearest Neighbors Oh Yeah) | Random projection trees; binary trees split space by random hyperplanes; search all trees |
| **HNSW** (Hierarchical Navigable Small World) | Multi-layer small-world graphs; upper layers = long shortcuts; lower layers = refinement |
| **FAISS** (Facebook AI Similarity Search) | Assumes Gaussian distances in high-D; vector quantization into clusters; coarse then fine search |
| **ScaNN** (Scalable Nearest Neighbors) | Anisotropic vector quantization — preserves inner-product distance specifically, not just L2 |

HNSW and FAISS are the most widely used in production vector databases.

---

## Component 3: Tool Use

**MRKL** (Modular Reasoning, Knowledge and Language) — neuro-symbolic architecture: LLM as router directing queries to specialized "expert" modules (neural or symbolic). Key finding: knowing *when* to call a tool is as hard as calling it correctly; LLM capability determines tool use quality.

**TALM / Toolformer** — finetune LMs to call external tool APIs. Dataset expanded by filtering on whether new API call annotations improve model output quality.

**HuggingGPT** — ChatGPT as orchestrator over HuggingFace models. Four-stage pipeline:
1. *Task planning*: LLM parses user request into typed tasks with dependencies
2. *Model selection*: LLM picks the best HuggingFace model for each task (multiple-choice prompt with filtered candidates)
3. *Task execution*: Selected expert models run on their sub-tasks
4. *Response generation*: LLM summarizes execution results

**API-Bank** — benchmark with 53 APIs, 264 annotated dialogues, 568 API calls. Three evaluation levels: (1) call the API correctly, (2) retrieve the right API, (3) plan across multiple API calls for complex tasks.

---

## Case Studies

### ChemCrow (Scientific Discovery Agent)
- LLM augmented with 13 chemistry expert tools (organic synthesis, drug discovery, materials design)
- Uses ReAct format (Thought / Action / Action Input / Observation)
- Key finding: GPT-4 self-evaluation rated GPT-4 ≈ ChemCrow, but human expert evaluation showed ChemCrow outperforms GPT-4 significantly — **LLMs can't evaluate domains they lack expertise in**

### Generative Agents (Park et al. 2023)
25 LLM-powered virtual characters in a Sims-like sandbox. Architecture combines:
- **Memory stream**: long-term external DB; each entry = an observation in natural language
- **Retrieval model**: surfaces context by scoring Recency (recent events score higher) + Importance (LLM asked directly) + Relevance (embedding similarity to current situation)
- **Reflection mechanism**: LLM prompted with 100 most recent observations → generates 3 salient high-level questions → answers them to form higher-level summaries
- **Planning & Reacting**: reflections + environment info → actions; environment stored as a tree structure

Results: emergent social behavior — information diffusion, relationship memory, spontaneous event coordination (e.g., throwing a party).

---

## Proof-of-Concept Systems

**AutoGPT** — autonomous agent with full tool suite (web search, file I/O, code execution, spawning sub-agents). Self-criticism loop baked in. Reliability issues due to natural language interface; much code is format parsing.

**GPT-Engineer** — iterative code generation: clarification → planning (class/function inventory) → file-by-file code output. Separation of clarification phase from execution phase is the key design insight.

---

## Challenges (as of 2023 — still relevant)

1. **Finite context length** — limits history, detailed instructions, API call context. Vector retrieval helps but lacks the representational power of full attention.
2. **Long-horizon planning and task decomposition** — LLMs struggle to adjust plans on unexpected errors; less robust than humans at trial-and-error.
3. **Reliability of natural language interface** — formatting errors, occasional refusal, parsing complexity. Most agent demo code centers on output parsing.

---

## Key Takeaways

- The canonical three-component framework: Planning + Memory + Tool Use
- ReAct (Thought/Action/Observation loop) is the standard agentic prompting pattern for tool-using agents
- Reflexion adds iterative self-improvement via reflection stored in working memory
- External memory = vector store with ANN search; HNSW and FAISS dominate in practice
- Human memory taxonomy (sensory → STM → LTM) maps cleanly onto LLM components
- Self-evaluation of LLM quality by LLMs fails in expert domains — ChemCrow case is the canonical example
- The three 2023 challenges (context, planning, NL interface) are progressively addressed by 2026 agent systems (see [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]])
