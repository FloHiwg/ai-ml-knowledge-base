# Mixture-of-Experts (MoE)

**Related:** [[architecture/transformer]] · [[architecture/attention]] · [[training/pretraining]] · [[concepts/scaling-and-the-bitter-lesson]]
**Sources:** [[summaries/Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.]]

---

## Core Concept

MoE layers replace the feed-forward network (FFN) in a transformer block with N independent FFN "experts" plus a learned router that selects only K of them per token. This introduces **conditional computation** (sparsity): total parameter count grows with N but compute per token stays constant — determined only by K active experts.

```
Dense FFN:  token → single FFN → output
MoE layer:  token → router → top-K experts → weighted sum of their outputs
```

Every P-th transformer block is converted to an MoE layer (interleaved MoE). Other blocks remain untouched. Common strides: P = 2, 4, or 6.

---

## Routing Mechanism

For each token, a linear projection followed by softmax produces a probability distribution over N experts. The top-K highest-probability experts are selected:

```
logits  = W_gate @ token_vector      # [N]
probs   = softmax(logits)            # [N]
chosen  = top_k(probs, K)
output  = Σ_{i in chosen} probs[i] · E_i(token)
```

### Routing Collapse

Without regularization, the router converges to always selecting the same few experts. The failure is self-reinforcing: frequently selected experts receive more gradient, improve faster, get selected even more. The resulting model is effectively a dense model with wasted capacity.

---

## Load Balancing

Three auxiliary losses combat routing collapse — all added on top of the standard next-token prediction loss:

| Loss | Source | What it penalizes |
|---|---|---|
| **Importance loss** | [1] Shazeer et al. 2017 | High variance in per-expert summed probabilities |
| **Load balancing loss** | [2] Switch Transformers | Imbalance in both router probability fraction AND token dispatch fraction per expert |
| **Router z-loss** | [3] ST-MoE | Large pre-softmax logits that cause float32 round-off errors during training |

Standard practice: combine load balancing [2] and z-loss [3]. The z-loss focuses on training stability; the load balancing loss focuses on utilization.

---

## Expert Capacity

For hardware efficiency (static batch sizes on GPUs), each expert has a maximum token budget per batch:

```
capacity = (tokens_per_batch / N_experts) × capacity_factor
```

Tokens routed to an overloaded expert are **dropped** — their representation passes to the next layer unchanged via the residual connection. A capacity factor of 1.0 assumes perfect balance; >1.0 provides slack. Typical: 1.25 training / 2.0 evaluation.

---

## Shared Experts (DeepSeek)

A subset of experts are designated "shared" — every token always passes through them. Routing only applies to the "routed" experts:

```
output = shared_output + Σ_{i in top-K routed} probs[i] · E_i(token)
```

Motivation: shared experts hold common/general knowledge, reducing redundancy among routed experts. The number of shared experts should be much smaller than the number of routed experts to preserve sparsity benefits.

---

## Fine-Grained Experts

Using more, smaller experts (e.g., 16 experts with K=4 instead of 8 with K=2) increases the number of distinct expert combinations exponentially. DBRX uses 16 experts → 65× more combinations than Mixtral (8 experts). DeepSeek uses 256 routed + 1 shared. Fine-grained experts improve quality at the cost of more routing overhead.

---

## Routing Behavior (Empirical)

Experiments on Mixtral and OpenMoE reveal:

- **Experts do NOT specialize by topic or domain** — token routing is not clustered by subject matter
- **Context-Independent Specialization** (OpenMoE): routing is primarily driven by the token ID, not the surrounding context — the same word ("an", "=") almost always routes to the same expert
- **Syntactic/positional patterns**: consecutive sequence tokens and syntactic structures (indentation, keywords) often share an expert
- **Routing dynamics solidify early** in pretraining and rarely change; hard to fix during post-training

---

## Pros and Cons

**Benefits:**
- Scale capacity without proportional compute — better quality/compute tradeoff than dense models
- Switch Transformer: 7× pretraining speedup over dense equivalent
- Inference efficiency: only K active experts per token

**Drawbacks:**
- Higher memory: all experts must be loaded (distributed across GPUs in practice)
- Training instabilities: require load balancing losses, careful initialization
- Fine-tuning difficulty: distribution shift destabilizes routing; mix instruction data into pretraining to mitigate
- Sensitivity to mixed-precision and hyperparameter settings

---

## MoE LLMs at a Glance

| Model | Total params | Active params | Experts (K active) | Key innovation |
|---|---|---|---|---|
| **Mixtral 8×7B** | 47B | 13B | 8 (K=2) | MoE extension of Mistral-7B; open weights |
| **Mixtral 8×22B** | 141B | 39B | 8 (K=2) | Larger Mixtral; 64K context; function calling |
| **Grok-1** | 314B | ~75B | 25% active | xAI; Apache 2.0; base model only |
| **DBRX** | 132B | 36B | 16 (K=4) | Fine-grained experts; 4× training efficiency |
| **DeepSeek-v2** | 236B | 21B | fine-grained + shared | MLA for KV cache (93% reduction) |
| **DeepSeek-v3** | 671B | 37B | fine-grained + shared | FP8 training; MTP objective; ~$5.6M training cost |

---

## Multi-Head Latent Attention (MLA)

Introduced by DeepSeek-v2. Reduces KV cache memory via low-rank projection:

- Standard MHA: stores full K and V matrices per layer per token
- MLA: stores a single small **latent vector**; upsamples at inference time to reconstruct K/V
- **Result:** 93% KV cache reduction vs a 67B dense model, with no significant performance loss

See [[architecture/attention]] for standard attention mechanics.

---

## Multi-Token Prediction (MTP)

Introduced by DeepSeek-v3. Extends the standard next-token objective to predict D future tokens sequentially:

```
standard NTP:  predict x_{t+1} from x_{1..t}
MTP (D=2):     predict x_{t+1} and x_{t+2} from x_{1..t}
```

Additional prediction modules are attached during training and discarded afterwards. Richer training signal → improved training efficiency and final model quality. MTP modules can also support speculative decoding at inference time, though DeepSeek uses them purely for training quality.

---

## Auxiliary-Loss-Free Load Balancing (DeepSeek-v3)

Alternative to the standard auxiliary load balancing loss: add a bias term to each expert's routing score that adjusts dynamically each iteration:

```
if expert was overloaded this step: bias -= γ
if expert was underloaded this step: bias += γ
```

The bias affects only expert selection (top-K), not the router probability weights used for output computation. Eliminates performance deterioration from auxiliary loss scaling, while still achieving balanced expert utilization. A small auxiliary loss is still used in practice.
