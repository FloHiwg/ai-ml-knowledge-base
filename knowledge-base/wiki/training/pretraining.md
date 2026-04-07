# Pretraining

**Related:** [[training/tokenization]] · [[training/fine-tuning]] · [[training/distributed-training]] · [[concepts/foundation-models]] · [[concepts/scaling-and-the-bitter-lesson]] · [[concepts/agi-and-intelligence]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]] · [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Andrej Karpathy — AGI is still a decade away]]

---

## Core Objective: Next Token Prediction

A language model is trained to predict the next token given preceding context. The training signal is **self-supervised** — no labels needed; the ground truth is the input text itself.

**Objective:** Maximize log-likelihood of the correct next token at every position:
```
L = -∑_t log P(x_{t+1} | x_1, ..., x_t)
```

The same forward pass computes the loss **at all positions simultaneously** via causal masking — the model predicts position `t+1` from positions `1..t` for every `t` in one pass.

---

## Forward Pass (Training)

```
Input tensor  idx     [batch × seq_len]   — token IDs
Target tensor targets [batch × seq_len]   — shifted-right input (idx[:, 1:])

1. Lookup token embeddings + positional embeddings  → [batch × seq_len × d_model]
2. Dropout
3. 12 × TransformerBlock (causal self-attention + FFN)
4. LayerNorm
5. lm_head (linear projection)                      → [batch × seq_len × vocab_size]
6. CrossEntropy loss across all positions
```

The key insight: one forward pass + causal masking = next-token prediction for every token in the batch at once.

---

## What the Model Learns

GPT-2 showed that **with sufficient capacity, a language model implicitly learns to perform downstream tasks** without any explicit training signal for those tasks — because being good at next-token prediction requires understanding syntax, semantics, world knowledge, and reasoning.

> *"A language model with sufficient capacity will begin to learn to infer and perform the tasks demonstrated in natural language sequences in order to better predict them."* — GPT-2 paper

This is the foundation of [[concepts/foundation-models]].

---

## Data Loading

Training data is stored as a flat array of token IDs. Batches are constructed by sampling random contiguous chunks of `context_length` tokens. Targets = input shifted by one position.

```python
# pseudo-code
idx     = data[offset : offset + block_size]     # input
targets = data[offset + 1 : offset + block_size + 1]  # next token for each position
```

---

## Training Data

| Model | Data | Notes |
|---|---|---|
| GPT | BooksCorpus | Long-form books; good for long-range dependencies |
| GPT-2 | WebText (Reddit outbound links) | Higher quality than raw web crawl |
| GPT-3 | Common Crawl + Books + Wikipedia + more | ~570GB of filtered text |

Quality of training data matters as much as quantity. Long, coherent documents are preferred over shuffled sentences — the model needs to learn long-range dependencies.

---

## Pretraining vs Fine-tuning

Pretraining is the expensive, one-time investment:
- Weeks to months on thousands of GPUs
- Learns general language understanding and world knowledge

Fine-tuning is cheap by comparison:
- Hours to days, much smaller data
- Specializes the model for a particular use case or aligns it to human preferences

See [[training/fine-tuning]] for SFT, RLHF, and DPO.

---

## Self-Supervised vs Supervised Learning

| | Supervised | Self-supervised (pretraining) |
|---|---|---|
| Labels | Human-annotated | Generated from data itself |
| Scale | Limited by labeling cost | Unlimited (all text on the internet) |
| Coverage | Task-specific | General |

Self-supervised pretraining is what enables the [[concepts/scaling-and-the-bitter-lesson|Bitter Lesson]] dynamic in NLP: scale data + compute → performance improves without bound.

---

## Pre-Training as "Crappy Evolution"

Pre-training and biological evolution are imperfect analogs. Both produce a starting point with broad knowledge and embedded cognitive algorithms. The key difference: evolution runs an outer loop over generations and encodes priors into DNA/brain wiring; pre-training runs gradient descent on internet text in a single lifetime.

Pre-training does two things simultaneously:
1. **Knowledge encoding** — compresses world knowledge from the training corpus
2. **Cognitive algorithm formation** — bootstraps in-context learning, reasoning circuits, pattern-completion strategies

The knowledge component may actually be a liability: models memorize encyclopedic facts that can distract from generalization. See [[concepts/agi-and-intelligence]] for the **cognitive core** concept — the vision of a model stripped of encyclopedic memory that retains only reasoning algorithms (~1B params).

**Data quality as the binding constraint:** Current large models are big partly because they compress enormous amounts of low-quality internet noise alongside signal. Better curated pre-training data would allow much smaller models with equivalent cognitive capability.
