# Experimenting with LLMs to Research, Reflect, and Plan

**Source:** [[raw/articles/Experimenting with LLMs to Research, Reflect, and Plan]]
**Author:** Eugene Yan (Apr 2023)
**Related:** [[summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG)]] · [[summaries/AI Agents from First Principles]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]]

---

## Core Idea

A practitioner's first-hand account of building LLM-powered tools on top of LangChain and Discord, exposing four concrete retrieval failures encountered in production-like use. The central framing: LLMs are reasoning engines, not fact databases — their value comes from being supplied with the right context at the right time via hybrid retrieval.

---

## Tools Built

Six Discord slash commands built on `gpt-3.5-turbo` / `gpt-4` + LangChain + Pinecone + OpenAI `text-embedding-ada-002`:

| Command | Description |
|---|---|
| `/summarize` | Fetches URL content and returns bullet-point summary |
| `/eli5` | Fetches URL content and explains it simply |
| `/sql` | Converts natural language to SQL, executes, returns results |
| `/sql-agent` | Zero-shot ReAct agent for SQL (less reliable; often hit iteration limits) |
| `/search` | Google Search API tool for real-time web queries |
| `/board` | RAG advisor backed by writing from Paul Graham, Marc Andreessen, Naval Ravikant, Will Larson, Charity Majors |
| `/ask-ey` | Personal RAG over Eugene's own blog — easier to validate recall/ranking errors |

---

## Four Retrieval Shortcomings

### 1. ANN Indices Tuned Sub-Optimally

Most production retrieval uses approximate nearest neighbours (ANN) — not exact — for latency. While well-tuned ANN indices achieve ~0.95 recall, **cloud vector databases may not expose tuning parameters**, leaving users with potentially as low as 50% recall. Mitigation: tune ANN index parameters to hit the recall/latency trade-off needed for the use case.

### 2. Off-the-Shelf Embeddings May Transfer Poorly

Generic embeddings (e.g., `text-embedding-ada-002`) show unexpectedly high cosine similarity between semantically different texts in specialized domains. Mitigation: **fine-tune an embedding model with triplet loss** on `(anchor, positive, negative)` examples. Sources of training signal:
- Explicit: thumbs-up/down on returned sources
- Implicit: click-through signals, ignored search results as negatives

### 3. Inadequate Chunking

Fixed-size chunking (1,500-token chunks) bundles multiple concepts into one chunk, producing muddy embeddings that scatter across the latent space. **Chunk by sections or paragraphs instead** — most writing organizes by section (high-level concept) → paragraph (lower-level concept). Natural boundary: `\n\n` paragraph breaks. Note: data prep (scraping + chunking) took as much effort as building the tools.

### 4. Embedding-Only Retrieval Insufficient

Dense retrieval struggles when term matching is critical. Short, precise queries often benefit less from semantic similarity than from keyword overlap. Also, phrasing sensitivity — minor query reformulations change retrieved results ("IC" vs "engineer" returns different sets). Solutions:
- **Hybrid retrieval:** BM25 (keyword) + semantic search — each covers the other's weakness
- **Query expansion:** LLM-based query parsing for synonym expansion, spelling correction, autocomplete before retrieval
- **Reranking:** Apply query-dependent signals (BM25 score, semantic score) and query-independent signals (popularity, recency, PageRank, document length) to re-order retrieved candidates

> Follow-up implementation: OpenSearch + E5 embeddings (hybrid).

---

## LLM-Augmented Workflows

Three envisioned use cases:

### Enterprise/Personal Search and Q&A
- Query internal docs, tickets, meeting transcripts with natural language
- Return synthesized answers (not just links) with source attribution
- Access-controlled: only returns documents you have permissions for

### Research, Planning, and Writing
- Use RAG to gather and synthesize background before writing
- LLM copilot fills document sections, suggests solutions, surfaces data points
- Human remains the author; LLM handles information gathering and preparation

### Personal Knowledge Base Q&A
- Query accumulated notes, papers, and writing over time
- Addresses the forgetting curve — knowledge is retrievable even years later

---

## Core Framing

> "The right way to think of the models that we create is a reasoning engine, not a fact database… What we want them to do is something closer to the ability to reason, not to memorize." — Sam Altman

The key challenge is **context delivery**: getting the right information into the LLM's context at the right time. Hybrid keyword + semantic retrieval is the mechanism. This explains the convergence happening across the industry: traditional search indices adding vector search, vector DBs adding keyword search, and purpose-built hybrid systems (Vespa, FB search).

---

## Key Takeaways

- LLMs are reasoning engines — their value depends on being given relevant context, not on parametric memory
- ANN recall is not guaranteed to be high; cloud vector DBs may not expose tuning options (risk: ~50% recall)
- Chunk by semantic units (sections/paragraphs) not fixed-size windows; muddy embeddings hurt retrieval quality
- Fine-tune embeddings with triplet loss when domain transfer is critical; use click/feedback signals for training data
- Hybrid BM25 + semantic retrieval is the right default; pure embedding retrieval has phrasing sensitivity and term-matching blind spots
- Query expansion (LLM-parsed synonyms) and reranking (query-dependent + query-independent signals) round out a production retrieval pipeline
- Data preparation (scraping, chunking, indexing) is as expensive as building the application itself
