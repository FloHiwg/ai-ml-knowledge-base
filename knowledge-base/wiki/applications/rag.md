# RAG — Retrieval Augmented Generation

**Related:** [[inference/decoding-strategies]] · [[applications/agentic-patterns]] · [[evaluation/llm-as-a-judge]]
**Sources:** [[manual/ML AI Engineering Cheat Sheet]] · [[summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG)]] · [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]] · [[summaries/Patterns for Building LLM-based Systems & Products]] · [[summaries/Evaluating RAG systems with synthetic data and LLM judge - Modulai]] · [[summaries/Agentic Design Patterns/14 Knowledge Retrieval (RAG)]]

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

This is the core benefit of **GraphRAG**: it can answer questions whose evidence is fragmented across multiple documents because the retrieval unit is not just a chunk, but a path through explicit relationships.

### Agentic RAG

Standard RAG retrieves context and passes it through. **Agentic RAG** adds a reasoning layer that inspects the retrieved material before final generation. That agent can:

- prefer the most authoritative or most recent source
- discard outdated or noisy context
- detect contradictions across retrieved documents
- decide that another retrieval round is needed before answering

This is especially valuable in enterprise settings where multiple documents disagree or where raw retrieval tends to surface both draft and final policy versions.

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

The retrieval unit matters because many RAG failures are really **chunking failures**. If a concept is spread across several chunks or buried inside overly broad chunks, the retriever may return incomplete evidence even when the right document exists.

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

Also use [[evaluation/llm-as-a-judge]] for end-to-end generation quality. Collect per-chunk user feedback (thumbs up/down on cited sources) for retrieval metrics (NDCG, DCG).

**RAGChecker** (Ru et al. 2024) provides fine-grained claim-level diagnostics: it extracts factual claims from answers and verifies each against context or ground truth separately, identifying whether errors originate in the retriever or generator.

### Retriever Evaluation Metrics

For high-stakes domains (legal, medical, enterprise search), the retriever often determines final response quality. Use **graded relevance labels** (1–5 ratings) rather than binary labels — they enable more informative IR metrics.

**NDCG@k (Normalized Discounted Cumulative Gain):** Accounts for both relevance and position. Documents at rank 1 contribute more than at rank 5.

```
DCG@k  = Σ rel_i / log2(i + 1)    for i = 1..k
NDCG@k = DCG@k / IDCG@k
```

Where `IDCG@k` is the ideal DCG (best possible ordering of results).

**k-star Precision@5:** Counts how many of the top 5 retrieved documents have relevance ≥ k, normalized by the number of qualifying documents:

```
k*P@5 = Σ 1(rel_i ≥ k) / min(5, |docs with rel ≥ k|)
```

Ensures scores are bounded [0, 1] even when fewer than 5 highly-relevant documents exist for a query.

---

## Advanced Retrieval Architectures

### Dense Passage Retrieval (DPR)

DPR (Karpukhin et al. 2020) trains two **bi-encoders** — one for queries, one for passages — using contrastive learning on (query, positive passage, hard negative passages) triplets from QA datasets. Stores passage embeddings in a FAISS index; retrieval via dot-product similarity.

The original dense retrieval baseline. Fine-tuning the encoders on domain QA pairs is the standard approach to improve in-domain recall.

### Fusion-in-Decoder (FiD)

FiD (Izacard & Grave 2020) solves the passage count scaling problem:

1. Encode each retrieved passage **independently** through the encoder — cost scales linearly with passage count
2. Decoder attends **jointly** over all encoded passage representations via cross-attention — the model sees all K passages simultaneously

More passages → linearly more encoding, but a single decoder call integrates them all. Scales to 100+ passages; strong on open-domain QA.

### RETRO: Retrieval During Pretraining

RETRO (Borgeaud et al. 2022) integrates retrieval into the pretraining loop rather than inference time:

- Retrieves from a 2 trillion token database during training
- Uses **chunked cross-attention** to attend to retrieved passages within each sequence chunk
- Only ~10% of model weights involve retrieval machinery

**RETRO-fitting:** An existing transformer can be converted to a RETRO model by training *only* the retrieval-related weights (<10% of parameters). Achieves GPT-3 (175B) performance at a 7B parameter scale — 25× parameter reduction.

### HyDE: Hypothetical Document Embeddings

HyDE (Gao et al. 2022) addresses the query-document distribution mismatch: queries are short and syntactically different from the long passages they should retrieve.

1. Use an LLM to **generate a hypothetical document** that would answer the query (factual accuracy doesn't matter)
2. Embed the hypothetical document
3. Search the real corpus using that embedding

The hypothetical document occupies similar embedding space to real documents, bridging the distribution gap. **No labeled training pairs required** — works zero-shot on new domains.

### Embedding Model Options

| Model | Notes |
|---|---|
| **Word2vec / fastText** | Word-level; no context; fastText handles OOV via subword units |
| **sentence-transformers** | Standard library; many pre-trained models for different domains |
| **E5** | Microsoft Research; strong on BEIR; uses instruction-prefixed inputs |
| **Instructor** | Instruction-tuned; specify retrieval task type in the input prefix |
| **GTE** | Alibaba DAMO; strong multilingual performance |

Evaluate domain-specific recall before committing to an embedding model — off-the-shelf models can fail on specialized or technical terminology.

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

---

## Operational Failure Modes

RAG systems commonly fail in four ways:

1. **Missed context** — the relevant information is split across chunks or documents and is never retrieved together
2. **Noisy retrieval** — the retriever surfaces technically similar but practically irrelevant chunks
3. **Conflicting evidence** — multiple retrieved sources disagree, and the model lacks a reconciliation layer
4. **Stale indexes** — the corpus changes faster than the embedding and retrieval pipeline is refreshed

These are why reranking, hybrid retrieval, GraphRAG, and Agentic RAG matter: they solve different parts of the same grounding problem.
