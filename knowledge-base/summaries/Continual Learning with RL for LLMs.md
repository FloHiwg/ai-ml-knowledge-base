# Continual Learning with RL for LLMs

**Source:** [[raw/articles/Continual Learning with RL for LLMs]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Direct Preference Optimization (DPO)]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## Core Idea

Continual learning — training a model on new tasks over time without losing prior capabilities — has historically been difficult due to catastrophic forgetting. Recent research reveals a surprising result: **on-policy RL naturally mitigates catastrophic forgetting** without any explicit continual learning mechanism, while SFT consistently degrades prior performance. The root cause is the on-policy nature of RL, which biases learning toward low-distributional-shift solutions.

---

## Basics of Continual Learning

### Catastrophic Forgetting

When a model trains on new data, gradient updates overwrite representations needed for old tasks. The greater the distributional shift between old and new data, the more severe the forgetting.

**Goal:** Learn new tasks (`plastic`) while preserving prior capabilities (`stable`) — the classic stability-plasticity tradeoff.

### Experimental Frameworks

| Framework | Description |
|---|---|
| **Batch-incremental** | Sequential exposure to whole task datasets `{D_1, D_2, …, D_T}`; no access to past data during each stage |
| **Domain adaptation** | Special case T=1: pretrained model trained on a single new domain |
| **Streaming learning** | Brief online updates per data point in real time |
| **Multi-task (joint) training** | Train on all tasks simultaneously — the performance ceiling / ideal baseline |

Non-IID data (new distribution) induces forgetting; continued training on the same distribution generally does not.

### Classic Mitigation Techniques

| Category | Approach |
|---|---|
| **Replay** | Store a buffer of prior data; train jointly with new data. Effective but hard to scale for LLMs whose training data is vast and often unavailable. |
| **Knowledge distillation** | Add a distillation loss that penalises drift from the prior model's outputs during new-task training. |
| **Regularization** | Constrain updates on important parameters (EWC, Memory-Aware Synapses); KL divergence penalty against prior policy. |
| **Architectural** | Add new modules (e.g., LoRA adapters) per task; Mixture-of-Experts architectures inherently resist forgetting. |

---

## Why SFT Forgets, Why RL Doesn't

### The KL Divergence Framing

**SFT ≈ Forward KL (mode-covering):** Minimising negative log-likelihood over a fixed offline dataset is equivalent to minimising the forward KL divergence `KL(π_* || π_θ)`. The model is heavily penalised for assigning near-zero probability to *any* completion in the data — it must spread probability mass across all modes. When the dataset covers only a small part of the model's original distribution, this spreading effect can crush unrepresented prior knowledge.

**RL ≈ Reverse KL (mode-seeking):** Maximising expected reward on on-policy completions is equivalent to minimising the reverse KL divergence `KL(π_θ || π_*)`. The model seeks high-reward modes without being penalised for ignoring other modes. This mode-seeking behaviour, combined with the on-policy nature of sampling, naturally limits distributional shift.

