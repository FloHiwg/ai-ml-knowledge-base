# Applying Statistics to LLM Evaluations

**Source:** [[raw/articles/Applying Statistics to LLM Evaluations]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/The Anatomy of an LLM Benchmark]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## Core Idea

Most LLM evaluations report a single accuracy score with no uncertainty quantification — treating noise as signal. This overview builds a statistical framework for evaluations from the ground up: standard errors, confidence intervals, clustered errors, variance reduction via resampling and token probabilities, paired model comparisons, and power analysis.

> *"We want to avoid mistaking noise for progress and instead equip ourselves with the statistical tools needed to run informative model evaluations."*

---

## Statistical Foundations

### Key quantities

| Quantity | What it captures |
|---|---|
| **Sample mean** `s̄` | Estimate of true performance μ over n questions |
| **Variance** `Var(X)` | Spread of individual scores around the mean |
| **Covariance** `Cov(X, Y)` | Whether two variables vary together |
| **Standard error (SE)** | Standard deviation of the *sample mean* — how much the mean estimate varies across runs |
| **z-score** | How many SDs a value lies from the mean |

**Law of total variance** — decomposes the variance of an evaluation score `S` into two parts:
1. `Var(x)` — variability due to which question was sampled (irreducible; a property of the super-population)
2. `E[σ_i^2]` — within-question variability from stochastic LLM generation / LLM judge

This decomposition directly motivates the variance reduction strategies below.

### Standard error and CLT

Assuming IID questions with finite variance, the standard error of the sample mean is:

```
SE(S̄) = s / sqrt(n)     (general)
SE(S̄) = sqrt(μ̂(1-μ̂)/n) (Bernoulli scores ∈ {0,1})
```

The **Central Limit Theorem** guarantees that the sample mean distribution approaches `N(μ, σ²/n)` as n grows → allows confidence intervals:

```
95% CI = s̄ ± 1.96 × SE
```

**Bootstrapping** (resample with replacement, measure SD of sample means) is a valid alternative, but the CLT is simpler when its assumptions hold.

---

## Statistical Framework for LLM Evaluations [1]

**Super-population framing:** Any benchmark is a finite sample from an infinite super-population of all possible evaluation questions for a given skill. Goal: estimate true mean performance μ on the super-population, not maximize score on the finite dataset.

### Recommendation 1 — Report standard errors (IID questions)

When questions are independently sampled: compute SE via CLT, report alongside the mean. A toy table looks like:

```
Model   | MMLU          | GSM-8K
--------|---------------|-------
Model A | 0.72 ± 0.013  | 0.61 ± 0.021
Model B | 0.74 ± 0.012  | 0.63 ± 0.019
```

Overlapping CIs do not rule out a true difference — see model comparison section.

### Recommendation 2 — Clustered standard errors (non-IID questions)

Questions are not always independent (e.g., same prompt in multiple languages, prompts from the same document, related topics). Assuming IID underestimates uncertainty — CIs are too narrow.

**Clustered SE:** Treat questions within a cluster as correlated, questions across clusters as independent. The clustered SE interpolates between:
- Perfectly correlated within cluster → each cluster is one effective observation
- Zero correlation → reduces to standard CLT SE

In practice, the clustered SE can be **3× larger** than the naive CLT SE. Always report `n` (questions) and `C` (clusters) when using this formulation.

### Recommendation 3 — Variance reduction

Two complementary strategies:

**Resampling (K samples per question):** Generate K completions for each question i and average their scores `S̄_i`. This reduces within-question variance by a factor of K:
```
Var(S̄_i) = σ_i² / K
```
Choose K such that `E[σ_i² / K] ≪ Var(x)`. Increasing K is useful when within-question variance dominates.

**Token probabilities (zero within-question variance):** If evaluation can be reduced to the probability of the correct token(s), use `s_i = p_i` (the probability of the ground truth response). This eliminates stochastic sampling variance entirely (`σ_i² = 0`). For multiple tokens: `p(response) = ∏ p(token_t | preceding tokens)`.

Caveats: many closed models don't expose token probabilities; reasoning models (long CoT) make this harder to compute; LLM-judge pipelines introduce their own variance.

> *"Do not adjust sampling temperature for variance reduction — this changes the underlying response distribution and makes the result incomparable to the original model."*

### Recommendation 4 — Paired model comparison

