# Statistical Evaluation of LLMs

**Related:** [[evaluation/benchmarks]]  
**Sources:** [[summaries/Applying Statistics to LLM Evaluations]]

---

## The Core Problem

Most evaluations report a single accuracy number with no uncertainty. Small differences are used to claim superiority, but it's usually unclear whether the difference is real or noise. **Noise is mistaken for progress.**

---

## Statistical Foundations

### Standard Error (SE)

The standard deviation of the *sample mean estimator* — how much the mean varies across evaluation runs:

```
SE(S̄) = s / sqrt(n)            (general IID case)
SE(S̄) = sqrt(μ̂(1-μ̂) / n)     (Bernoulli / binary scores)
```

Where `s` = sample standard deviation, `n` = number of questions.

**Intuition:** SE decreases as `1/sqrt(n)` — to halve the SE, you need 4× the questions.

### Confidence Intervals

```
95% CI = s̄ ± 1.96 × SE
```

Interpretation: if you repeated the evaluation many times, 95% of such intervals would contain the true mean μ.

**Key point:** Overlapping CIs do not rule out a real difference — check the CI of the *difference* directly (see model comparisons below).

### Central Limit Theorem (CLT)

The distribution of sample means approaches normal as `n` grows. **Requires:** IID questions, finite variance, and sufficiently large `n`.

**Warning:** The CLT fails (CIs too narrow, overconfident) when `n < 100`. Use Bayesian alternatives in small-data regimes.

---

## Four Recommendations [Anthropic, 2024]

### 1. Report Standard Errors (IID questions)

```
Model A | MMLU: 0.72 ± 0.013 | GSM-8K: 0.61 ± 0.021
```

Always report SE alongside the mean. Computing it requires one extra line of code.

### 2. Clustered Standard Errors (non-IID questions)

When questions are correlated (same topic, same document, same prompt in different languages), the IID formula **underestimates uncertainty** — CIs are too narrow.

**Clustered SE:** Treat questions within a cluster as correlated; questions across clusters as independent. In practice, the clustered SE can be **3× larger** than the naive CLT SE.

Report: mean, clustered SE, CI, number of questions `n`, number of clusters `C`.

### 3. Variance Reduction

The variance of an evaluation score decomposes into:
1. `Var(x)` — variability across question difficulty (irreducible)
2. `E[σ_i²]` — within-question variance from stochastic generation

**Resampling:** Generate `K` completions per question, average their scores. Reduces within-question variance by `K`. Choose K such that `E[σ_i²/K] ≪ Var(x)`.

**Token probabilities (best):** Use `P(correct response)` directly as the score — eliminates within-question variance entirely (`σ_i² = 0`). For multi-token responses: `P(response) = ∏ P(token_t | preceding tokens)`.

> *Never adjust temperature for variance reduction — it changes the response distribution.*

### 4. Paired Model Comparisons

When both models are evaluated on the **same questions**, analyze per-question differences:

```
d_i = s_i^A - s_i^B   (score difference for question i)
SE(d̄) = std(d) / sqrt(n)
```

**Why paired beats unpaired:** Models tend to agree on which questions are hard — their scores are positively correlated. The paired SE accounts for this, yielding a smaller (more precise) SE.

The CI for the difference excludes zero → statistically significant performance difference.

**Reporting:** pairwise difference, SE, CI, inter-model score correlation.

---

## Power Analysis

**Power** = probability of detecting a true performance difference when it exists.

**Sample size formula:** Given desired significance `α`, power `1-β`, and minimum detectable effect `δ`, solve for the required `n`.

**Key insight:** Detecting a gap half the size requires **4× the questions** (quadratic).

**Inversion:** Given fixed `n`, compute the minimum detectable effect — determines whether a benchmark is capable of detecting the improvement you care about.

Use cases:
- Check if an evaluation is worth running before collecting data
- Determine sample size when curating a new benchmark

---

## Related Findings from Empirical Studies

### CLT Failures (Bowyer et al. 2025)

CLT-based CIs fail across **all evaluation settings when n < 100**. Especially bad when a model scores 0% or 100% on a small dataset (all scores identical → SE collapses to 0).

Alternatives: Bayesian methods (Beta-Binomial posterior) — less sensitive to n, extend to clustered/paired settings.

### Continuous Metrics Beat Binary (Madaan et al. 2024; Heineman et al. 2025)

Evaluating via token probabilities (log-likelihood of correct completion) rather than binary correct/wrong improves:
- Signal-to-noise ratio (SNR) across benchmarks
- Monotonicity of improvement across training checkpoints

**MMLU-Cloze:** Reformulating MMLU as completion-based (log-likelihood of correct answer) vs. multiple choice drastically reduces variance.

### SNR for Benchmark Selection (Heineman et al. 2025)

Define SNR = signal / noise where:
- `signal = (max_score - min_score) / mean_score` across models
- `noise = std(scores over last n checkpoints) / mean`

Practical tips from SNR analysis:
- Select high-SNR sub-tasks from large benchmarks (16 of 57 MMLU tasks → improved reliability + 3× cheaper)
- Average scores over last `n` training checkpoints to smooth training noise

---

## Recommended Reporting Format

| Situation | Report |
|---|---|
| Single model, IID questions | mean, SE, 95% CI, n |
| Clustered questions | mean, clustered SE, CI, n, C |
| Two models, same questions | pairwise difference, paired SE, CI, correlation |
| New benchmark design | power analysis → required n, or MDE for given n |
