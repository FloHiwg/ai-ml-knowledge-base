# LLM Benchmarks

**Related:** [[evaluation/statistical-evaluation]] · [[concepts/scaling-and-the-bitter-lesson]]  
**Sources:** [[summaries/The Anatomy of an LLM Benchmark]]

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

Pairwise instruction following: LLM judge (GPT-4-Turbo) compares candidate to reference model, reports win rate. 805 prompts combining multiple instruction-following datasets. Improvements focused on reference/judge model quality to better correlate with human preferences.

### Math Benchmarks

**Saturated:** GSM-8K (grade school), MATH (high school), AMC, AIME.

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

## Super-Population Framing

Any benchmark is a finite sample from a conceptual infinite super-population of all possible questions for a given skill. Goal: estimate true skill μ on the super-population, not maximize score on the finite benchmark. This framing motivates statistical evaluation — see [[evaluation/statistical-evaluation]].
