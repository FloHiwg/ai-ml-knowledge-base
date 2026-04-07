# Tokenization

**Related:** [[training/pretraining]] · [[architecture/transformer]] · [[architecture/positional-embeddings]]  
**Sources:** [[summaries/Language Model Training and Inference From Concept to Code]]

---

## Pipeline

```
Raw text  →  Tokenizer  →  Token IDs  →  Token Embeddings  →  + Positional Embeddings
```

---

## Tokenization Algorithms

### BPE — Byte Pair Encoding

The most common approach for LLMs. Starts from characters and iteratively merges the most frequent adjacent pair into a new token until a target vocabulary size is reached.

```
"lower" → ["l", "o", "w", "e", "r"]
after merges: ["low", "er"]
```

**Properties:**
- Vocabulary size is a hyperparameter (typically 30K–50K)
- Balances character-level flexibility with word-level efficiency
- Unknown words are broken into subword pieces — no truly "unknown" token

### BBPE — Byte-level BPE

Operates on raw bytes rather than characters. Every byte (0–255) is always representable, so there are no out-of-vocabulary tokens even for arbitrary Unicode text.

**Used by:** GPT-2 (50,257 token vocabulary = 256 bytes + 50,000 BPE merges + 1 special token)

---

## Token Embeddings

A learned lookup table: `vocab_size × d_model`. Each token ID maps to a dense vector of dimension `d_model`. This is trained end-to-end with the rest of the model — the embeddings encode semantic and syntactic properties of tokens.

**Weight tying:** In most LLMs (including GPT-2/NanoGPT), the token embedding matrix is **shared with the output classification head** (`lm_head`). Reduces parameters significantly and improves performance.

---

## Positional Embeddings

Added to token embeddings before the first transformer block to inject order information. See [[architecture/positional-embeddings]] for full details (learned, RoPE, ALiBi).

---

## Context Window

The maximum number of tokens the model can process in a single forward pass. Bounded by:
- The number of positional embeddings (for learned schemes)
- Memory: self-attention is O(n²) in sequence length

GPT-2: 1024. Llama 3: 8K. Claude: up to 200K+.

Practical note: You can technically truncate inputs to shorter than the context window — the model will still work, just without the full context.

---

## Vocabulary Size Trade-offs

| Smaller vocabulary | Larger vocabulary |
|---|---|
| Fewer parameters in embedding layer | More parameters, better coverage |
| More tokens per word | Fewer tokens per word |
| Better generalization on rare words | Better handling of common words |
| Slower training (longer sequences) | Faster (shorter sequences) |

Most modern LLMs use 32K–128K vocabulary sizes.
