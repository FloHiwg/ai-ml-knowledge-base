# LLM Benchmarks

**Related:** [[evaluation/statistical-evaluation]] · [[evaluation/llm-as-a-judge]] · [[concepts/scaling-and-the-bitter-lesson]]  
**Sources:** [[summaries/The Anatomy of an LLM Benchmark]] · [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]] · [[summaries/Patterns for Building LLM-based Systems & Products]]

---

## Design Principles

| Principle | What it means |
|---|---|
| **Domain taxonomy** | Categorise into domains/sub-domains for granular diagnostics |
| **Human annotation** | Expert review for writing, validating difficulty, catching LLM mistakes |
| **Model-in-the-loop** | Use LLMs for difficulty filtering, reformatting, routing to human review |
| **Data quality** | Vetted sources; explicit pipelines to detect mislabels and ambiguity |
| **Realism** | Questions should match how models are actually deployed |
| **Evolution** | Plan for saturation; design to grow harder as models improve |

---

## Common Failure Modes

- **Multiple choice** → random guessing inflates scores; doesn't match generative deployment
- **Static question sets** → models get trained on them (contamination/overfitting)
- **Low discrimination** → easy questions tell you nothing about relative model quality
- **Blind-solvable questions** → tests language priors, not the target capability
- **No evolution plan** → benchmark saturates and becomes irrelevant within months

---

## Key Benchmarks

### MMLU (Hendrycks et al. 2020)

- ~16K multiple-choice questions, 57 subjects, 4 answer choices
- Sources: freely available online material; difficulty tiers from elementary to professional
- Human accuracy: 34.5% (MTurk) to ~89.8% (domain experts)
- **Problem:** ~6.5% error rate in questions; some domains up to 57% (Virology)

**MMLU-Pro:** Model-based filtering removes easy/noisy questions (majority correct across 8 models → removed), expands to 10 choices, adds human+LLM quality review. ~12K questions.

**MMLU-Redux:** Manual audit of 5,700 questions with hierarchical error taxonomy. Fixing errors meaningfully changes model rankings.

### GPQA (Rein et al. 2024)

- 546 questions written from scratch by PhD-level experts (Biology, Chemistry, Physics)
- Designed to be Google-proof: non-experts with unrestricted web access score only ~30–40%
- Experts: ~70–80% accuracy
- **Diamond subset** (198 questions): both experts agree, ≤1 non-expert correct — the hardest

Curation: Write → expert solve → revise → 3 non-expert annotators validate (≥15 min, full internet allowed).

### BIG-Bench Family

**BIG-Bench:** 204 tasks from 450+ authors via GitHub PRs. Varied formats.  
**BBH (BIG-Bench Hard):** 23 tasks where models underperformed humans at release. Saturated by early 2025.  
**BBEH (BIG-Bench Extra Hard):** Replaces all BBH tasks with harder variants. Iterative difficulty calibration: tasks reworked until both a general *and* a reasoning model score below 70%.

Fixes over BBH: removes high random-chance performance, shortcut-solvable tasks, very short inputs.

### IFEval / IFBench (Instruction Following)

Focus: **objectively verifiable** instruction following (word count, format, structure) — not subjective quality.

**IFEval:** 25 constraint templates → prompts with 1–3 random constraints. Binary per-instruction verification.  
**IFBench:** 58 constraints (+29 for RLVR training). Models overfit IFEval because its constraints are often used directly in synthetic SFT data generation — IFBench performance drops vs IFEval reveal this.

### AlpacaEval (Dubois et al. 2024)

Pairwise instruction following: LLM judge (GPT-4-Turbo) compares candidate to reference model, reports win rate. 805 prompts combining multiple instruction-following datasets. Runs in <3 minutes for <$10.

**Length-Controlled AlpacaEval:** Regression-based debiasing removes the verbosity contribution from win-rate. Achieves Spearman 0.98 correlation with Chatbot Arena — the highest of any automated metric. Cannot be gamed by asking the model to be more verbose. See [[evaluation/llm-as-a-judge]] for full LLM-as-a-Judge context.

### Math Benchmarks

**Saturated for standard LLMs:** GSM-8K (grade school), MATH (high school), AMC.

**Active frontier (reasoning era):** AIME — near-saturated for standard LLMs (GPT-4o: 12%), but still an active benchmark for reasoning models (o3: ~97%). See [[training/reasoning-models]].

