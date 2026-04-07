# RAG — Retrieval Augmented Generation

**Related:** [[inference/decoding-strategies]] · [[applications/agentic-patterns]]  
**Sources:** [[manual/ML AI Engineering Cheat Sheet]]

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

### LLM as Ranker

Use an LLM (or agent) to reason about which candidates are relevant. Expensive and context-limited, but requires no training. With fast modern LLMs, this is less of a bottleneck than it once was.

**Commercial APIs:** Jina Reranker, Cohere Rerank, Voyage AI

---

## RAG vs Fine-tuning

| | RAG | Fine-tuning |
|---|---|---|
| Knowledge update | Dynamic (update the index) | Static (retrain required) |
| Proprietary data | Keeps data outside model weights | Bakes data into weights |
| Hallucination | Grounded in retrieved text | Less grounded, more fluid |
| Latency | Higher (retrieval step) | Lower (no retrieval) |
| Best for | Factual QA, document search | Style, format, specialized capabilities |
