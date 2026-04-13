# RAG — Retrieval Augmented Generation

**Related:** [[inference/decoding-strategies]] · [[applications/agentic-patterns]] · [[evaluation/llm-as-a-judge]]
**Sources:** [[manual/ML AI Engineering Cheat Sheet]] · [[summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG)]] · [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]]

---

## Core Idea

Retrieval Augmented Generation (RAG) preselects relevant content from a corpus and injects it into the model's context at inference time. This allows the model to use:
- **Proprietary/private knowledge** not in the pretraining data
- **Up-to-date information** beyond the model's training cutoff
- **Precise grounding** to reduce hallucinations

```
Query → Retriever → Top-K relevant chunks → Injected into prompt → LLM generates answer
```

---

## Information Representation

### Vector Database

Documents are chunked and embedded into dense vectors. The database stores these vectors and supports fast approximate nearest-neighbor search.

**Why chunk?** Embedding an entire large document into a single vector causes information loss — fine-grained passages get averaged out. Chunking preserves local precision.

**Common vector DBs:** Pinecone, Weaviate, Chroma, pgvector

### RAG Graph (Knowledge Graph RAG)

Instead of a flat vector index, stores relational structure — how entities and concepts are connected. Enables multi-hop retrieval ("what is the CEO of the company that acquired X?") without requiring all facts to appear in a single passage.

---

## Retrieval Techniques

### Cosine Similarity (Dense Retrieval)

Embed the query with the same model used for indexing. Find the K nearest document vectors by cosine similarity (equivalent to dot product on normalized vectors). This is dense retrieval / k-nearest-neighbors in embedding space.

**Used by:** Most modern RAG systems.

### BM25 (Sparse / Keyword Retrieval)

Classical TF-IDF-based retrieval, extended by BM25:
- **TF (Term Frequency):** More occurrences of the query term → more relevant
- **IDF (Inverse Document Frequency):** Rare terms count more than common terms
- **BM25 extension:** Normalizes by document length — a 10-word document with 3 occurrences outscores a 10,000-word document with 3 occurrences

**Good for:** Exact keyword matching, technical terms, proper nouns. Often used as a first-stage retriever in hybrid systems.

### Hybrid Retrieval

Combine dense (cosine similarity) and sparse (BM25) results, then rerank. Gets the semantic coverage of dense retrieval plus the exact-match precision of keyword search.

Embedding-only retrieval has two failure modes: (1) short/precise queries benefit little from semantic similarity; (2) phrasing sensitivity — minor reformulations ("IC" vs "engineer") retrieve entirely different results. BM25 covers the term-matching gap.

### Query Expansion

Before retrieval, parse the query with an LLM to expand synonyms, correct spelling, and standardize phrasing. This ensures consistent retrieval regardless of minor phrasing differences. A simple implementation: pass the query to the LLM with a "rewrite this as a search query" instruction before embedding.

---

## Reranking

A second-stage model scores the top-K retrieved candidates for final relevance before injecting into the prompt.

### Bi-Encoder

Separate encoders for query and document; compare via cosine similarity of output vectors.

- **Pro:** Fast — document vectors pre-computed and cached
- **Con:** Information loss when encoding independently — no direct query-document interaction

### Cross-Encoder

Query and document fed **together** into one encoder; predicts a single relevance score.

- **Pro:** Deep interaction between every query token and document token → more accurate
- **Con:** Slow — must re-run per (query, document) pair. Not feasible for millions of candidates, but fine for reranking top 50–100

**Examples:** BGE Reranker, BERT-based cross-encoders, Cohere Rerank

### Late Interaction — ColBERT

Middle ground: store multi-vector representations (one vector per token) for both query and document. Compute relevance via MaxSim — for each query token, find its best-matching document token, sum across query tokens.

More accurate than bi-encoder (preserves token-level information), faster than cross-encoder (precomputed document vectors).

**Index:** PLAID narrows candidate documents before the MaxSim step.

### Reranking Signals

Two types of signals for ranking retrieved candidates:

| Signal type | Examples |
|---|---|
| **Query-dependent** | BM25 score, semantic similarity, cross-encoder relevance |
| **Query-independent** | User feedback (thumbs up/down), popularity, recency, PageRank, document length |