**Key insight:** For multi-modal target distributions (like an LLM's general capabilities), the mode-seeking objective of RL allows both old and new knowledge to coexist, while the mode-covering objective of SFT forces trade-offs.

---

## Paper Summaries

### [1] RFT Naturally Mitigates Forgetting in Continual Post-Training

**Setup:** Qwen-2.5-VL-7B sequentially trained on 7 vision-QA datasets (ScienceQA, TextVQA, VizWiz, Geometry3K, GQA, PathVQA, Super-CLEVR). No replay buffer.

**Metrics:**
- `AvgAcc` — average accuracy across all tasks at the end
- `FM` (Forgetting Measure) — average drop from peak accuracy per task (closer to 0 = less forgetting)

**Results:**

| Method | AvgAcc | FM |
|---|---|---|
| SFT | 54.0% | -10.4% |
| GRPO (RL) | 60.0% | -2.3% |
| Multi-task (upper bound) | 62.9% | — |

RL also maintains or improves general benchmark performance (MMMU: 52.1% → 54.2% after continual RL). SFT degrades it.

**Why?** Not KL divergence penalty (removing it doesn't change forgetting). Not long CoT (models without CoT show the same pattern). Theory shows **RL naturally scales parameter updates by reward variance** — sensitive/important parameters for prior tasks receive conservative updates because those tasks have high variance on new-task rewards.

### [2] Retaining by Doing: On-Policy Data Mitigates Forgetting

**Setup:** Domain adaptation (single new task), Qwen-2.5 and Llama-3 up to 8B. Three algorithms:
1. SFT from teacher model (Llama-3.3-70B)
2. Self-SFT (rejection sampling from initial policy — offline)
3. RL (GRPO with verifiable rewards — on-policy)

**Results:** Qwen-2.5 with RL: <1% average accuracy drop on non-target tasks. SFT: up to 30% drop. RL and SFT sit at different points on the Pareto frontier — SFT achieves higher in-domain accuracy but at the cost of forgetting.

**Key finding:** The continual learning advantage is not from GRPO specifically (naive REINFORCE shows the same pattern) or from KL regularization. It comes from **on-policy data**:
- `On-policy SFT` (SFT using samples generated by the current policy during RL) matches RL's forgetting resistance
- `Iterative SFT` (regenerate data each epoch) also substantially reduces forgetting
- Practical guideline: if you can't run RL, re-sample data asynchronously or at the start of each epoch

### [3] RL's Razor: Why Online RL Forgets Less

**Core claim:** KL divergence between base and finetuned models, measured on the target dataset, **reliably predicts catastrophic forgetting**. RL is implicitly biased toward solutions with minimal KL → "RL's Razor."

> *"RL's Razor: among the many high-reward solutions for a new task, on-policy methods such as RL are inherently biased toward solutions that remain closer to the original policy in KL divergence."*

**Verified via:**
- Toy MNIST/FashionMNIST experiments: KL divergence is the only metric consistently predictive of forgetting (not gradient magnitude, sparsity, or rank)
- Oracle experiment: SFT on data analytically constructed to minimise KL beats RL itself
- SimPO (offline preference tuning) resembles SFT in forgetting behaviour; on-policy algorithms (GRPO, REINFORCE) do not
- Further theoretical justification

**Implication:** RL doesn't forget less because of architectural properties — it's the **online nature of training** that discovers low-KL solutions.

### [6] Entropy-Adaptive Fine-Tuning (EAFT)

**Diagnosis:** SFT data contains "Confident Conflicts" — tokens where:
- The model has **low entropy** (is very confident about its prediction)
- But the target token has **low probability** under the model (strong conflict with external supervision)

These tokens cause large, destructive gradient updates that overwrite general representations. On-policy RL data has almost no confident conflicts because the model generates data consistent with its own distribution.

**Solution:** Scale the per-token cross-entropy loss by the token's normalised entropy:

```
EAFT_loss(token_t) = entropy(token_t) × CE_loss(token_t)
```

Low-entropy tokens (confident conflicts) receive near-zero loss weight. High-entropy tokens (genuine uncertainty) receive full weight.

Computed over Top-K=20 tokens only for efficiency (minimal overhead vs vanilla SFT).

**Results:** EAFT matches RL's forgetting resistance while maintaining SFT's in-domain performance advantage. Validated on math, medical, and tool-use domains across 4B–32B models.

### [7] SFT Memorizes, RL Generalizes

RL improves **out-of-distribution generalization**; SFT hurts it. Tested on GeneralPoints (rule-based card game) and V-IRL (visual navigation):

| Method | OOD performance change |
|---|---|
| RL | +3–11% improvement |
| SFT | Up to -79.5% degradation |

RL also improves the underlying perception capabilities of vision-language models — not just reasoning patterns.

### [8] From Atomic to Composite

SFT learns atomic skills; RL synthesizes them into composite reasoning. The optimal pipeline:
1. SFT to teach foundational skills
2. RL to compose them into higher-level generalization

Pure SFT: high in-domain, poor OOD. RL without SFT primer: struggles to acquire basic skills. SFT → RL: best compositional generalization.

### [9] Math RL Transfers to General Capabilities

RL trained only on math data generalizes broadly to non-reasoning benchmarks. SFT on the same data does not. On-policy data and the presence of a **negative gradient** (penalising incorrect responses) in the RL objective are key contributors.

---

## Key Takeaways

- **RL naturally resists catastrophic forgetting** — without any explicit replay, regularization, or architectural modification
- **The mechanism is on-policy data** — not KL penalty, not CoT, not GRPO specifically. On-policy samples keep distributional shift small
- **RL's Razor:** among all high-reward solutions, RL finds the one closest to the base model in KL — minimising forgetting as a side effect
- **SFT + EAFT** can partially close the gap: entropy-weighting the SFT loss suppresses confident-conflict tokens that cause destructive updates
- **RL generalizes; SFT memorizes** — RL improves OOD performance, SFT hurts it
- **RL is on the path to AGI:** adaptability (continual learning) is a prerequisite for general intelligence, and RL's robustness makes it a natural candidate