**Unpaired (separate question sets):** Compute SE of the difference `S̄_A - S̄_B` as `sqrt(SE_A² + SE_B²)`. Build a CI for the difference and check whether it excludes zero.

Note: checking whether two separate CIs overlap is *more conservative* than computing a CI for the difference directly.

**Paired (same question set):** Compute per-question score differences `d_i = s_i^A - s_i^B`, then apply SE formula to `{d_i}`. The variance of the paired difference is:
```
Var(S̄_A - S̄_B) = Var(S̄_A) + Var(S̄_B) - 2·Cov(S_A, S_B)
```
Since models tend to agree on which questions are hard, `Cov > 0` → **paired analysis is strictly better** whenever models are evaluated on the same questions.

Report: pairwise difference, SE, CI, and inter-model score correlation.

---

## Power Analysis [1]

**Power** = ability to detect a true performance difference when it exists. Key quantities:
- `α` — significance level (false positive rate); typically 0.05
- `1 - β` — power (true positive rate); typically 0.80 or 0.90
- `δ` — minimum detectable effect (MDE): the smallest gap you want to reliably detect

**Sample size formula:** Given `α`, `1 - β`, and `δ`, solve for the required `n`. Key insight:

> *Detecting a gap half the size requires 4× the number of questions (quadratic relationship).*

**Inversion:** Rearrange the formula to solve for MDE given a fixed `n` → determines whether a benchmark is even capable of detecting the improvement you care about.

---

## Related Papers

### [2] Don't Use CLT for n < ~few hundred [Bowyer et al., 2025]

Extensive simulations show **CLT-based CIs consistently fail when n < 100** — they are too narrow and overconfident across all evaluation settings (IID, clustered, paired, unpaired).

Special failure case: when a model scores 0% or 100% on a tiny benchmark, all scores are identical → SE → 0 → CI collapses to a point.

**Alternatives:** Bayesian methods (Beta-Binomial posterior, etc.) are less sensitive to small n, extend naturally to clustered and paired settings, and perform no worse at large n.

### [3] Quantifying Variance in Evaluation Benchmarks [Madaan et al., 2024]

Large-scale study: 280+ models (Llama-2-7B variants with different seeds + checkpoints), 13 benchmarks.

**Key findings:**
- Smaller benchmarks (COPA, HumanEval) have higher variance — emphasizes the need for large n
- Some benchmarks show near-random performance for smaller models → benchmark is only informative at certain capability levels
- **Continuous metrics (token probabilities) substantially improve SNR and monotonicity** compared to binary correct/wrong scores
- **MMLU-Cloze:** reformulating MMLU as a completion task (log-likelihood of correct answer) instead of multiple choice drastically reduces variance

### [4] Signal and Noise Framework [Heineman et al., 2025]

Proposes an SNR metric for benchmark reliability:
- **Signal** = `(max_score - min_score) / mean_score` across models — captures how well the benchmark discriminates
- **Noise** = `std(scores over last n checkpoints) / mean` — captures sensitivity to training randomness

**Practical tips:**
- Select high-SNR sub-tasks from large benchmarks (e.g., 16 of 57 MMLU tasks) → improves reliability and reduces cost
- Average evaluation scores across the last n training checkpoints instead of just the final one → smooths training noise
- Use log likelihood (bits-per-byte) of correct completions rather than discrete accuracy

---

## Recommended Reporting Format

| Situation | What to report |
|---|---|
| Single model, IID questions | Mean, SE, 95% CI, n |
| Single model, clustered questions | Mean, clustered SE, 95% CI, n, C (clusters) |
| Comparing two models, same questions | Per-question differences, paired SE, CI, inter-model correlation |
| Designing a new benchmark | Sample size from power analysis formula, or MDE given fixed n |

---

## Key Takeaways

- **Standard errors and CIs are cheap** — compute them with one extra line of code; not reporting them is inexcusable.
- **CLT requires n ≥ several hundred** — below that, use Bayesian alternatives.
- **Non-independent questions inflate confidence** — always check for clusters in your evaluation data.
- **Resampling and token probabilities reduce variance** — token probs are the gold standard when accessible.
- **Paired comparisons dominate unpaired** — use them whenever both models see the same questions.
- **Continuous metrics (log-likelihood) beat binary accuracy** — more informative, less noisy, consistently recommended by [1], [3], and [4].
