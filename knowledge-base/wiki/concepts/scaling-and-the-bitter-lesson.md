# Scaling and The Bitter Lesson

**Related:** [[concepts/foundation-models]] · [[training/pretraining]] · [[architecture/transformer]] · [[architecture/vision-transformers]]  
**Sources:** [[summaries/The Bitter Lesson]] · [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/AINews Is Harness Engineering real - Latent.Space]]

---

## The Bitter Lesson (Rich Sutton, 2019)

**Core thesis:** In the long run, the only thing that matters in AI is leveraging **computation**. Human-designed tricks, rules, and specialized knowledge consistently lose to general-purpose methods that scale with Moore's Law.

> *"Researchers always try to make their systems work better by incorporating human knowledge. But over a longer timeframe, this is always crushed by methods that leverage computation."*

### Why It's "Bitter"

The lesson is bitter because human ingenuity and domain expertise — despite providing short-term gains — consistently prove to be a **performance ceiling**. The elegant, hand-crafted solution loses to the simple, dumb, scalable approach.

### Historical Evidence

| Domain | Hand-crafted approach | What beat it |
|---|---|---|
| Chess | Minimax + handcrafted evaluation | Deep Blue (search at scale), then AlphaGo (learned value functions) |
| Computer Vision | SIFT, HOG features | Deep CNNs (ImageNet 2012: SVM 25% → AlexNet 15%) |
| NLP | Grammar rules, linguistic features | RNNs, then Transformers |
| Language Translation | Statistical MT, alignment models | Sequence-to-sequence + attention, then Transformers |
| Game Playing (Go) | Hand-crafted patterns, human intuition | AlphaGo (MCTS + deep learning) |

### Two Scalable Methods

1. **Search** — exploring a large space efficiently (Monte Carlo Tree Search, beam search)
2. **Learning** — gradient-based optimization over large models and data

Both scale with compute. Both continue improving as resources grow. Everything else has a ceiling.

### What to Build In

The lesson is *not* "don't use domain knowledge." It's about *where* to embed it:
- **Build in:** general methods, flexible architectures capable of learning structure from data
- **Don't bake in:** specific knowledge, hand-crafted features, brittle heuristics

---

## The GPT Scaling Trajectory

The clearest empirical illustration of the Bitter Lesson in NLP:

| Model | Parameters | Adaptation | Key contribution |
|---|---|---|---|
| GPT (2018) | 117M | Fine-tuning per task | Pretraining + fine-tuning paradigm |
| GPT-2 (2019) | 1.5B | Zero-shot prompting | Emergent task-solving from scale |
| GPT-3 (2020) | 175B | Few-shot in-context | Prompting replaces fine-tuning |

**Pattern:** Each step removed the need for more task-specific human engineering. Scale was the only variable changed.

GPT-2 showed that zero-shot performance consistently improved with model size across all tasks — the models were still **underfitting** even at 1.5B parameters, pointing to further gains.

---

## Scaling Laws

Empirical finding (Kaplan et al. 2020, Hoffmann/Chinchilla 2022):

**Loss scales as a power law** with model parameters `N`, training tokens `D`, and compute `C`:
```
L(N, D) ∝ N^{-α} + D^{-β} + const
```

**Chinchilla finding:** For a given compute budget `C`, the optimal allocation is roughly:
```
N_optimal ≈ sqrt(C / 6)     (parameters)
D_optimal ≈ 20 × N          (tokens)
```

Many earlier large models were undertrained — too many parameters, too few tokens. The optimal ratio is ~20 tokens per parameter.

**Implication:** You often get more performance from more data + a smaller model than from a bigger model trained on less data.

---

## Scaling in Vision

The same dynamic played out in vision:
- CNNs with handcrafted inductive biases (locality, translation equivariance) dominated when data was limited
- ViT, with minimal inductive bias and far more data, matched and then exceeded CNNs
- CLIP (400M internet image-text pairs) achieved zero-shot transfer rivaling supervised models

See [[architecture/vision-transformers]].

---

## Key Takeaway

> *"Scale beats hand-crafted approaches — not in every paper, but in every decade."*

The practical implication for practitioners: invest in data quality and quantity, in general architectures (transformers), and in compute before investing in elaborate domain-specific engineering.

---

## The Bitter Lesson Applied to Agent Harnesses

The Bitter Lesson predicts a specific dynamic in agent engineering: scaffolding built to compensate for model weaknesses will eventually be rendered obsolete by model improvements.

This has already occurred once: before reasoning models (GPT-o1, DeepSeek-R1), elaborate agentic scaffolding made many sequential calls to weaker models to simulate chain-of-thought reasoning. Reasoning models arrived and eliminated the need for that scaffolding — the model internalized what the harness was doing (Noam Brown, 2026).

The same pattern is expected to recur: any harness component that compensates for a current model limitation is a candidate for obsolescence as models improve.

**Counterargument (Big Harness):** Despite the Bitter Lesson, market evidence suggests harness engineering has durable value — Cursor's $50B valuation, dramatic cross-model improvements from harness optimization (Pi blog), and Jerry Liu's observation that the biggest barrier to AI value is context/workflow engineering, not model capability. The harness may evolve rather than disappear: as one layer of scaffolding becomes obsolete, new applications expose new limits that require new scaffolding.

See [[summaries/AINews Is Harness Engineering real - Latent.Space]] and [[wiki/applications/agent-harness]] for the full debate.
