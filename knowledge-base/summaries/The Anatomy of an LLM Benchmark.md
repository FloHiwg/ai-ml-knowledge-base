# The Anatomy of an LLM Benchmark

**Source:** [[raw/articles/The Anatomy of an LLM Benchmark]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Direct Preference Optimization (DPO)]] · [[summaries/Graph-Based Prompting and Reasoning with Language Models]]

---

## Core Idea

Good benchmarks drive AI progress — but creating them is hard, and most receive far less attention than modeling research. This overview surveys how the most widely-used LLM benchmarks are constructed and derives practical principles for making useful evaluations. Coverage excludes agent and coding benchmarks (treated as their own domain).

---

## Benchmark Survey

### MMLU [Hendrycks et al., 2020]
- **Data:** ~16K multiple-choice questions across 57 subjects (STEM, humanities, social sciences), sourced from freely available online material and curated by students.
- **Format:** Multiple choice (4 options), zero/few-shot, graded by string matching accuracy.
- **Difficulty tiers:** Elementary → high school → college → professional, inferred from question source.
- **Human accuracy:** Ranges from 34.5% (MTurk) to ~89.8% (domain experts).
- **Problem:** ~6.5% of questions contain errors; some subjects up to 57% error rate (Virology). Easy questions inflate performance and limit discrimination.
- **MMLU-Pro:** Removes easy/noisy questions via model-based filtering (majority-correct across 8 models → removed), augments with harder sources, expands to 10 answer choices, adds human+LLM quality review. ~12K questions in 14 domains.
- **MMLU-Redux:** Manual audit of 5,700 questions with hierarchical error taxonomy, re-annotation, and Cohen's Kappa agreement checks. Fixing errors meaningfully changes model rankings.

### GPQA [Rein et al., 2024]
- **Data:** 546 questions written from scratch by 61 PhD-level domain experts in Biology, Chemistry, Physics.
- **Format:** Multiple choice (4 options), designed to be answerable without answer choices.
- **Curation pipeline:** Write → expert solve/validate → revise → non-expert validation (3 annotators, ≥15 min, unrestricted web).
- **Subsets:** Extended (546) → Main (≥1 expert agrees, ≤2 non-experts correct: 448) → Diamond (both experts agree, ≤1 non-expert correct: 198).
- **Difficulty:** Experts ~70-80% accuracy; non-experts ~30-40% even with internet ("Google-proof").

### BIG-Bench → BBH → BBEH [Srivastava et al., 2023 / Suzgun et al., 2023 / Kazemi et al., 2025]
- **BIG-Bench:** 204 tasks contributed via GitHub PRs from 450+ authors. Varied formats (JSON + programmatic). Standardized API with `generate_text` / `cond_log_prob`. Scores normalized to [0, 100] via per-task high/low reference scores.
- **BIG-Bench Lite:** 24 JSON tasks for fast evaluation.
- **BIG-Bench Hard (BBH):** 23 tasks where models underperformed humans at time of release; filtered to exact-match/multiple-choice format for CoT compatibility. Saturated by early 2025.
- **BIG-Bench Extra Hard (BBEH):** Replaces all BBH tasks with harder variants. Fixes known issues: high random-chance performance, shortcut-solvable tasks, very short inputs. Uses human+model co-curation: tasks iterated until both a general and a reasoning model (Gemini-based) score below 70%.

### IFEval / IFBench [Zhou et al., 2023 / Pyatkin et al., 2025]
- **Focus:** Objectively verifiable instruction following (e.g. "response must be 100–200 words") — not subjective quality.
- **IFEval:** 25 constraint templates → prompts with 1-3 random constraints. Binary per-instruction verification. Metrics: instruction-level and prompt-level strict/loose accuracy.
- **IFBench:** Expands to 58 constraints (+ 29 for RLVR training). Constraints sourced from user feedback, designed to be hard and Python-verifiable. Performance drop vs IFEval suggests models overfit to IFEval's specific constraints (often used directly in synthetic SFT data generation).

### AlpacaEval [Dubois et al., 2024]
- **Format:** Pairwise instruction following — LLM judge (GPT-4-Turbo) compares candidate model output to a reference model output; reports win rate.
- **Data:** 805 prompts from AlpacaFarm, combining Self-Instruct, Open Assistant, Anthropic Helpfulness, Vicuna, Koala evaluation sets.
- **Evolution:** Underlying prompts stayed mostly fixed; improvements focused on changing reference/judge models to improve correlation with human preferences.

