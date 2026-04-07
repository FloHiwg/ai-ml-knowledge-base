# Direct Preference Optimization (DPO)

**Source:** [[raw/articles/Direct Preference Optimization (DPO)]]  
**Author:** Cameron R. Wolfe  
**Related:** [[raw/articles/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[raw/articles/Language Model Training and Inference From Concept to Code]] · [[raw/articles/Language Models GPT and GPT-2 - by Cameron R. Wolfe, Ph.D.]]

---

## What it is

DPO is a preference-tuning algorithm for LLMs that solves the same objective as RLHF **without** a separate reward model or RL training. It is applied after pretraining and SFT as part of the post-training alignment step.

The key insight: the LLM policy implicitly encodes a reward model. By reparameterizing the RLHF objective in terms of this implicit reward, DPO reduces alignment to a simple supervised classification loss — optimizable with standard gradient descent over an offline preference dataset.

> *"Your Language Model is Secretly a Reward Model"* — title of the DPO paper [Rafailov et al., 2023]

---

## Prerequisites

- **Pretraining** — trains the LLM from scratch on internet-scale text via next token prediction. See [[raw/articles/Language Model Training and Inference From Concept to Code]].
- **SFT (Supervised Fine-Tuning)** — teaches instruction following. The SFT model becomes the **reference policy** in DPO. See [[raw/articles/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]].
- **Preference data** — a dataset of `(prompt, chosen completion, rejected completion)` triples, annotated by humans or an LLM judge.
- **Bradley-Terry model** — statistical model used to express the probability that one completion is preferred over another, given their rewards: `P(y_w > y_l) = σ(r(x, y_w) − r(x, y_l))`.

---

## The Problem with RLHF

Standard RLHF (PPO-based) requires:
1. Training a separate **reward model (RM)** on the preference dataset.
2. Running **online RL** (e.g. PPO) against the RM, keeping 4 model copies in memory (policy, reference policy, RM, value function).

This is unstable, expensive, and complex to tune. DPO eliminates both the explicit RM and the RL loop.

---

## DPO Derivation (4 steps)

Starting from the standard RLHF objective (maximize expected reward minus a KL penalty weighted by β):

1. **Solve for the optimal policy** — derive the closed-form expression: `π*(y|x) ∝ π_ref(y|x) · exp(r(x,y)/β) / Z(x)`, where `Z(x)` is a normalizing partition function.

2. **Extract an implicit reward** — rearrange the optimal policy expression to express the reward in terms of the policy: `r(x,y) = β · log(π*(y|x) / π_ref(y|x)) + β · log Z(x)`.

3. **Plug into Bradley-Terry** — substitute the implicit reward into the pairwise preference probability. The `Z(x)` terms cancel (they only depend on `x`, not `y`), giving a tractable expression.

4. **Train via MLE** — replace `π*` with a learned policy `π_θ` and minimize the negative log-likelihood (identical in form to reward model training):

$$\mathcal{L}_\text{DPO} = -\mathbb{E}\left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_\text{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_\text{ref}(y_l|x)}\right)\right]$$

---

## Why It Works: Gradient Analysis

The DPO loss gradient has three components:
- **Weighting term** (red): `σ(implicit reward of rejected − chosen)` — upweights examples where the model's implicit reward is wrong.
- **Positive term** (blue): increases log-likelihood of chosen completions.
- **Negative term** (green): decreases log-likelihood of rejected completions.

Without the weighting term (naïve "unlikelihood training"), models degenerate. The weighting is what makes DPO effective.

---

## Practical Implementation

**Training pipeline:**
1. Start from an SFT model (= reference policy `π_ref`).
2. Collect preference pairs `(prompt, chosen, rejected)`.
3. Minimize the DPO loss via MLE. Only 2 model copies needed (policy + frozen reference).

**Key hyperparameter:** `β ∈ [0, 1]` — controls KL constraint strength. Lower β = more aggressive preference adaptation. `β = 0.1` is a common default.

**Offline data caveat:** When using pre-collected datasets (e.g. UltraFeedback), the true reference model is unknown. Mitigation: SFT the reference model on the *chosen* completions before DPO training to reduce distribution shift.

**Tooling:** HuggingFace `trl.DPOTrainer` provides a ready-to-use implementation.

---

## Key Takeaways

| | RLHF (PPO) | DPO |
|---|---|---|
| Reward model | Explicit, separately trained | Implicit, inside the policy |
| Optimization | Online RL (PPO) | Offline MLE (cross-entropy) |
| Model copies in memory | 4 | 2 |
| Stability | Difficult to tune | More stable |
| Performance | Slightly better in large-scale runs | Competitive; sometimes a gap exists |

- DPO is not "reward-model-free" — it *is* reward modeling, just implicit.
- DPO is theoretically guaranteed to yield the same optimal policy as RLHF (proven via reward equivalence class argument).
- A performance gap vs. online RL methods can exist [Tang et al. 2024, Ivison et al. 2024], so DPO is often combined with online RL in modern post-training pipelines.
