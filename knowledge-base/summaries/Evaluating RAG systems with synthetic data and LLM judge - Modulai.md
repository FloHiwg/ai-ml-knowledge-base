# Evaluating RAG systems with synthetic data and LLM judge - Modulai

**Source:** [[raw/articles/Evaluating RAG systems with synthetic data and LLM judge - Modulai]]
**Author:** Yue Liu (Modulai)
**Related:** [[summaries/A Practitioners Guide to Retrieval Augmented Generation (RAG)]] · [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Applying Statistics to LLM Evaluations]]

---

## Core Idea

RAG evaluation requires assessing both the retriever and the generator along multiple dimensions. This post surveys three complementary strategies: end-to-end LLM judge scoring, fine-tuning specialized judges on synthetic QA data (ARES), and claim-based evaluation (RAGAS, RAGChecker). A meta-evaluation on WikiEval benchmarks these approaches against human agreement. The central insight: fine-tuned judges can match claim-based approaches on most metrics but require high-quality synthetic data to do so.

---

## Four Evaluation Dimensions

All approaches assess RAG along four dimensions:

| Dimension | What it measures | Compared against |
|---|---|---|
| **Context Relevance** | Is the retrieved context relevant to the question? | Question ↔ Retrieved context |
| **Answer Faithfulness** | Does the response stay true to the retrieved context? | Response ↔ Retrieved context |
| **Answer Relevance** | Does the response address the question? | Response ↔ Question |
| **Factual Correctness** | Is the response factually accurate? | Response ↔ Ground-truth answer |

---

## Approach 1: End-to-End LLM Judge

Prompt a general LLM (e.g., GPT-4) to act as judge across all four dimensions simultaneously. Fast and scalable, but general-purpose models lack consistency and interpretability when not fine-tuned for evaluation tasks. Outputs tend to be coarse (binary or unanchored Likert scores).

---

## Approach 2: ARES — Fine-tuned Judges on Synthetic QA

**Paper:** ARES (Saad-Falcon et al. 2023) — Automated Evaluation Framework for Retrieval-Augmented Generation Systems.

### Dataset Construction

Generate synthetic (question, context, answer) triples covering three quality levels:
- **Grounded (positive):** high-quality, faithful answers
- **Ungrounded (hallucinated):** answers that contradict or are unsupported by context
- **Poor (negative):** low-quality, irrelevant answers

Automatically label via instruction-following prompts asking the LLM to judge each example — returns binary or scaled judgments. Clean the dataset to remove low-confidence or ambiguous examples before fine-tuning.

| Metric | Positive Example | Negative Example |
|---|---|---|
| **Context Relevance** | (question, correct context) | (question, irrelevant context) |
| **Answer Faithfulness** | (question, context, grounded_answer) | (question, context, ungrounded_answer) |
| **Answer Relevance** | (question, context, grounded_answer) | (question, context, poor_answer) |
| **Factual Correctness** | (question, response, grounded_answer) | (question, poor_answer, grounded_answer) |

### Training

Add a classification head to the LLM for each evaluation metric. Train a **separate fine-tuned judge per metric** rather than one general model. This produces metric-specific, well-calibrated scores rather than coarse binary judgments.

**Advantage over off-the-shelf judges:** Fine-tuned models can assign nuanced scores with higher consistency — essential for performance tracking and debugging specific RAG components.

---

## Approach 3: Claim-Based Evaluation (RAGAS, RAGChecker)

Rather than scoring end-to-end, decompose evaluation into verifiable sub-steps:

1. LLM extracts **factual claims** from the generated answer
2. Each claim is cross-checked against retrieved context or ground-truth sources
3. Metrics computed from the claim-level verdicts (supported / unsupported / contradicted)

**Tools:**
- **RAGAS** (Es et al. 2024): automates faithfulness, answer relevance, and context relevance via claim extraction + NLI
- **RAGChecker** (Ru et al. 2024): fine-grained framework providing per-claim diagnostic insights into both retriever and generator weaknesses

