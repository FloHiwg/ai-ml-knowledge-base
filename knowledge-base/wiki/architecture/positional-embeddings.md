# Positional Embeddings

**Related:** [[architecture/transformer]] · [[architecture/attention]] · [[training/tokenization]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]] · [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]]

---

## Why They Are Needed

Transformers process all tokens **in parallel** — there is no inherent notion of order. Without positional information, the model would treat "dog bites man" and "man bites dog" identically. Positional embeddings inject order information into the token representations.

---

## Types

### Learned (Absolute) Positional Embeddings

A learnable matrix of size `[context_length × d_model]` — one embedding vector per position. Added to the token embedding at the input layer.

**Used by:** GPT, GPT-2, BERT, NanoGPT  
**Pro:** Simple, works well within the training context length  
**Con:** Does not generalize beyond the maximum position seen during training

```python
# NanoGPT
self.wpe = nn.Embedding(block_size, n_embd)  # positional embeddings
pos = torch.arange(0, t)                      # position indices
x = tok_emb + self.wpe(pos)                  # add to token embedding
```

### Sinusoidal (Fixed) Positional Embeddings

Original "Attention is All You Need" encoding. Deterministic sine/cosine functions at different frequencies — no learned parameters. Each dimension `i` uses a different frequency:

```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**Pro:** Can represent any position, including those not seen in training  
**Con:** Does not generalize length particularly well in practice

### RoPE — Rotary Position Embedding (Su et al. 2021)

Encodes position as a **rotation** applied to the Query and Key vectors in attention. Instead of adding position to token embeddings, RoPE modifies Q and K so that the dot product `Q·K` naturally depends on the *relative* distance between positions.

**Used by:** LLaMA, Mistral, modern open-weight models  
**Pro:** Relative position encoding; length generalization is better than absolute; efficient  
**Key property:** `Q(pos_m) · K(pos_n)` depends only on `m - n`, not on absolute positions

### ALiBi — Attention with Linear Biases (Press et al. 2021)

Adds a fixed, position-dependent **bias** to attention logits before softmax. The bias penalizes attention scores by a linear function of distance (closer = less penalty). No positional embeddings at all in the token representation.

**Used by:** BLOOM  
**Pro:** Strong length extrapolation (train short, test long)  
**Con:** Less widely adopted than RoPE

---

## Comparison

| Method | Type | Parameters | Length extrapolation | Notes |
|---|---|---|---|---|
| Learned | Absolute | Yes (d_model × ctx_len) | Poor | GPT-2, NanoGPT |
| Sinusoidal | Absolute | None | Moderate | Original transformer |
| RoPE | Relative | None | Good | Most modern open models |
| ALiBi | Relative bias | None | Very good | Train-short-test-long |

---

## Context Window

The context window (also called `block_size` or `max_position_embeddings`) is the maximum sequence length the model can process. It is bounded by:
- The number of positional embeddings (for learned/sinusoidal)
- Memory: attention is O(n²), so long contexts are expensive

Typical ranges: GPT-2 = 1024, modern models = 8K–1M+.