### Math Benchmarks
- **Saturated:** GSM-8K (grade school, 8.5K), MATH (high school, 12.5K), AMC, AIME.
- **Frontier-level (unsaturated):**
  - **FrontierMath** — expert-crafted research-level problems (hours/days to solve).
  - **MathArena** — uses fresh competition problems immediately after release to avoid contamination.
  - **RealMath** — auto-updated from research papers and forums.
  - **OmniMath** — 4.5K competition problems across 30+ sub-domains.
- **Grading:** Automatic verifier or exact string match; proof-based questions use human review.

---

## Advanced Techniques: Item Response Theory (IRT)

IRT (from psychometrics) models each item `i` with **difficulty** (`β_i`) and **discrimination** (`α_i`) parameters, and each model `l` with a **capability** parameter (`θ_l`). The probability that model `l` answers item `i` correctly is a logistic function of these parameters. Fit from historical evaluation data.

### tinyBenchmarks [Polo et al., 2024]
- **Goal:** Evaluate a new model on far fewer examples while maintaining accurate performance estimates.
- **Method (p-IRT estimator):** Fit a multi-dimensional IRT model from historical results. Use IRT embeddings to cluster items and select `K` anchor points. Evaluate new model only on anchors, fit only `θ_l'`. Predict performance on remaining items via the IRT model.
- **IRT++:** Convex combination of the sample average (low bias, high variance) and IRT prediction (low variance, some bias).
- **Result:** ~100 anchor points per sub-domain achieves <2% error — a 140× reduction on MMLU.

### Fluid Benchmarking [Hofmann et al., 2025]
- **Goal:** Dynamically select the most informative evaluation items per model rather than using a fixed set.
- **Key insight:** A hard question is uninformative for a weak model; an easy question is uninformative for a strong model. Static benchmarks treat all items equally.
- **Method:** Fit unidimensional IRT offline. For each new model, iteratively select items by **Fisher information** (prioritises items whose difficulty matches current capability estimate), evaluate, re-fit `θ_l'`. Report `θ_l'` directly as the performance metric instead of raw accuracy.
- **Result:** Stable, accurate capability estimates across a wide range of evaluation budgets.

### DatBench [Joshi et al., 2026] — VLM Evaluation
- **Problems found in existing VLM benchmarks:** Multiple-choice format inflates scores via guessing; up to 70% of questions are blind-solvable (answerable without the image); up to 42% of data in some domains is mislabeled/ambiguous.
- **Curation pipeline:**
  1. Convert MC → generative (LLM judge grades open responses).
  2. Remove blind-solvable questions (re-run without images; flag any model-solvable).
  3. Quality filter: flag questions no model answers correctly → frontier VLM judge verifies.
  4. Discriminative selection: rank by **point-biserial correlation** (`r_pb`) — items that strong models answer correctly and weak models miss.
- **Result:** 90% of discriminative power retained with 40% of data; 13× evaluation speedup; generative format alone causes up to 35% performance drop.
- **Bonus findings:** VLMs exhibit a perception/reasoning tradeoff; "overthinking" (incorrect answers use 3× more tokens); vision vs. language prior dependence varies by capability.

---

## Keys to a Useful Benchmark

| Principle | What it means |
|---|---|
| **Domain taxonomy** | Categorise data into domains/sub-domains for granular diagnostics and structured evolution |
| **Human annotation** | Expert review remains essential — for writing questions, validating difficulty, or catching LLM mistakes |
| **Model-in-the-loop** | Use LLMs for difficulty filtering, data reformatting, and routing issues to human review |
| **Data quality** | Pull from recognised, vetted sources; build explicit pipelines to detect mislabels and ambiguity |
| **Realism** | Questions should reflect how models are actually used (e.g. generative format > multiple choice) |
| **Evolution** | Plan for saturation; design benchmarks to grow harder (difficulty, scope, diversity) as models improve |

---

## Common Failure Modes to Avoid

- **Multiple choice** → random guessing inflates scores; doesn't match generative deployment.
- **Static question sets** → models get trained on them (benchmark contamination / overfitting).
- **Low discrimination** → easy questions tell you nothing about relative model quality.
- **Blind-solvable questions** → tests language priors, not the capability of interest.
- **No evolution plan** → benchmark becomes saturated and irrelevant within months.
