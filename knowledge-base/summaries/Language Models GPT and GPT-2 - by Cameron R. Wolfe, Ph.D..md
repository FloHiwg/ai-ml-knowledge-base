# Language Models: GPT and GPT-2

**Source:** [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]]  
**Author:** Cameron R. Wolfe  
**Related:** [[raw/articles/Language Model Training and Inference From Concept to Code]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]] · [[summaries/The Bitter Lesson]]

---

## Core Idea

Train a single large language model on raw, unlabeled text via next token prediction, then reuse it across many downstream tasks — either by fine-tuning (GPT) or zero-shot prompting (GPT-2). This is the foundation of the modern LLM paradigm.

---

## Background

### Language Modeling

A language model is trained to predict the next token given the preceding `k` tokens as context. The training objective maximizes the log-likelihood of the correct next token across a corpus — a **self-supervised** objective since no labels are needed; the ground truth is already in the data.

Key properties:
- Larger models learn better representations and generalize more broadly.
- Pre-training on **long, contiguous text** (not shuffled sentences) is essential — the model needs to learn long-range dependencies.
- Models trained this way aren't just good at text generation; the learned representations transfer to other tasks.

### Decoder-Only Transformer

Both GPT and GPT-2 use a **decoder-only** transformer: the encoder and encoder-decoder cross-attention are removed, leaving only stacked layers of masked self-attention + feed-forward network.

**Why masked (causal) self-attention?** The model must not look ahead when predicting the next token. Masking ensures each token only attends to preceding tokens, making the architecture autoregressive: output at step `t` becomes input at step `t+1`.

This is in contrast to encoder-only models (e.g. BERT) which use bidirectional attention — better for understanding tasks but can't generate autoregressively.

### Foundation Models

The GPT insight: rather than training a new narrow expert for every task (expensive, requires labeled data), pretrain one large model on abundant unlabeled text, then adapt it. This "foundation model" approach:
- Amortizes compute across many tasks
- Mitigates labeled data scarcity
- Produces representations that generalize broadly

---

## GPT [Radford et al., 2018]

**Architecture:** 12-layer decoder-only transformer, learnable positional embeddings. ~117M parameters — identical to the base transformer in "Attention is All You Need."

**Training:** Two phases:
1. **Pretraining** — language modeling on BooksCorpus (long-form books, good for long-range dependencies).
2. **Fine-tuning** — supervised fine-tuning on each downstream task separately.

**Adaptation strategy:** No architectural changes per task. Instead, inputs are reformatted into task-specific structures (e.g. for entailment: `[sentence1] [DELIM] [sentence2]`), passed through GPT, and a lightweight classification head is added on top.

**Results:** State-of-the-art on 9 of 12 NLP benchmarks, outperforming task-specific models and even ensembles.

---

## GPT-2 [Radford et al., 2019]

**Architecture:** Same decoder-only design as GPT, scaled up. Four sizes tested (117M → 1.5B parameters). Minor changes: different weight init, larger vocabulary, longer context window.

**Key departure from GPT:** No fine-tuning at all. Tasks are solved entirely via **zero-shot prompting** — the model receives a natural language prompt and is expected to produce the correct output.

**Data:** WebText — curated from Reddit outbound links (higher quality than raw web crawls).

**Results:**
- Near state-of-the-art on language modeling and reading comprehension (zero-shot).
- Falls short on summarization and QA — the authors attribute this to insufficient model capacity.
- Zero-shot performance **consistently improves with model size**, suggesting the models were still underfitting WebText at 1.5B parameters.

**Key insight:** LMs with sufficient capacity implicitly learn to perform tasks from the structure of the training data, without any explicit supervision.

> *"A language model with sufficient capacity will begin to learn to infer and perform the tasks demonstrated in natural language sequences in order to better predict them."* — from [2]

---

## GPT → GPT-2 → GPT-3: The Scaling Trajectory

| | GPT | GPT-2 | GPT-3 |
|---|---|---|---|
| Parameters | 117M | 1.5B | 175B |
| Adaptation | Fine-tuning | Zero-shot | Few-shot prompting |
| Training data | BooksCorpus | WebText | Common Crawl + more |
| Key contribution | Pretraining + fine-tuning paradigm | Zero-shot transfer via prompting | In-context few-shot learning at scale |

GPT and GPT-2 established the methodology; GPT-3 confirmed that scaling removes the need for fine-tuning on most tasks. The trajectory is a direct illustration of [[summaries/The Bitter Lesson]] — scale beats hand-crafted task-specific approaches.

---

## Key Takeaways

- **Pretraining is powerful** — a single LM pretrained on raw text learns representations that transfer broadly, without ever seeing task labels.
- **Size matters** — every scaling step improved zero-shot and few-shot performance; models consistently underfit larger datasets, pointing to further gains from more scale.
- **Prompting is a zero-cost adaptation mechanism** — GPT-2 showed that reformulating tasks as text completions enables task solving without any gradient updates.
- **Foundation models generalize; narrow experts don't** — the pretrain-then-adapt paradigm replaced the prevailing one-model-per-task approach.
- These models set the stage for SFT and RLHF/DPO: see [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] and [[summaries/Direct Preference Optimization (DPO)]].
