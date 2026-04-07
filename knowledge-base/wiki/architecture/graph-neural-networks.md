# Graph Neural Networks

**Related:** [[architecture/attention]] · [[inference/prompting-and-reasoning]]  
**Sources:** [[summaries/Graph-Based Prompting and Reasoning with Language Models]]

---

## Why Graphs?

Standard deep learning (transformers, CNNs) handles Euclidean data — sequences and grids. Many real-world structures are **non-Euclidean**: molecules, knowledge graphs, social networks, and reasoning chains. Graph Neural Networks (GNNs) operate on graph-structured data where the topology (who is connected to whom) carries meaning.

---

## GCN — Graph Convolutional Network

Each node has a learned embedding vector. Each layer applies:
1. **Transform:** Apply a feed-forward layer to each node's embedding
2. **Aggregate:** Mix in the embeddings of neighboring nodes (e.g., by averaging)

Stacking multiple layers lets each node's representation incorporate information from further-away nodes. `k` layers → node sees its `k`-hop neighborhood.

---

## GAT — Graph Attention Network

Replaces the simple average aggregation with **learned attention weights** over neighbors — analogous to how self-attention works in transformers:

```
h_i' = aggregate_j∈N(i) [α_{ij} · W · h_j]
```

Where `α_{ij}` is an attention score between node `i` and neighbor `j`, computed from their embeddings. Nodes learn *which* neighbors to pay attention to.

This is exactly self-attention applied to a graph's adjacency structure instead of a sequence.

---

## Graph-Based Reasoning with LLMs

### Prompting Hierarchy

| Technique | Structure | Key capability |
|---|---|---|
| Chain-of-Thought (CoT) | Linear chain | Step-by-step rationale |
| Self-Consistency | Multiple chains + majority vote | Reduces single-path errors |
| Tree-of-Thought (ToT) | Tree with backtracking | Lookahead, search |
| **Graph-of-Thought (GoT)** | Directed graph | **Merge separate paths, feedback loops** |

GoT strictly generalizes all prior approaches — it can simulate CoT and ToT as degenerate cases.

See [[inference/prompting-and-reasoning]] for full details on CoT / ToT / GoT usage.

### GOTR — Graph-of-Thought Reasoning (fine-tuned)

A trained encoder-decoder system (not pure prompting) that encodes:
- Text via T5 encoder
- Images via ViT (DETR)
- **Entity relationship graph** via GAT (subject-verb-object triplets extracted with CoreNLP)

The GAT output is fused with text/image encodings via cross-attention. The result outperforms GPT-3/3.5 on GSM8K math word problems and achieves SOTA on ScienceQA (multimodal QA).

**Limitation:** Task-specific fine-tuning required — not plug-and-play.

### GoT — Graph of Thoughts (pure prompting)

No fine-tuning. Any causal LLM. Models each generated thought as a node; edges encode dependencies.

**Three thought transformations:**
- **Aggregation:** Merge multiple thoughts (e.g., combine sorted sublists into a final sorted list)
- **Refinement:** Self-loop — iteratively improve a single thought
- **Generation:** Expand one thought into multiple parallel branches

**Implementation modules:**
- *Prompter* — formats current graph state into an LLM prompt
- *Parser* — extracts structured thought state from output
- *Scorer* — evaluates thought quality
- *Controller* — decides which transformation to apply next

**When GoT wins:** Problems decomposable into sub-problems that can be merged (sorting, set intersection). The aggregation operation is GoT's distinctive advantage over CoT/ToT.

**Trade-off:** More LLM calls per problem → higher cost. On open-ended tasks, the advantage over simpler methods narrows.
