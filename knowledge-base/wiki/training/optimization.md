# Optimization

**Related:** [[training/pretraining]] · [[training/distributed-training]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]]

---

## Learning Rate Schedule

LLM pretraining uses a two-phase schedule:

```
Phase 1: Linear warmup (e.g., 2000 steps)
         LR ramps from ~0 to peak_lr

Phase 2: Cosine decay (remainder of training)
         LR decays from peak_lr to min_lr (e.g., peak_lr / 10)
```

**Why warmup?** Early in training, gradients are noisy — a high LR causes instability. Starting small and ramping up stabilizes the first steps.

**Why cosine decay?** Smooth reduction; model can benefit from high LR during most of training, then settle into fine refinement.

```python
def get_lr(it, warmup_iters, lr_decay_iters, learning_rate, min_lr):
    if it < warmup_iters:
        return learning_rate * it / warmup_iters   # linear warmup
    if it > lr_decay_iters:
        return min_lr
    # cosine decay
    decay_ratio = (it - warmup_iters) / (lr_decay_iters - warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return min_lr + coeff * (learning_rate - min_lr)
```

---

## Gradient Clipping

Caps the global L2 norm of all gradients to `max_norm` (typically 1.0):

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
```

Prevents catastrophically large updates when gradients spike (common in early training or near data outliers). Essential with AMP — apply *after* unscaling (see [[training/distributed-training]]).

---

## Optimizer

Standard choice is **AdamW** (Adam with decoupled weight decay):

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, 
                               betas=(0.9, 0.95), weight_decay=0.1)
```

- `β1 = 0.9`: momentum for first moment (gradient mean)
- `β2 = 0.95`: momentum for second moment (gradient variance) — lower than default 0.999 is common for LLM training
- Weight decay applied to weights only, not biases or LayerNorm parameters

---

## Weight Initialization

GPT-2-style initialization:
- Most weights: normal distribution `N(0, 0.02)`
- Residual projection layers (output of attention and FFN): scaled by `1/sqrt(2 × n_layers)` — prevents variance from accumulating through deep residual stacks

---

## Hyperparameter Sensitivity

LLM pretraining is sensitive to:
- Peak learning rate (too high → divergence; too low → slow/underfit)
- Batch size (affects gradient variance and effective LR)
- Warmup duration (too short → instability)
- Weight decay (regularization)

Most practitioners follow established recipes (e.g., Chinchilla scaling laws for compute-optimal batch size / LR) rather than searching from scratch.