Query-independent signals are especially useful when the retrieved top hit is technically retrieved but contains irrelevant content — a common failure mode when chunks span multiple concepts.

### LLM as Ranker

Use an LLM (or agent) to reason about which candidates are relevant. Expensive and context-limited, but requires no training. With fast modern LLMs, this is less of a bottleneck than it once was.

**Commercial APIs:** Jina Reranker, Cohere Rerank, Voyage AI

---

## RAG Pipeline: End-to-End

A production RAG pipeline has four stages:

1. **Data preprocessing** — clean and chunk documents (100–500 tokens per chunk). Data quality has outsized impact: proper preprocessing produces a 20% boost in answer correctness and 64% fewer tokens passed to the LLM.
2. **Indexing** — embed chunks with an encoder model; store in a vector DB with an ANN index.
3. **Retrieval** — hybrid search (dense + BM25); optional re-ranking with a cross-encoder or ColBERT.
4. **Generation** — inject retrieved chunks into the prompt; LLM uses in-context learning to generate a grounded response. No LLM finetuning required in modern usage.

### Chunking Strategy

The default LangChain approach — fixed-size chunks of 1,000–2,000 tokens — produces muddy embeddings when a chunk spans multiple concepts. A better approach is to **chunk by semantic units: sections or paragraphs**. Most writing naturally organizes by section (high-level concept) → paragraph (lower-level concept), with `\n\n` as a natural boundary.

Why it matters: embedding a 1,500-token chunk that covers five concepts forces the model to place it in the latent space of all five, making retrieval on any single concept unreliable. Paragraph-level chunking keeps embeddings conceptually focused.

Note: scraping, chunking, and indexing data often takes as much engineering effort as building the application on top of it.

### Embedding Domain Adaptation

Off-the-shelf embeddings (e.g., `text-embedding-ada-002`) may show unexpectedly high cosine similarity between semantically different texts in specialized domains. For private or domain-specific corpora, fine-tune an embedding model with **triplet loss** on `(anchor, positive, negative)` examples. Training signal sources:
- **Explicit:** thumbs-up/down on returned sources shown in the UI
- **Implicit:** click-through (clicked = positive, ignored = negative), search query logs

### ANN Recall Risk

Production retrieval uses ANN (approximate nearest neighbours) for latency — well-tuned indices achieve ~0.95 recall. However, cloud vector databases may not expose index tuning parameters, leaving users at potentially **as low as 50% recall**. Verify ANN configuration and tune `ef_construction`, `m`, and `nprobe`/`nlist` parameters when available.

### Lost-in-the-Middle Problem

LLMs struggle to use information in the middle of long context windows (Liu et al. 2023). Mitigation: use a **diversity ranker** that places the most relevant chunks at the beginning and end of the context, not in order of rank. Apply after retrieval (selection, not re-ranking).

---

## RAGAS: Automated RAG Evaluation

Three-metric evaluation framework (Es et al. 2023) that requires no human-annotated reference answers:

| Metric | What it measures | How it's computed |
|---|---|---|
| **Faithfulness** | Is the answer grounded in the retrieved context? | LLM extracts factual statements from answer; checks if each can be inferred from context |
| **Answer relevance** | Does the answer address the question? | LLM generates reverse-questions from the answer; average cosine similarity with the original question |
| **Context relevance** | Is retrieved context focused (low noise)? | LLM classifies each sentence in context as relevant or not |

Also use [[evaluation/llm-as-a-judge]] for end-to-end generation quality. Collect per-chunk user feedback (thumbs up/down on cited sources) for retrieval metrics (nDCG, DCG).

---

## RAG vs Fine-tuning

| | RAG | Fine-tuning |
|---|---|---|
| Knowledge update | Dynamic (update the index) | Static (retrain required) |
| Proprietary data | Keeps data outside model weights | Bakes data into weights (security risk) |
| Hallucination | Grounded in retrieved text | Less grounded, more fluid |
| Latency | Higher (retrieval step) | Lower (no retrieval) |
| Best for | Factual QA, document search | Style, format, specialized capabilities |

**Empirical finding**: RAG far outperforms continued pretraining/finetuning for knowledge injection. Combining RAG + finetuning does not consistently outperform RAG alone (Ovadia et al. 2023). Most knowledge is acquired during pretraining; finetuning adjusts output format more than knowledge content.
