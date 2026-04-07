# Decoding Strategies

**Related:** [[architecture/transformer]] · [[training/pretraining]] · [[inference/prompting-and-reasoning]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]]

---

## Autoregressive Generation

Generating text is a **step-by-step loop** — unlike training, which processes all positions in parallel:

```
loop:
  1. Forward pass with current token sequence
  2. Extract logits for the LAST position only
  3. Apply decoding strategy to get next token
  4. Append token to sequence
  5. Repeat until stop condition (EOS token or max length)
```

This is inherently sequential — each step depends on the previous output. This is the main inference bottleneck for LLMs.

---

## Sampling Strategies

### Greedy Decoding

Always pick the highest-probability token:
```
next_token = argmax(logits)
```

Fast and deterministic. Often produces repetitive, low-quality text for open-ended generation (the model gets "trapped" in high-probability loops).

### Temperature Scaling

Divide logits by a temperature `T` before softmax:
```
P(token) = softmax(logits / T)
```

| Temperature | Effect |
|---|---|
| `T → 0` | Greedy (deterministic, sharp) |
| `T = 1.0` | Raw model probabilities |
| `T > 1.0` | Flatter distribution (more random) |
| `T < 1.0` | Sharper distribution (more conservative) |

**Rule of thumb:** `T ≈ 0.7–0.9` for creative tasks; `T ≈ 0.0–0.3` for factual/precise tasks.

### Top-K Sampling

Keep only the `K` most likely tokens, set all others to `-∞`, then sample:
```python
top_k_indices = logits.topk(K).indices
logits[~top_k_indices] = -float('inf')
next_token = sample(softmax(logits))
```

Prevents sampling from very unlikely tokens. Typical values: K = 40–100.

### Nucleus (Top-p) Sampling

Keep the smallest set of tokens whose cumulative probability exceeds `p`, sample from them:
```
Sort tokens by probability descending
Cumulative sum: keep tokens until sum ≥ p
Sample from this dynamic set
```

**Advantage over Top-K:** Adapts to the distribution. When the model is confident (one token has 90% probability), the nucleus is small. When the model is uncertain, the nucleus is larger.

Typical values: `p = 0.9–0.95`.

---

## Temperature vs Evaluation

**Critical:** For statistical LLM evaluation, **do not change the sampling temperature** just to reduce variance in evaluation scores. This changes the underlying response distribution, making results incomparable to the original model configuration. See [[evaluation/statistical-evaluation]].

---

## Inference vs Training Forward Pass

| | Training | Inference |
|---|---|---|
| Targets | Required (next token ground truth) | Not provided |
| Positions processed | All simultaneously (parallel) | One new position per step |
| Loss computed | Yes | No |
| Causal mask | Needed for parallelism | Naturally satisfied (prefix only) |

The forward pass code is the same — just pass `targets=None` during inference.

---

## KV Cache

In practice, inference is accelerated with a **KV cache** — storing the Key and Value tensors for all previously generated tokens so they don't need to be recomputed at each step. This reduces per-step compute from O(n) to O(1) (for the new token only).

Most production LLM frameworks (vLLM, TGI, llama.cpp) implement KV caching automatically.
