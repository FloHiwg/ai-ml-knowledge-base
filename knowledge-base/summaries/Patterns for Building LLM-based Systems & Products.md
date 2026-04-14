# Patterns for Building LLM-based Systems & Products

**Source:** [[raw/articles/Patterns for Building LLM-based Systems & Products]]
**Author:** Eugene Yan
**Related:** [[summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG)]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models)] · [[summaries/The Anatomy of an LLM Benchmark]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

A practitioner's taxonomy of seven patterns for building reliable LLM-based systems. Organized along two axes: *improving performance vs. reducing cost/risk* and *closer to the data vs. closer to the user*. The patterns build on each other — evals gate fine-tuning decisions, RAG extends knowledge, guardrails protect outputs, and feedback loops close the improvement cycle.

---

## Pattern 1: Evals

### Automated Metrics

Four text generation metrics, each measuring a different property:

**BLEU (Bilingual Evaluation Understudy):** Precision-based n-gram overlap. Measures what fraction of generated n-grams appear in the reference. Adds a **brevity penalty** to penalize short outputs that game precision. Used in machine translation.

**ROUGE (Recall-Oriented Understudy for Gisting Evaluation):** Recall-based n-gram overlap. Measures what fraction of reference n-grams appear in the generated text.
- ROUGE-N: n-gram recall
- ROUGE-L: Longest Common Subsequence — captures sentence-level structure
- ROUGE-S: Skip-gram co-occurrences — allows gaps between matched words

**BERTScore:** Contextual embedding similarity. Embeds tokens from both candidate and reference using BERT; computes cosine similarity for each reference token against all candidate tokens; takes max (greedy matching). Aggregates as Precision (P), Recall (R), and F1. Captures semantic similarity that n-gram metrics miss entirely.

**MoverScore:** Applies **Soft WMD (Word Mover's Distance)** to align token embeddings. Uses BERT contextual embeddings with idf-weighting. Allows many-to-one token mappings (unlike BERTScore's one-to-one). Computes the minimum "transport cost" to move probability mass from candidate tokens to reference tokens — optimal transport applied to language.

### Metric Pitfalls

All automated metrics can be gamed and have known failure modes:
- BLEU/ROUGE miss paraphrases and semantic equivalence
- BERTScore depends heavily on the embedding model's domain coverage
- None are reliably aligned with human judgment on open-ended generation

### MMLU Implementation Variance

The same model can receive substantially different MMLU scores depending on which evaluation harness is used (original Hendrycks, HELM, EleutherAI's lm-eval). Sources of variance include few-shot prompt format, instruction/chat template, how options are presented, and whether probabilities or sampling are used. **Implication:** model rankings from MMLU comparisons are only valid when the same harness is used throughout.

### LLM-as-a-Judge and G-Eval

G-Eval (Liu et al. 2023) uses Auto-CoT (LLM generates evaluation criteria and steps) combined with **logprob weighting** — asks the model to score on a 1–5 scale and computes the expected score as `sum(score × P(token))` across all score tokens. This achieves Spearman correlation of 0.514 with human evaluations on summarization — significantly above traditional metrics.

For LLM-as-a-judge more broadly, see [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]].

### Eval-Driven Development

Build evals *before* building features. A good eval suite allows you to catch regressions, compare system changes systematically, and make release decisions with confidence. The same investment in an eval suite pays off more over time than any individual system improvement.

---

## Pattern 2: RAG

### Dense Passage Retrieval (DPR)

DPR (Karpukhin et al. 2020) trains two **bi-encoders** — one for queries, one for passages — using contrastive learning on (query, positive passage, negative passages) triplets from QA datasets. Creates a FAISS index of passage embeddings for ANN search. Retrieval via dot-product similarity between query and passage vectors.

### Original RAG Paper (Lewis et al. 2020)

RAG = DPR retriever + BART generative model. Two variants:
- **RAG-Sequence:** Retrieves K documents once; generates the full answer conditioned on each; marginalizes over documents
- **RAG-Token:** Retrieves for *each* generated token; allows different documents to contribute different parts of the answer

### Fusion-in-Decoder (FiD)

FiD (Izacard & Grave 2020) solves the *passage count scaling* problem:
- Encodes each retrieved passage **independently** (linear cost with passage count)
- Decoder attends **jointly** over all encoded passages via cross-attention
- Scales to 100+ passages while keeping encoding cost linear

More passages → linearly more encoding, but the decoder can attend to all simultaneously. Strong performance on open-domain QA.

### RETRO: Retrieval During Pretraining

RETRO (Borgeaud et al. 2022) integrates retrieval into the pretraining loop rather than inference:
- Retrieves from a 2 trillion token database during training
- Uses **chunked cross-attention** to attend to retrieved passages
- Only 10% of model weights involve retrieval — "RETRO-fitting" existing models requires updating only these layers
- Achieves GPT-3 performance at 25× fewer parameters (7B vs 175B)

### HyDE: Hypothetical Document Embeddings

HyDE (Gao et al. 2022) solves the query-document distribution mismatch: queries are short and syntactically different from the long passages they should retrieve.

1. Use an LLM to generate a **hypothetical document** that would answer the query (doesn't need to be factually correct)
2. Embed the hypothetical document
3. Use that embedding to search the real corpus

The hypothetical document occupies similar embedding space to real passages, bridging the distribution gap. **No labeled training data required** — useful for zero-shot or domain-specific retrieval.

### Embedding Models

| Model | Notes |
|---|---|
| **Word2vec / fastText** | Word-level; no context; fastText handles OOV via subword units |
| **sentence-transformers** | Standard library; many pre-trained models on various domains |
| **E5** | MS Research; state-of-the-art on BEIR; instruction-prefixed embeddings |
| **Instructor** | Instruction-tuned; specify task type in the prompt |
| **GTE** | Alibaba DAMO; strong multilingual performance |

Recommendation: evaluate domain-specific recall before committing to an embedding model. Off-the-shelf models can fail on specialized terminology.

### RAG vs Fine-tuning

RAG substantially outperforms continued pretraining or fine-tuning for knowledge injection (Ovadia et al. 2023). Combining RAG + fine-tuning does not consistently beat RAG alone. Fine-tuning adjusts *output format* more than *knowledge content* — pretraining is where knowledge is encoded.

---

## Pattern 3: Fine-tuning

### Transfer Learning and Alignment

Fine-tuning history: ULMFiT → BERT (masked LM) → GPT → T5 (seq2seq) → InstructGPT (RLHF). Each represents a shift in how pre-trained representations are adapted. See [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] for alignment-focused fine-tuning.

### Soft Prompt Tuning (Lester et al. 2021)

Add a small number of trainable tokens to the **input embedding layer only**. All model weights frozen. The "prompt" is not natural language — it's a floating-point tensor optimized by gradient descent.
- Parameter count: `num_tokens × embedding_dim` (e.g., 20 × 768 = 15,360 params)
- At small model scales (<1B), significantly weaker than fine-tuning
- At 10B+ scale, approaches full fine-tuning performance

### Prefix Tuning (Li & Liang 2021)

Similar to soft prompt tuning but adds trainable vectors to **every transformer layer's K/V pairs**, not just the input. A separate MLP reparameterizes the prefix to stabilize training.
- **~0.1% of parameters** (vs full fine-tuning)
- Outperforms full fine-tuning in **low-data regimes** — less risk of overfitting to few examples
- Strong on structured generation tasks (table-to-text, code)

### Adapter Layers (Houlsby et al. 2019)

Insert small **bottleneck FFN modules** between transformer sub-layers: down-project → nonlinearity → up-project, with a residual connection. All original weights frozen.
- **~3.6% of parameters** (depends on bottleneck dimension)
- Within **0.4% of full fine-tuning** performance on GLUE (results from original Houlsby paper)
- More inference latency than LoRA (extra sequential FFNs), but modular and composable

### LoRA (Hu et al. 2021)

See [[wiki/training/peft-and-lora]] for full details. Key: low-rank decomposition of weight updates; zero latency at inference (adapter merged into weights).

### QLoRA (Dettmers et al. 2023)

Enables fine-tuning of 65B+ models on a **single GPU** by combining:
1. **4-bit NF4 quantization** (Normal Float 4) — optimal for normally distributed weights
2. **Double quantization** — quantize the quantization constants themselves, saving ~0.4 bits/param
3. **Paged optimizers** — offload optimizer states to CPU RAM when GPU memory spills

Memory comparison: 65B model
- Full BF16 fine-tuning: >780GB VRAM (10+ A100 GPUs)
- QLoRA: **~48GB** (1–2 GPUs)

Performance: approaches full BF16 fine-tuning on most benchmarks despite quantization.

---

## Pattern 4: Caching

Three caching strategies for LLM systems:

| Strategy | Mechanism | Best for |
|---|---|---|
| **Semantic caching** | Store (embedding, response); on new query, check cosine similarity; return cached response if above threshold | Repeated paraphrased queries (FAQ-style) |
| **Item ID caching** | Cache responses keyed by exact content ID (document hash, product ID) | RAG chunks, product descriptions |
| **Pre-computation** | Compute and cache responses for known query distributions offline | High-traffic predictable queries |

**GPTCache** is a library implementing semantic similarity caching with pluggable backends. Threshold tuning is important — too aggressive collapses semantically different queries.

---

## Pattern 5: Guardrails

Five layers of validation:

| Layer | What it checks | Tools |
|---|---|---|
| **Structural** | Output format (JSON, XML, schema compliance) | Guidance, token healing, regex validators |
| **Syntactic** | Grammar, sentence well-formedness | NLTK, spaCy, dependency parsers |
| **Semantic/Factuality** | Faithfulness to source; NLI consistency | NLI models, SelfCheckGPT, NeMo-Guardrails |
| **Safety** | Toxic content, PII leakage, off-topic | Perspective API, LLM classifiers |
| **Input** | Prompt injection detection, input validation | Custom classifiers, blocklists |

### Guidance and Token Healing

**Guidance** (Microsoft) constrains generation at the token level — outputs must match a specified grammar or schema. At generation time, only tokens consistent with the allowed grammar are valid choices, making format violations structurally impossible.

**Token healing** addresses a quirk of BPE tokenization: boundary tokens at the end of a prompt may be sub-optimal. Token healing backtracks one token and regenerates with full probability over the complete token, avoiding format failures from tokenization artifacts.

### NeMo-Guardrails

NVIDIA's NeMo-Guardrails uses LLM-based validation via programmable "rails" defined in Colang (a domain-specific language). Supports:
- Input rails (screen incoming messages)
- Dialog rails (control conversation flow)
- Output rails (validate responses before returning)

Integrates with LangChain and other agent frameworks.

### SelfCheckGPT

Detect hallucinations by sampling multiple responses to the same prompt and checking consistency. Consistent facts across samples → likely grounded. Inconsistent "facts" → likely hallucinated. No reference document required.

---

## Pattern 6: Defensive UX

Three frameworks for designing LLM interfaces that set correct user expectations:

### Microsoft HAI Guidelines (18 guidelines)

Key principles: help users calibrate trust ("I'm not sure about this"), make confidence/uncertainty visible, always allow users to correct outputs, explain *why* the model responded as it did, and provide graceful failure modes.

### Google PAIR Guidebook (23 patterns)

Patterns for human-AI interaction: show model reasoning, explain data sources, handle disagreement constructively, communicate confidence levels. Covers both chat and embedded AI features.

### Apple HIG for Machine Learning

Focus on system-level principles: ML features should feel like part of the OS, not separate AI overlays. Key: never surprise users with ML outputs; always provide an opt-out; make it clear when ML is involved.

Common to all three: **surface uncertainty, give users control, explain model behavior, plan for failures.**

---

## Pattern 7: User Feedback

### Explicit Feedback

Direct signals from users:
- Thumbs up/down on responses
- "Report a problem" flows
- Star ratings
- Corrections / edits to model outputs

The key design question: what level of feedback granularity is feasible? Thumbs up/down requires one click; asking "what specifically was wrong?" requires effort users may not provide.

### Implicit Feedback

Inferred from behavior without requiring user action:
- **GitHub Copilot "accept" action** — accepted suggestion = positive, dismissed = negative
- **Dwell time** on a response
- **Copy/paste behavior** — copied response = useful
- **Follow-up clarifying questions** — may indicate response was unclear

### Data Flywheel

User feedback → fine-tuning or retrieval improvement → better responses → more user trust → more feedback. Implicit feedback is especially valuable because it's captured without friction and scales with usage. The key engineering challenge: instrument the right implicit signals before launch — instrumentation added post-launch is rarely complete.

---

## Key Takeaways

- **Evals first:** Build evals before features. Automated metrics (BLEU/ROUGE/BERTScore) are useful but limited; LLM-as-judge (G-Eval Spearman 0.514) is stronger for open-ended tasks.
- **MMLU scores are harness-dependent:** Never compare scores across different evaluation frameworks.
- **RAG beats fine-tuning for knowledge injection:** Ovadia et al. 2023. Fine-tuning adjusts format, not facts. RAG + fine-tuning doesn't consistently beat RAG alone.
- **FiD enables large passage counts at linear cost:** Encode independently, decode jointly.
- **RETRO reduces model size 25×** by integrating retrieval into pretraining via chunked cross-attention.
- **HyDE requires no labeled data:** Generate a hypothetical answer, use its embedding for retrieval.
- **QLoRA reduces 65B model VRAM from >780GB to ~48GB** via 4-bit NF4 + double quantization + paged optimizers.
- **Prefix tuning (0.1% params) beats full fine-tuning in low-data regimes.**
- **Adapters (3.6% params) come within 0.4% of full fine-tuning performance.**
- **Structural guardrails (Guidance, token healing) make format violations impossible at generation time.**
- **Implicit feedback (Copilot accept) scales better than explicit feedback** — instrument before launch.
