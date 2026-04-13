# Attention Mechanism

**Related:** [[architecture/transformer]] · [[architecture/vision-transformers]] · [[architecture/graph-neural-networks]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]] · [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.]]

---

## Core Intuition

Attention lets every token (or patch, or node) **look at every other** and weight how much to incorporate from each. Instead of a fixed-size hidden state (the bottleneck of RNNs), attention gives each position direct access to all positions — weighted by relevance.

*"What am I looking for? Who has it? What do I take from them?"*

---

## Scaled Dot-Product Attention

Given input `X`, compute three projections:

```
Q = X W_Q    (Query  — "what am I looking for?")
K = X W_K    (Key    — "what do I offer?")
V = X W_V    (Value  — "what content do I carry?")

Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) · V
```

- `Q K^T` produces a score matrix: how much each query matches each key
- `/ sqrt(d_k)` — scaling prevents dot products from growing too large, keeping softmax gradients stable
- `softmax(...)` normalizes scores to a probability distribution (attention weights)
- Multiply by `V` to produce a weighted sum of value vectors

---

## Causal (Masked) Self-Attention

In decoder-only models, future positions must be invisible at training and inference time. This is enforced by **masking** — adding `-∞` to all positions `j > i` before softmax, so they become 0 after softmax.

```
Mask[i][j] = 0      if j <= i   (allowed)
           = -inf   if j > i    (forbidden)
```

This makes the architecture autoregressive: output at step `t` depends only on inputs at steps `0..t`.

**Bidirectional attention** (BERT / encoder-only) uses no mask — each token attends to all others. Better for understanding tasks; cannot generate autoregressively.

---

## Multi-Head Attention

Run `H` independent attention heads in parallel, then concatenate and project:

```
head_h = Attention(X W_Q^h, X W_K^h, X W_V^h)
MHA(X) = concat(head_1, ..., head_H) · W_O
```

Each head uses `d_k = d_model / H` dimensions. Multiple heads let the model attend to different relationship types simultaneously (syntax, coreference, proximity, etc.).

---

## Cross-Attention (Encoder-Decoder)

In encoder-decoder models, the decoder's Keys and Values come from the encoder output, while Queries come from the decoder's own state:

```
CrossAttention(Q_dec, K_enc, V_enc)
```

Used in T5-style seq2seq models and in GOTR (Graph-of-Thought fine-tuned model) to fuse text, image, and graph signals.

---

## Attention in Vision Transformers

In ViT, the "tokens" are image patches. Attention operates over patches instead of words — same mechanism, different inputs. See [[architecture/vision-transformers]].

---

## Attention in Graph Networks

**Graph Attention Networks (GATs)** use attention to weight neighbor aggregation in GCNs — instead of averaging all neighbors equally, learn which neighbors matter more. Analogue of multi-head self-attention applied to graph structure. See [[architecture/graph-neural-networks]].

---

## Computational Complexity

Standard attention is `O(n²)` in sequence length — every token attends to every other. This is why context windows were historically capped (1K–8K) and why efficient attention variants (FlashAttention, sparse attention) exist.

---

## Efficient Attention Variants

Standard MHA has O(n²) complexity and stores full K and V tensors per layer per token in the KV cache. Several variants reduce this cost:

| Variant | Mechanism | KV cache reduction |
|---|---|---|
| **Multi-Query Attention (MQA)** | Single K/V head shared across all Q heads | Large |
| **Grouped-Query Attention (GQA)** | K/V heads shared within groups of Q heads | Moderate; used in Mistral/Mixtral |
| **Sliding Window Attention (SWA)** | Attention over fixed local window; stacked layers expand effective context | Reduces per-layer compute |
| **Multi-head Latent Attention (MLA)** | Low-rank joint projection stores a single latent vector; upsampled at inference to recover K/V | 93% KV cache reduction vs 67B dense |

MLA (DeepSeek-v2) is the most aggressive: K/V projections are computed from a compressed latent vector that is stored instead of the full K/V matrices. At inference, one linear projection restores the full representations. No significant accuracy cost observed.

See [[architecture/mixture-of-experts]] for the MoE context where MLA appears.

---

## Key Properties

| Property | Why it matters |
|---|---|
| Parallelizable | All positions computed simultaneously (unlike RNNs) |
| Long-range dependencies | Any two positions can interact directly regardless of distance |
| Interpretable (roughly) | Attention weights are inspectable |
| O(n²) memory/compute | Bottleneck for very long sequences |
