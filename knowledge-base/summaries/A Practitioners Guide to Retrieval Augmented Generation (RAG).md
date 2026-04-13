# A Practitioners Guide to Retrieval Augmented Generation (RAG)

**Source:** [[raw/articles/A Practitioners Guide to Retrieval Augmented Generation (RAG)]]
**Author:** Cameron R. Wolfe, Ph.D.
**Related:** [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## Core Idea

RAG improves an LLM's factuality and knowledge by pairing it with a searchable external knowledge base. Instead of relying on parametric knowledge (encoded in model weights during pretraining — which LLMs access unreliably), RAG retrieves relevant text chunks from a non-parametric store and injects them into the prompt at inference time, leveraging the LLM's in-context learning ability. RAG is simpler and cheaper than finetuning/continued pretraining, and empirically outperforms finetuning as a knowledge injection strategy.

---

## RAG Pipeline Structure

A complete RAG pipeline has four main stages:

### 1. Data Preprocessing (Cleaning & Chunking)
- Extract raw text from heterogeneous sources (PDF, Markdown, HTML, code, etc.)
- **Chunk** documents into 100–500 token units — the basic unit of retrieval
- **Chunk strategies:**
  - *Fixed-size*: split at a fixed token count (most common)
  - *Natural boundary*: use document structure (paragraphs, posts, product descriptions)
  - *Variable-size*: use separators to split at meaningful boundaries
- Data cleaning has outsized impact: proper preprocessing produces a 20% boost in answer correctness and a 64% reduction in tokens passed to the model

### 2. Indexing
- Embed each chunk with an encoder model (typically BERT-family: sBERT, ColBERT, etc.)
- Store vectors in a vector database (Pinecone, Weaviate, Chroma, pgvector)
- Build an efficient approximate nearest-neighbor index for fast retrieval

### 3. Retrieval
- Embed the input query using the same model
- Perform **hybrid search** (dense + lexical) for best results:
  - *Dense retrieval*: cosine similarity over embeddings (semantic coverage)
  - *Lexical retrieval*: BM25/keyword search (exact-match precision)
  - Combine results with weighted fusion
- Optional **re-ranking**: cross-encoder or ColBERT-style late interaction for fine-grained relevance scoring
- Optional **selection/diversity ranking**: sub-select retrieved chunks for diversity and optimal context layout

### 4. Generation
- Concatenate retrieved chunks with the input query in the LLM prompt
- LLM leverages in-context learning to generate a grounded, factual response
- Modern approach uses no finetuning of the LLM; relies entirely on ICL

---

## Origins: The Original RAG Paper [1]

Proposed in 2020 (Lewis et al.) for knowledge-intensive NLP tasks. Setup:
- **Retriever**: Dense Passage Retrieval (DPR) — BERT bi-encoder (separate query and document encoders)
- **Generator**: BART (encoder-decoder Seq2Seq model, pretrained with denoising objective)
- **Data**: Wikipedia dump chunked into 100-token sequences
- **Training**: only the DPR query encoder + BART generator are trained; document encoder is frozen (avoids rebuilding the index)

Two marginalization strategies:
- **RAG-Sequence**: same retrieved document used for all target tokens
- **RAG-Token**: each target token can use a different document

Results: state-of-the-art on open-domain QA, outperforming both extractive and closed-book Seq2Seq models.

**Key difference from modern usage**: original RAG involves finetuning; modern LLM-era RAG is purely inference-time with no model training required.

---

## RAG vs Finetuning for Knowledge Injection

| Dimension | RAG | Finetuning |
|---|---|---|
| Knowledge update | Dynamic — update the index | Static — requires retraining |
| Proprietary data | Stays outside model weights | Baked into weights (security risk) |
| Hallucination | Grounded in retrieved text | Less grounded |
| Implementation cost | Low | High |
| Best for | Factual QA, up-to-date info, proprietary docs | Style, format, new skills |

**Empirical finding** (Ovadia et al. 2023): RAG far outperforms finetuning for injecting new knowledge; combining finetuning + RAG does not consistently outperform RAG alone.

**Why finetuning fails at knowledge injection**: most information is learned during pretraining; finetuning adjusts output format more than knowledge content. This aligns with the Superficial Alignment Hypothesis from LIMA.

---

## Practical Tips for RAG Applications

### Retrieval: Use Hybrid Search, Not Just Vectors
- Pure dense retrieval produces semantic false positives
- Add a parallel BM25/lexical search and fuse results
- Enable keyword tricks: boost/exclude documents by specific terms, augment documents with synthetic data for better matching

### Context Window Optimization
- Require a large-context-window LLM (65K–200K+ tokens ideally)
- **Lost-in-the-middle problem** (Liu et al. 2023): LLMs struggle to use information in the middle of a long context; start and end positions are captured most reliably
- Mitigation: **diversity ranker** — place most relevant chunks at beginning and end; interleave by alternating most-relevant → least-relevant → next-most-relevant

### Data Cleaning Pipeline
- Inspect large volumes of data from each source; identify artifacts (logos, special symbols, code blocks, formatting tokens)
- Remove artifacts iteratively; can use LLM-as-a-Judge to automate pipeline construction
- Result: 20% answer correctness improvement, 64% token reduction

### Evaluation: Measure Both Retrieval and Generation
**Retrieval metrics**: traditional search metrics (DCG, nDCG); collect user relevance feedback (thumbs up/down on cited chunks)

**Generation metrics** — RAGAS framework [8]:
1. *Faithfulness*: is the answer grounded in the retrieved context? (LLM extracts factual statements, then checks if they follow from context)
2. *Answer relevance*: does the answer address the question? (LLM generates reverse-questions from the answer; cosine similarity with original)
3. *Context relevance*: is the retrieved context focused and not diluted with irrelevant passages?

Also use [[evaluation/llm-as-a-judge]] (LLM-as-a-Judge) to evaluate generation quality.

### Gorilla: Retrieval-Aware Finetuning for Tool Use [5]
- Finetuned LLaMA to use 1,600+ deep learning model APIs (HuggingFace, TensorFlow Hub)
- Training: self-instruct data generation + retrieval-aware finetuning (documentation injected at training time)
- Result: adapts to real-time API documentation changes at inference; fewer hallucinations in API calls

### Iterative Improvement
1. Add re-ranking (cross-encoder or ColBERT)
2. Finetune the embedding model on human relevance labels
3. Finetune the LLM generator on high-quality output examples
4. Augment prompts/chunks with synthetic LLM-generated data
5. Run A/B tests to validate each improvement

---

## Key Takeaways

- RAG pairs an LLM with a searchable knowledge base via prompt injection; no model training required in modern implementations
- RAG beats finetuning for knowledge injection — combining them doesn't consistently help beyond RAG alone
- Hybrid search (dense + lexical) is almost always better than pure vector search
- Data cleaning has major impact: 20% accuracy gain, 64% token reduction reported
- Lost-in-the-middle: place most relevant context at prompt edges, not the middle
- RAGAS provides automated evaluation across faithfulness, answer relevance, and context relevance
- The full RAG pipeline — retrieval, selection, prompt engineering, generation, evaluation — must all be iteratively improved
- RAG provides user-verifiable citations, reduces security risk from proprietary data, and keeps knowledge up-to-date without retraining