**Frontier-level (unsaturated):**
- **FrontierMath** — research-level problems (hours/days to solve even for experts)
- **MathArena** — uses fresh competition problems after release (anti-contamination)
- **OmniMath** — 4.5K competition problems across 30+ sub-domains

---

## Advanced: Item Response Theory (IRT)

IRT models each item's **difficulty** and **discrimination**, and each model's **capability**. Fit from historical evaluation data. Enables:

### tinyBenchmarks (Polo et al. 2024)

Use IRT embeddings to cluster items, select ~100 anchor points per sub-domain, evaluate only on anchors, and predict full-benchmark performance via the IRT model. Achieves <2% error — a **140× reduction** in evaluation cost on MMLU.

### Fluid Benchmarking (Hofmann et al. 2025)

Dynamically select items by **Fisher information** — prioritizes items whose difficulty matches the model's current capability estimate. A hard question is uninformative for a weak model; an easy question is uninformative for a strong model. Adapts the evaluation to each model.

### Point-Biserial Correlation

For each item, compute the correlation between "answered correctly" and "overall model strength." High correlation = discriminative item (strong models get it right, weak models don't). Used in DatBench for item selection: 90% of discriminative power retained with 40% of data.

---

## Benchmark Saturation and Reasoning Models

The arrival of reasoning models ([[training/reasoning-models]]) has dramatically accelerated benchmark saturation. GSM-8K, MATH, and BBH — each considered frontier-level in their time — are now fully saturated. AIME, near-saturated for standard LLMs, remains an active frontier specifically because reasoning models can push it further. This creates ongoing pressure to produce harder benchmarks (BBEH, FrontierMath, ARC-AGI) faster than models can saturate them.

---

## Text Generation Metrics

Four automated metrics for evaluating generated text, each measuring a different property:

### BLEU (Bilingual Evaluation Understudy)

**Precision-based n-gram overlap.** Measures what fraction of n-grams in the *generated* text appear in the reference. Adds a **brevity penalty** to prevent short outputs from gaming precision.

- Used primarily in machine translation
- Fails to capture paraphrase or semantic equivalence
- Sensitive to tokenization choices

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

**Recall-based n-gram overlap.** Measures what fraction of reference n-grams appear in the generated text.

| Variant | What it captures |
|---|---|
| **ROUGE-N** | n-gram recall |
| **ROUGE-L** | Longest Common Subsequence — sentence-level structure |
| **ROUGE-S** | Skip-gram co-occurrences — allows gaps between matched words |

Used primarily in summarization evaluation.

### BERTScore

**Contextual embedding similarity.** Embeds tokens from candidate and reference using a BERT model, then computes token-level cosine similarity with greedy matching: for each reference token, find the most similar candidate token.

Outputs: Precision (P), Recall (R), F1. Captures semantic similarity that n-gram metrics miss. Heavily dependent on the choice of embedding model and its domain coverage.

### MoverScore

**Soft WMD (Word Mover's Distance)** using BERT contextual embeddings. Unlike BERTScore's one-to-one matching, MoverScore allows many-to-one mappings — finding the optimal transport assignment that minimizes cost to "move" probability mass from candidate to reference tokens. Uses idf-weighting to downweight common words.

More flexible alignment than BERTScore; better at capturing complex semantic relationships between sentences.

### Metric Limitations

All four metrics can be gamed and diverge from human judgment on open-ended generation. Use them as diagnostic signals, not ground truth. G-Eval (Auto-CoT + logprob weighting) achieves Spearman 0.514 with human evaluation on summarization — see [[evaluation/llm-as-a-judge]].

---

## MMLU Implementation Variance

The same model can receive substantially different MMLU scores depending on which evaluation harness is used. Sources of variance:

- **Prompt format:** original Hendrycks format vs HELM vs EleutherAI's `lm-eval`
- **Few-shot examples:** which examples are selected, and how many
- **Chat template:** whether instruction/chat formatting is applied to the model
- **Scoring method:** token probabilities vs sampling vs log-likelihood

**Implication:** model comparisons via MMLU are only valid when the same harness is used throughout. Published leaderboard scores from different organizations are not directly comparable.

---

## Super-Population Framing

Any benchmark is a finite sample from a conceptual infinite super-population of all possible questions for a given skill. Goal: estimate true skill μ on the super-population, not maximize score on the finite benchmark. This framing motivates statistical evaluation — see [[evaluation/statistical-evaluation]].
