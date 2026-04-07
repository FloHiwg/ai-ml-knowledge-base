# Language Model Training and Inference From Concept to Code

**Source:** [[raw/articles/Language Model Training and Inference From Concept to Code]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Vision Transformers - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

A ground-up walkthrough of how causal language models work and how to implement them — from tokenization through pretraining to autoregressive inference — using Andrej Karpathy's NanoGPT (a clean GPT-2 reimplementation) as the concrete code reference.

---

## Prerequisites

**Transformer architecture:** The GPT family uses decoder-only transformers — stacked blocks of causal multi-head self-attention + feed-forward network. "Causal" means each token can only attend to preceding tokens (masked attention), which is what makes autoregressive generation possible.

**PyTorch tooling:**
- **DDP (Distributed Data Parallel):** Run one training process per GPU; each holds a full model copy; gradients are synchronized after each mini-batch.
- **FSDP (Fully Sharded Data Parallel):** Shards model parameters across devices — required when the model is too large for a single GPU. More common for modern large LLMs.
- **AMP (Automatic Mixed Precision):** Uses `float16`/`bfloat16` for most computation, `float32` for accumulation, with a gradient scaler to prevent underflow. Reduces memory and speeds up training.

---

## Tokens and Vocabularies

**Tokenization pipeline:**
1. Raw text → subword tokens via **Byte-Pair Encoding (BPE)** or **Byte-level BPE (BBPE)**
2. Each token maps to an integer ID (vocabulary index)
3. IDs look up **token embeddings** (a learned `vocab_size × d_model` matrix)
4. **Positional embeddings** (also learned, or via RoPE/ALiBi for length extrapolation) are added to encode position within the sequence

**Context window:** The maximum sequence length the model can process in one forward pass (NanoGPT uses 1024 tokens; modern models range from 8K to millions). The positional embedding table has exactly `context_length` entries.

---

## Pretraining: Next Token Prediction

**Objective:** Self-supervised — no labels needed. Given a sequence of tokens, predict the next token at every position. The ground truth is the input itself, shifted by one.

**Forward pass (training):**
1. Look up token and positional embeddings, add them together
2. Pass through dropout → 12 transformer blocks → LayerNorm
3. Apply linear `lm_head` → logits over vocabulary (shape: `[batch, seq_len, vocab_size]`)
4. Compute **CrossEntropy loss** across all token positions in the batch simultaneously (causal masking ensures position `t` can only see tokens `< t`)

**Key implementation detail — weight tying:** The `lm_head` linear layer shares weights with the token embedding matrix. This reduces parameter count while improving performance (Press & Wolf, 2016).

**Data loading:** Training data is stored as a flat array of token IDs. Mini-batches are constructed by randomly sampling contiguous chunks of `context_length` tokens. Targets = input shifted by one position.

---

## Inference: Autoregressive Generation

Generating text is a step-by-step loop — there is no parallel computation across output tokens:

1. Forward pass with current input sequence (no targets tensor)
2. Extract logits for the **last** token position only
3. Scale by **temperature** (`T < 1` → sharper/greedier; `T > 1` → flatter/more random)
4. *[Optional]* **Top-K filtering** — zero out all but the K most probable tokens
5. Apply **softmax** → probability distribution
6. **Sample** the next token from the distribution
7. Append sampled token to input, repeat

**Greedy decoding** = temperature → 0 (always pick the argmax). **Nucleus (top-p) sampling** = keep smallest set of tokens whose cumulative probability exceeds p.

---

## NanoGPT Implementation

NanoGPT matches GPT-2 base (~117M parameters). Key components:

### Model Config
```python
@dataclass
class GPTConfig:
    block_size: int = 1024   # context length
    vocab_size: int = 50257  # GPT-2 BPE vocabulary
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    dropout: float = 0.0
    bias: bool = True
```

### Transformer Block
Each block:
- **Causal multi-head self-attention** (masked, scaled dot-product)
- **Feed-forward network:** two linear layers with a hidden width ~4× the embedding dim
- **Pre-norm:** LayerNorm applied before each sub-layer (not after, unlike original "Attention is All You Need")
- **Residual connections** around both sub-layers

### Full Model
```
token_embedding (vocab_size × n_embd)
+ positional_embedding (block_size × n_embd)
→ dropout
→ 12 × TransformerBlock
→ LayerNorm
→ lm_head (linear, weights tied to token_embedding)
```

### Training Setup

**DDP:** Each GPU runs a separate process with a unique rank. Gradients are all-reduced after each micro-batch.

**Gradient accumulation:** Accumulate gradients over several micro-batches before updating weights — simulates a larger effective batch size without requiring more GPU memory per step.

**Learning rate schedule:**
- Short **linear warmup** (e.g., 2000 steps)
- Followed by **cosine decay** to a minimum LR for the remainder of training

**Training loop extras:**
- **Gradient clipping** (`max_norm=1.0`) to prevent gradient explosion
- **AMP loss scaling** (via `torch.cuda.amp.GradScaler`) to handle `float16` underflow

---

## Key Takeaways

- **Next token prediction is the universal pretraining objective** — the same forward pass drives both training (all positions in parallel via causal masking) and inference (one position at a time).
- **Weight tying** between token embeddings and the output head is a simple technique that reduces parameters and improves generalization.
- **Temperature and Top-K/Top-p** are the main knobs for controlling generation quality vs. diversity at inference time.
- **DDP vs FSDP:** DDP works when each device can hold a full model copy; FSDP is needed for models too large for a single device.
- **Gradient accumulation** decouples effective batch size from GPU memory — essential for training with large batches on limited hardware.
- The full training pipeline is less than ~300 lines of PyTorch; understanding NanoGPT gives a concrete mental model that scales directly to modern LLMs.
