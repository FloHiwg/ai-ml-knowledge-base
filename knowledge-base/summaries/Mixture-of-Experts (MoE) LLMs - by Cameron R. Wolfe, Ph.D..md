# Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.

**Source:** [[raw/articles/Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.]]
**Author:** Cameron R. Wolfe, Ph.D.
**Related:** [[summaries/Language Model Training and Inference From Concept to Code]] · [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

MoE layers replace the feed-forward network in a decoder-only transformer with multiple independent feed-forward "experts" plus a learned routing mechanism that selects only a subset of experts per token. This introduces **sparsity**: total parameters increase substantially but active parameters per token remain constant, decoupling model capacity from compute cost. MoEs allow training and running larger models than would otherwise be feasible at the same compute budget.

---

## Architecture Fundamentals

### What Are Experts?

Each "expert" is an independent copy of the standard FFN from a transformer block, with its own weights:

```
N experts:  E_1, E_2, ..., E_N
Each expert: two linear layers + non-linear activation (same as a standard FFN)
```

Only every P-th transformer layer is converted to an MoE layer (interleaved MoE). Common values: P = 2, 4, or 6. This controls the total parameter count and the cost/performance tradeoff.

### Routing Algorithm

For each token vector, a linear layer projects it to N logits (one per expert). Softmax converts these to a probability distribution. The top-K experts are selected:

```
router_logits = token_vector @ W_gate          # shape: [N]
router_probs  = softmax(router_logits)
selected      = top_k(router_probs, k=K)       # e.g., K=2
output        = weighted_sum(E_i(token) for i in selected)
```

**Routing collapse**: Without regularization, the router converges to always selecting the same few experts ("self-reinforcing" imbalance — favored experts are trained faster, selected more).

### Active vs Total Parameters

Total parameters = all expert weights + all shared/non-expert weights. Active parameters = only the K selected experts per MoE layer + all non-expert weights. Compute is proportional to active parameters, not total.

---

## Load Balancing and Auxiliary Losses

Three mechanisms to prevent routing collapse:

| Loss | Source | What it controls |
|---|---|---|
| **Importance loss** | [1] | Squared CV of per-expert probability sums — encourages equal probability across experts |
| **Load balancing loss** | [2] | Dot product of (router probability fraction, token dispatch fraction) — captures both importance and token count balance |
| **Router z-loss** | [3] | Penalizes large pre-softmax logits — prevents round-off errors that destabilize training at scale |

In practice: load balancing loss [2] + router z-loss [3] are used together on top of the standard language modeling loss.

---

## Expert Capacity

To support static batch sizes (needed for hardware efficiency), each expert has a fixed capacity — the maximum number of tokens it can process per batch:

```
capacity = (tokens_per_batch / N_experts) × capacity_factor
```

Tokens routed to an expert beyond its capacity are **dropped** and pass through the residual connection unchanged. A capacity factor of 1.0 = perfectly balanced routing assumed; >1.0 provides buffer for imbalance. Typical: 1.25 during training, 2.0 during evaluation.

---

## Shared Experts (DeepSeek Innovation)

All tokens always pass through a set of "shared experts" (dense, non-routed); sparse routing applies only to the "routed experts." This:
- Stores common, general knowledge in shared experts
- Reduces redundant information duplication across routed experts
- Output = shared_experts_output + weighted_sum(selected_routed_experts_output)

---

## MoE LLMs in Practice

### Mixtral 8×7B (Mistral AI)

- **Architecture:** Mistral-7B base + every layer converted to MoE with 8 experts, K=2 active
- **Scale:** 47B total / 13B active parameters; 32K context
- **Base:** GQA (grouped-query attention) + Sliding Window Attention (SWA)
- **Results:** Outperforms LLaMA-2-70B despite fewer active parameters; excels at code, math, multilingual
- **Routing insight:** Experts do NOT specialize by topic/domain. Routing follows syntactic structure: same token often goes to the same expert regardless of context; sequential/positional patterns observed

### Mixtral 8×22B

- 141B total / 39B active; 64K context; native function calling; particularly strong at coding and math

### Grok-1 (xAI)

- 314B total / ~70-80B active (25% active); Apache 2.0 license; base model only (no post-training details)
- Grok-1.5 added better reasoning and 128K context; likely improved via post-training from same base

### DBRX (Databricks / Mosaic)

- **Scale:** 132B total / 36B active; 16 experts with K=4 active (fine-grained MoE)
- **Fine-grained insight:** Larger number of smaller experts → 65× more expert combinations → better quality
- **Data quality:** New pretraining data 2× more token-efficient than prior data (tested in isolation)
- **Curriculum learning:** Domain-specific datasets upsampled late in training for quality boost
- **Efficiency:** 4× less compute end-to-end vs prior pipeline; 2× faster inference than LLaMA-2-70B
- **Context:** 32K tokens; GPT-4 tokenizer (tiktoken) for token efficiency

### OpenMoE

- Suite of open-source decoder MoEs (650M–34B params); 16 or 32 experts per layer; K=2
- **Context-Independent Specialization**: routing dictated primarily by token ID, not context — same token routes to same expert regardless of surrounding words
- **Routing issues**: tokens later in sequences dropped more; hurts multi-turn chat
- **SFT domain gap**: routing dynamics learned during pretraining become unstable when distribution changes at SFT time — fix: mix instruction-following data into pretraining

### DeepSeek-v2

- **Scale:** 236B total / 21B active; fine-grained experts + shared experts
- **MLA (Multi-head Latent Attention):** Low-rank KV compression — stores a small latent vector instead of full key/value projections. Reduces KV cache by 93% vs a 67B dense model with no performance loss
- **Device-level load balancing:** Extra auxiliary losses encourage balanced computation and communication across devices in distributed training

### DeepSeek-v3

- **Scale:** 671B total / 37B active; pretrained on 14.8T tokens
- **Multi-Token Prediction (MTP):** Predicts D future tokens (not just 1) sequentially via additional modules; richer training signal improves performance and training efficiency; modules discarded after training
- **Auxiliary-loss-free load balancing:** Per-expert bias terms added/subtracted each iteration based on over/underload; only affects expert selection (top-K), not router probabilities
- **FP8 training:** First validation of 8-bit mixed precision at this scale
- **Training cost:** ~$5.6M total H800 GPU hours; no loss spikes or rollbacks
- **Post-training:** Two-stage SFT for context extension (32K → 128K), then RLHF; R1 reasoning capabilities distilled in

---

## Pros and Cons of MoEs

**Benefits:**
- Scale model capacity without proportional compute increase
- Better compute-quality tradeoff than dense models at same active parameter count
- Switch Transformer reported 7× pretraining speedup over dense equivalent
- Efficient inference: low active parameter count → fast per-token compute

**Drawbacks:**
- More memory required (must store all experts across GPUs)
- Training instabilities (addressed by load balancing losses, z-loss, careful initialization)
- Hard to fine-tune — prone to overfitting; domain shift triggers routing instability
- Sensitive to mixed-precision settings and hyperparameters

---

## Key Takeaways

- MoEs replace FFN layers with N independent expert FFNs + a learned router that selects K experts per token; total params >> active params
- Routing collapse is the core failure mode; load balancing loss + router z-loss are standard mitigations
- Expert capacity (with token dropping) enables static batch sizes for hardware efficiency
- Experts empirically do NOT specialize by topic/domain; routing follows syntactic/token-ID patterns
- Fine-grained experts (more, smaller experts) allow exponentially more combinations → better quality (DBRX, DeepSeek)
- Shared experts (DeepSeek) store common knowledge to reduce redundancy among routed experts
- MLA (DeepSeek-v2) reduces KV cache 93% via low-rank projection — critical at scale
- MTP (DeepSeek-v3) extends next-token prediction to D future tokens for a richer training signal
- MoEs are hard to fine-tune due to routing instability under distribution shift — mix instruction data into pretraining
