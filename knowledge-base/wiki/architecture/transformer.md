# Transformer Architecture

**Related:** [[architecture/attention]] · [[architecture/positional-embeddings]] · [[training/pretraining]] · [[training/fine-tuning]] · [[inference/decoding-strategies]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]] · [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Mixture-of-Experts (MoE) LLMs - by Cameron R. Wolfe, Ph.D.]]

---

## Three Variants

| Variant | Attention | Primary use | Examples |
|---|---|---|---|
| **Encoder-only** | Bidirectional (full) | Understanding, embeddings, classification | BERT, RoBERTa |
| **Decoder-only** | Causal (masked) | Text generation, LLMs | GPT family, Llama, Claude |
| **Encoder-decoder** | Cross-attention between enc/dec | Seq2seq, translation, T5-style | T5, BART, original "Attention is All You Need" |

Modern LLMs almost exclusively use **decoder-only** architectures. The encoder is removed; the remaining decoder self-attention is masked so position `t` can only attend to positions `< t`.

---

## Decoder Block Structure

Each transformer block = two sub-layers with **pre-norm** (LayerNorm before each sub-layer, not after) and **residual connections** around both:

```
Input
  └─ LayerNorm → Causal Multi-Head Self-Attention → + residual
  └─ LayerNorm → Feed-Forward Network              → + residual
Output
```

### Causal Multi-Head Self-Attention

See [[architecture/attention]] for full mechanics. Key properties in a decoder block:
- **Causal masking** prevents attending to future positions
- **Multi-head:** run H parallel attention heads, concatenate, project — captures different relationship types
- Query, Key, Value matrices are all learned projections of the same input

### Feed-Forward Network (FFN)

Two linear layers with a hidden layer ~4× wider than the embedding dimension:
```
FFN(x) = W2 · activate(W1 · x + b1) + b2
```
Activation is typically GELU (GPT-2+) or ReLU. The FFN is where most parameters live.

### LayerNorm Placement

Original "Attention is All You Need" applied LayerNorm **after** each sub-layer (post-norm). GPT-2 and essentially all modern LLMs apply it **before** (pre-norm) — more stable training.

---

## Full GPT-2 / NanoGPT Model

```
token_embedding      [vocab_size × d_model]   — trainable lookup table
positional_embedding [context_len × d_model]  — one per position (learned)
↓ sum, dropout
12 × TransformerBlock
↓ LayerNorm
lm_head (linear)     [d_model × vocab_size]   — weight-tied to token_embedding
```

**Weight tying:** `lm_head` shares weights with the token embedding matrix. Reduces parameters, improves generalization. (Press & Wolf 2016)

**GPT-2 base config:**
```python
block_size = 1024   # context length
vocab_size = 50257  # BPE vocabulary
n_layer    = 12
n_head     = 12
n_embd     = 768    # d_model
```

---

## Key Design Decisions

| Decision | Modern choice | Reason |
|---|---|---|
| Norm placement | Pre-norm (before) | More stable training at scale |
| Activation | GELU / SwiGLU | Better than ReLU empirically |
| Positional encoding | Learned (GPT-2) or RoPE (newer) | RoPE better for length generalization |
| Weight tying | Yes (most LLMs) | Reduces params, improves performance |
| Residual connections | Around both sub-layers | Enables very deep networks |

---

## Mixture-of-Experts (MoE) Modification

The most significant architectural modification to the decoder-only transformer is replacing FFN layers with **MoE layers**. Each MoE layer contains N independent FFNs ("experts") plus a learned router that selects only K experts per token, keeping compute proportional to K·FFN cost rather than N·FFN cost.

Key tradeoff: total parameters scale with N (requiring more GPU memory to store), but FLOPs per token remain constant. This enables significantly larger models at the same inference compute budget.

See [[architecture/mixture-of-experts]] for the full MoE reference page.

---

## Historical Note

Original transformer (Vaswani et al. 2017) was encoder-decoder for translation. The decoder-only insight — that the same masked language modeling objective on raw text is sufficient for broad generalization — came from GPT (2018). See [[concepts/scaling-and-the-bitter-lesson]] and [[concepts/foundation-models]].
