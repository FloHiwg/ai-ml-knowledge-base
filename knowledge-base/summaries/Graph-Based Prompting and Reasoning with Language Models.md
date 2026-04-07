# Graph-Based Prompting and Reasoning with Language Models

**Source:** [[raw/articles/Graph-Based Prompting and Reasoning with Language Models]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[raw/articles/Language Model Training and Inference From Concept to Code]] · [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

Chain-of-thought and tree-of-thought prompting force LLMs to reason linearly. Human reasoning is non-linear — we make leaps between ideas and merge insights from separate threads. **Graph-based approaches** model the reasoning process as a graph (nodes = thoughts, edges = dependencies), enabling merging, looping, and branching that CoT/ToT cannot express.

> *"Human thinking is often characterized by its ability to make sudden leaps and connections between seemingly unrelated ideas."* — from [1]

---

## Prompting Hierarchy (Context)

| Technique | Structure | Key capability |
|---|---|---|
| Chain-of-Thought (CoT) | Linear chain | Step-by-step rationale |
| Self-Consistency | Multiple chains, majority vote | Reduces single-path errors |
| Tree-of-Thought (ToT) | Tree with backtracking | Lookahead, backtracking |
| **Graph-of-Thought** | **Directed graph** | **Merge separate reasoning paths, feedback loops** |

Each level strictly generalises the one above — GoT can do everything CoT and ToT can do and more.

---

## Background: Graph Neural Networks

Standard deep learning architectures (transformers, CNNs) handle Euclidean data (grids, sequences). **Graph Convolutional Networks (GCNs)** handle non-Euclidean graph data:
- Each node has an embedding vector.
- Each layer: apply a feed-forward transform to each node, then aggregate neighbouring node embeddings (e.g. by averaging).
- Multiple layers → representations capture both local node properties and broader graph structure.

**Graph Attention Networks (GATs)** extend GCNs by replacing the simple average aggregation with a learned attention-weighted aggregation over neighbours — analogous to how self-attention works in transformers.

---

## Paper 1: Graph-of-Thought Reasoning (GOTR) [Yao et al., 2023]

A **fine-tuned, encoder-decoder framework** (not a pure prompting technique). Uses three input modalities:

| Input | Encoder |
|---|---|
| Text | T5 encoder |
| Image (optional) | Vision Transformer (DETR) |
| Thought graph | GAT |

**Thought graph construction:** Extract subject-verb-object triplets from the input text using CoreNLP, resolve co-references, and form a named-entity relationship graph automatically.

**Two-stage pipeline:**
1. **Rationale generation** — encode all inputs, fuse with cross-attention + gated fusion layer, decode a chain-of-thought-style rationale.
2. **Answer generation** — re-encode with rationale appended to input, decode the final answer.

**Results:**
- Outperforms GPT-3/3.5 on GSM8K (math word problems).
- State-of-the-art on ScienceQA (multi-modal science QA), outperforming GPT-4+CoT on several subtasks.
- Largest gains on multi-modal tasks where graph + image signals complement each other.

**Limitation:** Requires fine-tuning per task — it's a trained model, not a plug-and-play prompting strategy.

---

## Paper 2: Graph of Thoughts (GoT) Prompting [Besta et al., 2023]

A **pure prompting approach** — no fine-tuning, works with any causal LLM. Models each LLM-generated thought as a node in a directed graph; edges encode which thoughts were used to produce which.

**Three thought transformations:**
- **Aggregation** — merge multiple thoughts into one (e.g. combine sorted sublists into a final sorted list).
- **Refinement** — self-loop: iteratively improve a single thought.
- **Generation** — expand one thought into multiple new ones.

**Implementation modules:**
- *Prompter* — formats the current graph state into an LLM prompt.
- *Parser* — extracts structured thought state from LLM output.
- *Scorer* — evaluates thought quality (via LLM or heuristic).
- *Controller* — orchestrates the graph, decides which transformation to apply next and when to stop.

The controller maintains two structures: a static **Graph of Operations** (the execution plan) and a dynamic **Graph Reasoning State** (current thought states).

**Results:**
- Fewer sorting errors than CoT, self-consistency CoT, and ToT.
- Higher *volume* (more preceding thoughts can influence the current thought) and lower *latency* (fewer steps to a solution) than CoT/ToT theoretically.
- Less improvement on real-world tasks (document merging, keyword counting) where ToT is already competitive.
- **Higher cost** than CoT — more LLM calls per problem.

---

## GOTR vs GoT

| | GOTR [1] | GoT [2] |
|---|---|---|
| Approach | Fine-tuned encoder-decoder | Pure prompting (no fine-tuning) |
| Graph role | Encodes entity relationships in input | Models the LLM's reasoning process |
| Modalities | Text + image + graph | Text only |
| LLM type | T5 (encoder-decoder) | Any causal LLM |
| Flexibility | Task-specific | General-purpose |

---

## When to Use GoT

**Good fit:**
- Problems naturally decomposable into sub-problems that can be solved and merged (e.g. sorting, set intersection).
- Tasks where merging multiple reasoning threads is essential.

**Probably not worth it:**
- Problems solvable with CoT or ToT — simpler methods are cheaper and competitive.
- Real-world tasks where the merge structure is unclear.

---

## Key Takeaways

- Graph-based reasoning is a strict generalisation of CoT and ToT — it adds merging and feedback loops that linear structures cannot express.
- GOTR is a fine-tuned system that genuinely benefits multi-modal reasoning; GoT is a flexible prompting framework for any LLM.
- The main trade-off for GoT is **cost**: more LLM calls, more complex orchestration.
- The performance advantage over simpler methods is most pronounced on structured, merge-friendly problems; on open-ended tasks the gap narrows.
