# LLM-as-a-Judge

**Related:** [[evaluation/benchmarks]] · [[evaluation/statistical-evaluation]] · [[training/fine-tuning]] · [[inference/prompting-and-reasoning]]
**Sources:** [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Evaluating RAG systems with synthetic data and LLM judge - Modulai]]

---

## What It Is

LLM-as-a-Judge is a reference-free evaluation strategy: a powerful LLM (the "judge") is prompted to score the quality of another model's output. Introduced alongside GPT-4 (the first model capable of reliably evaluating other models), it has become the dominant fast-iteration evaluation method alongside human evaluation.

**Key properties:**
- Reference-free — no gold-standard output required
- Generalizes to any open-ended task via prompt changes only
- ~80% agreement with human preferences (matching human inter-annotator agreement)
- Cheap and fast; AlpacaEval runs in <3 min for <$10

---

## Prompt Setups

| Setup | Description | Trade-offs |
|---|---|---|
| **Pairwise comparison** | Judge picks the better of two responses | Most reliable; O(n²) across model pairs |
| **Pointwise scoring** | Judge assigns a Likert score to a single response | Scalable; less stable (absolute scores drift) |
| **Reference-guided** | Judge sees a reference solution alongside responses | Best for math/coding; requires ground truth |

**Combining with CoT:** Append a zero-shot CoT instruction ("explain your reasoning before scoring"). Ask for rationale *before* the score — rationales generated after the score are not supported by it.

---

## Key Benchmarks

### MT-Bench
80 expert-written multi-turn questions across 8 genres (writing, roleplay, reasoning, math, coding, etc.). Used in the original LLM-as-a-Judge paper to measure judge correlation with human preferences.

### AlpacaEval
805 instructions; LLM judge compares candidate model vs. baseline (pairwise win-rate). Runs in <3 min.

**Length-Controlled AlpacaEval:** Regression-based debiasing strips the length contribution from win-rate scores. Achieves **Spearman 0.98** correlation with Chatbot Arena — highest of any automated benchmark. Cannot be significantly gamed by verbosity alone.

### Chatbot Arena
Crowdsourced platform: users chat with two unknown LLMs simultaneously and pick a winner. Elo ranking over >1.5M pairwise preferences. Considered the gold-standard human leaderboard.

---

## Biases

Three documented biases (Zheng et al. 2024):

1. **Position bias** — judge favors responses by position in the prompt. GPT-4 prefers first; ChatGPT prefers second. Vicuna-13B's win rate over ChatGPT swung from 2.5% → 82.5% just from position switching.
2. **Verbosity bias** — longer responses score higher independent of quality.
3. **Self-enhancement bias** — judge prefers outputs from its own model family. GPT-4 preferred GPT-4 outputs 87.76% of the time vs. 47.61% for human raters.

Additional weaknesses: judges struggle with questions they cannot answer themselves; judges can be misled by incorrect information in evaluated responses.

---

## Bias Mitigation

| Technique | Effect |
|---|---|
| **Position switching trick** | Randomize output positions; average scores across both orderings |
| **Few-shot calibration** | Provide examples to anchor internal scoring scale |
| **Reference answers** | Supply correct solution for hard math/reasoning questions |
| **Grading rubric** | Explain what each score level means in the prompt |
| **Logprob-weighted scoring** | Final score = Σ(score × P(score)); reduces integer clustering |
| **Multi-judge ensemble** | Use 2–3 different judge models; dilutes self-enhancement |
| **Low temperature** | Use ~0.1 for determinism; same temperature across all comparisons |

**Multiple Evidence Calibration** (Wang et al. 2023): generate CoT evidence before scoring, several times with switched positions. Significantly reduces positional bias.

---

## G-Eval

Framework proposing two improvements for pointwise LLM evaluation:

1. **Auto-CoT**: LLM first generates a set of evaluation steps from the task description, then uses those steps as scoring context (more structured than plain CoT)
2. **Logprob-weighted scoring**: final score = weighted average of all possible scores by their generation probability

G-Eval achieves Spearman 0.514 with human ratings on summarization — a significant improvement over prior metrics.

---

## Specialized Judge Models

When proprietary judges are unavailable or self-enhancement bias is a concern, specialized open-source judges can be fine-tuned:

- **Prometheus** (Kim et al. 2023, 2024): LLaMA fine-tuned specifically for fine-grained evaluation
- JudgeLM, PandaLM, Generative Judge — other fine-tuned evaluator families
- LLaMA-3 as base model largely closes the gap with proprietary judges

---

## RLAIF: LLM-as-a-Judge as a Training Signal

LLM-as-a-Judge prompts can generate synthetic preference pairs for RLHF training — this is called **Reinforcement Learning from AI Feedback (RLAIF)**. Constitutional AI (Bai et al. 2022) and Lee et al. (2023) showed this is viable. Rumored to be widely used in top industry labs. See also [[training/fine-tuning]].

---

## RAG-Specific Evaluation

LLM-as-a-Judge is especially common in RAG pipelines. The standard four dimensions are:

| Dimension | What it measures |
|---|---|
| **Context Relevance** | Is the retrieved context relevant to the question? |
| **Answer Faithfulness** | Does the response stay true to the retrieved context? |
| **Answer Relevance** | Does the response directly address the question? |
| **Factual Correctness** | Is the response factually accurate against a known ground truth? |

### Fine-tuning Judges: ARES

Rather than using a general-purpose LLM judge, ARES (Saad-Falcon et al. 2023) fine-tunes **separate models per metric** on synthetic QA datasets. Synthetic data covers three quality levels (grounded, hallucinated, poor); examples are auto-labeled and filtered for quality before training. Fine-tuned judges produce more calibrated, nuanced scores than off-the-shelf models.

**WikiEval agreement scores** (vs human labels):

| Metric | RAGChecker | RAGAS | Fine-tuned (ARES-style) |
|---|---|---|---|
| Context Relevance | 1.0 | 0.96 | 0.56 |
| Answer Relevance | — | 0.84 | 0.82 |
| Answer Faithfulness | 0.98 | 1.0 | 0.89 |
| Factual Correctness | 0.92 | 1.0 | 0.91 |

Fine-tuned judges match claim-based approaches on most metrics but lag on context relevance — attributable to synthetic data diversity limitations.

### Claim-Based Evaluation: RAGAS and RAGChecker

Instead of holistic scoring, extract factual claims from the answer and verify each claim against context or ground truth. Reduces holistic evaluation to a sequence of simpler binary judgments — explains the higher human agreement scores.

- **RAGAS** (Es et al. 2024): automates faithfulness, answer relevance, and context relevance
- **RAGChecker** (Ru et al. 2024): fine-grained per-claim diagnostics across retriever and generator

### Human-in-the-Loop: EvalGen

EvalGen (Shankar et al. 2024): use human ratings to calibrate automated evaluators, then iterate. "Validator validation" — ensure the judge itself is trustworthy before trusting its outputs in production decisions.

---

## Practical Implementation Checklist

- Always use position switching for pairwise; average over both orderings
- Ask for rationale before score (zero-shot CoT)
- Add grading rubric for pointwise scoring, or use logprob-weighted scoring
- Use temperature ~0.1; keep temperature constant across compared runs
- Supply reference answers for math/coding tasks
- Never deploy solely on LLM judge results — include human evaluation before production
