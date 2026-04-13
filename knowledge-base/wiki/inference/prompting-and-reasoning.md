# Prompting and Reasoning Strategies

**Related:** [[inference/decoding-strategies]] · [[architecture/graph-neural-networks]] · [[training/fine-tuning]] · [[concepts/agi-and-intelligence]] · [[applications/agentic-patterns]]
**Sources:** [[summaries/Graph-Based Prompting and Reasoning with Language Models]] · [[summaries/Andrej Karpathy — AGI is still a decade away]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]] · [[summaries/AI Agents from First Principles]]

---

## Prompting Hierarchy

Each level generalizes the one above — higher levels can simulate lower ones:

| Technique | Structure | Key capability |
|---|---|---|
| **Zero-shot** | Single prompt, no examples | Relies on model's pretraining |
| **Few-shot** | Prompt + examples | In-context learning |
| **Chain-of-Thought (CoT)** | Linear reasoning chain | Step-by-step rationale |
| **Self-Consistency** | Multiple CoT chains + majority vote | Reduces single-path errors |
| **Tree-of-Thought (ToT)** | Tree with backtracking | Lookahead, search, backtracking |
| **Graph-of-Thought (GoT)** | Directed graph | Merge separate paths, feedback loops |

---

## Zero-Shot and Few-Shot

**Zero-shot:** Just ask. GPT-2 demonstrated that large LMs can answer questions in natural language without any examples — because their training data contained demonstrations of task-solving implicitly.

**Few-shot:** Prepend 1–5 examples of the desired format to the prompt. The model infers the pattern and applies it. This is called **in-context learning** — no gradient updates, just conditioning.

### How In-Context Learning Works

In-context learning is not merely pattern matching — it may implement a form of gradient descent *internally* through the attention mechanism:

- Research has shown that transformers trained on XY regression pairs learn to perform linear regression in-context
- Analysis of the weights reveals mechanics analogous to a gradient descent optimizer running inside the layers
- Theoretically, attention heads can implement gradient descent steps

This explains why in-context adaptation is powerful: the model isn't just retrieving — it's doing something structurally similar to learning, but in activation space rather than weight space.

**Memory framing:** Everything in the context window is directly accessible (working memory); everything in the weights is a hazy recollection at ~0.07 bits per training token. Providing relevant text in-context dramatically outperforms relying on parametric memory for specific facts. See [[concepts/agi-and-intelligence]].

---

## Chain-of-Thought (CoT)

Prompt the model to generate intermediate reasoning steps before the final answer:

```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3. How many does he have?
A: Roger starts with 5. 2 cans × 3 balls = 6. 5 + 6 = 11. The answer is 11.
```

**Why it works:** For multi-step problems, the "answer" token comes at the end of the reasoning chain. Conditioning on intermediate steps pushes probability mass toward correct reasoning paths.

**Limitation:** Linear — each step builds on the one before. Cannot merge independent reasoning threads or backtrack.

---

## Self-Consistency

Run CoT multiple times (with temperature > 0) and take a **majority vote** over the final answers. Reduces the impact of individual incorrect reasoning chains.

Cost: K × inference cost. Works well for problems with discrete, verifiable answers.

---

## Tree-of-Thought (ToT)

Model reasoning as a **search tree**:
- Each node is a "thought" (intermediate reasoning state)
- Branches explore different continuations
- A value function (LLM-evaluated) scores each node
- Backtracking when dead ends are reached

Enables **lookahead and recovery** — the model can explore "what if I go this way?" and back out. More effective than CoT for problems requiring strategic planning.

**Cost:** Much more LLM calls than CoT. Best for complex, structured tasks (puzzles, multi-step planning).

---

## Graph-of-Thought (GoT)

See [[architecture/graph-neural-networks]] for full implementation details.

Key additions over ToT:
- **Aggregation:** Multiple independent reasoning branches can be **merged** into a single new thought (impossible in CoT/ToT)
- **Refinement:** A thought can be improved iteratively via self-loops
- **Feedback loops:** The graph can cycle — a thought can inform an earlier thought

GoT is strictly a generalization of CoT and ToT — it can do everything they can, and more.

**Three thought transformations:**
```
Aggregation:  [thought_A, thought_B] → thought_C  (merge/synthesize)
Refinement:   thought_A → improved_A              (self-correction)
Generation:   thought_A → [branch_1, branch_2]    (expand)
```

**Best fit for GoT:** Problems decomposable into independent sub-problems that can be solved and merged (sorting, set operations, document merging). The key advantage is the aggregation operation.

---

## GOTR vs GoT

| | GOTR | GoT |
|---|---|---|
| Approach | Fine-tuned encoder-decoder | Pure prompting (no fine-tuning) |
| Graph role | Encodes entity relationships in the *input* | Models the *reasoning process* |
| LLM | T5-based | Any causal LLM |
| Flexibility | Task-specific | General-purpose |

---

## ReAct: Reasoning + Acting

ReAct (Yao et al. 2023) formalizes agents as a **policy** `π` mapping context to actions, with language thoughts as first-class actions:

```
context = [o_1, a_1, o_2, a_2, ..., o_t]
a_t = π(context)          # observation → action
A = {tool_calls} ∪ {language_thoughts}   # expanded action space
```

The Thought/Action/Observation loop:
```
Thought: I need to find the population of France.
Action: search("France population 2023")
Observation: France has approximately 68 million people.
Thought: Now I can answer.
Action: finish("~68 million")
```

Thought frequency can be fixed (one thought per action, for reasoning-heavy tasks) or agent-determined (sparse, for high-action decision tasks).

**Performance**: ReAct > Act-only on both HotpotQA/FEVER and AlfWorld/WebShop. CoT outperforms ReAct when hallucination is unlikely; ReAct wins when external grounding matters.

**ReAct + CoT backoff strategies:**
- **ReAct → CoT**: fall back to CoT if ReAct fails after N steps
- **CoT → ReAct**: sample multiple CoT answers; invoke ReAct if they disagree

Either direction outperforms using one approach alone.

ReAct is the standard template for tool-using agents — see [[applications/agentic-patterns]].

---

## Cost vs. Performance Trade-off

| Method | LLM calls | Relative cost | Best for |
|---|---|---|---|
| Zero/few-shot | 1 | 1× | Simple, well-defined tasks |
| CoT | 1 | ~1× | Multi-step reasoning |
| Self-Consistency | K | K× | Discrete-answer problems |
| ToT | Many | High | Planning, puzzles |
| GoT | Many | High | Merge-able sub-problems |

Start with the simplest method that works. GoT/ToT are rarely worth the cost unless the task structure genuinely requires merging or backtracking.
