# The Bitter Lesson

**Source:** [[raw/articles/The Bitter Lesson]]  
**Author:** Rich Sutton  
**Published:** March 13, 2019  
**Related:** [[raw/articles/Language Model Training and Inference From Concept to Code]] · [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## The Core Argument

Seventy years of AI research consistently show the same pattern: **general methods that scale with computation beat hand-crafted, knowledge-based methods** — always, eventually, and by a large margin.

The reason is Moore's law. Computation gets exponentially cheaper over time. Approaches designed around fixed compute budgets (where injecting human knowledge helps) are eventually overtaken once more compute becomes available and general learning/search methods are applied at scale.

> *"The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin."*

---

## Historical Evidence

| Domain | Human-knowledge approach | Scalable approach that won |
|---|---|---|
| **Chess** | Rules encoding chess structure | Deep brute-force search (defeated Kasparov, 1997) |
| **Go** | Hand-crafted heuristics, pattern libraries | Search + self-play learning (20 years later) |
| **Speech recognition** | Phonemes, vocal tract models | HMMs → deep learning on large corpora |
| **Computer vision** | Edges, SIFT features, generalized cylinders | CNNs with convolution + learned invariances |

The pattern repeats: human-knowledge approaches win in the short term and feel satisfying to build, then plateau — while the brute-force, computation-scaling approach eventually dominates.

---

## The Two Scalable Methods

**Search** and **learning** are the only methods that scale arbitrarily with increased computation:
- Search: bring massive compute to bear on finding good solutions (e.g. game tree search, beam search).
- Learning: train on large datasets and let the system discover structure (e.g. pretraining LLMs on internet text).

LLMs are a direct expression of this thesis — see [[raw/articles/Language Model Training and Inference From Concept to Code]] and [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]].

---

## What to Build In (and What Not To)

**Don't build in:** domain knowledge, human-conceived representations of space, objects, symmetries, language structure. These feel right but are endlessly complex and ultimately limit the system.

**Do build in:** meta-methods — general mechanisms like search and learning that can *discover* arbitrary complexity on their own.

> *"We want AI agents that can discover like we can, not which contain what we have discovered. Building in our discoveries only makes it harder to see how the discovering process can be done."*

---

## Why It's "Bitter"

Researchers invest deeply — intellectually and psychologically — in human-knowledge approaches. When the scaling approach wins, it's a repudiation of that work. The lesson is "bitter" because:
1. The knowledge-based approach always helps in the short term and is personally satisfying.
2. It inevitably plateaus and even *inhibits* further progress.
3. Success arrives through the opposing approach, often after the field resists it.

---

## Relevance to Modern LLMs

The Bitter Lesson is the philosophical foundation of the LLM scaling era. Pretraining on massive corpora with next token prediction — no linguistic rules, no hand-crafted grammar, no explicit reasoning modules — is the canonical example of what Sutton advocates. SFT and RLHF/DPO then further refine the model through more learning, not more human-specified rules. See [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] and [[summaries/Direct Preference Optimization (DPO)]].