Claim-based approaches tend to produce high agreement with human annotations because they reduce holistic scoring to a series of simpler, more reliable binary judgments.

---

## Meta-Evaluation: WikiEval Agreement Scores

**WikiEval dataset** (Es et al. 2024): 50 Wikipedia pages from after 2022 with structured fields (question, source, grounded/ungrounded/poor answers) — enables granular validation of all four dimensions.

**Agreement scores** vs human-annotated labels:

| Metric | RAGChecker | RAGAS | Fine-tuned LLM judge |
|---|---|---|---|
| **Context Relevance** | 1.0 | 0.96 | 0.56 |
| **Answer Relevance** | — | 0.84 | 0.82 |
| **Answer Faithfulness** | 0.98 | 1.0 | 0.89 |
| **Factual Correctness** | 0.92 | 1.0 | 0.91 |

**Key finding:** Fine-tuned judges approach claim-based frameworks on answer relevance (0.82 vs 0.84), faithfulness (0.89 vs 0.98/1.0), and factual correctness (0.91 vs 0.92/1.0) — but significantly underperform on **context relevance** (0.56 vs 1.0/0.96). The authors attribute the context relevance gap to limited synthetic data diversity, not a fundamental limitation of the approach.

---

## Mixed Methods: EvalGen and Human Feedback Loops

**EvalGen** (Shankar et al. 2024): human-in-the-loop framework that bridges automatic and human evaluation:
- Use human ratings to validate and calibrate automated scores
- Iteratively refine LLM-based evaluators to reduce misalignment
- "Validator validation" — ensure the evaluators themselves are trustworthy

This hybrid approach aligns evaluation methods with actual user expectations and corrects systematic biases in automated scoring before they propagate into system decisions.

---

## Retriever Evaluation

For high-stakes domains (legal, medical, enterprise search), the retriever often determines final response quality. Binary relevance labels are insufficient — **graded relevance labels** (1–5 rating scale) enable more informative IR metrics.

### NDCG (Normalized Discounted Cumulative Gain)

Measures retrieval quality by position: relevant documents at rank 1 contribute more than at rank 5. Normalized against the ideal ranking (IDCG):

```
DCG@k = Σ rel_i / log2(i + 1)    for i = 1..k
NDCG@k = DCG@k / IDCG@k
```

Where `rel_i` is the graded relevance of the document at position i.

### k-star Precision@5

Counts how many of the top 5 retrieved documents have relevance ≥ k, normalized by the number of documents rated ≥ k for the query:

```
k*P@5 = Σ 1(rel_i ≥ k) / min(5, |docs with rel ≥ k|)
```

Ensures scores are bounded [0, 1] even when fewer than 5 relevant documents exist.

These IR metrics complement LLM-based assessment by quantifying rank ordering quality — particularly useful in ACORD (legal contract retrieval) and similar high-precision retrieval applications.

---

## Challenges

- **No standard benchmark reflecting real-world use cases:** WikiEval uses 2022 Wikipedia snapshots; LLMs may have seen this data during pretraining, inflating scores.
- **Retriever vs. generator attribution:** Holistic evaluation cannot isolate which component caused an error. Claim-based approaches partially address this by tracking per-claim provenance.
- **Benchmark scope limitations:** Existing datasets focus on structured, well-formed content — not the ambiguous, multi-hop, conversational queries typical in production.

---

## Key Takeaways

- Four standard RAG evaluation dimensions: context relevance, answer faithfulness, answer relevance, factual correctness
- Fine-tuned judges (ARES) can match claim-based approaches on most metrics but require diverse synthetic data — context relevance is hardest (0.56 vs 1.0 for RAGChecker)
- Claim-based evaluation (RAGAS, RAGChecker) achieves highest human agreement by decomposing scoring into verifiable binary claim checks
- Human-in-the-loop calibration (EvalGen) is essential before trusting automated evaluators in production
- Use graded relevance labels + NDCG / k-star Precision@5 for retriever evaluation, especially in high-stakes domains
- WikiEval is the standard meta-evaluation benchmark for comparing RAG evaluation approaches
