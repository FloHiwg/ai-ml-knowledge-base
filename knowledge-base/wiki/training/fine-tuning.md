# Fine-Tuning: SFT, RLHF, and DPO

**Related:** [[training/pretraining]] · [[concepts/foundation-models]] · [[training/continual-learning]]  
**Sources:** [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Direct Preference Optimization (DPO)]] · [[summaries/Continual Learning with RL for LLMs]]

---

## The Three-Stage Pipeline

```
Pretraining  →  SFT  →  Alignment (RLHF or DPO)
```

Pretraining produces a foundation model with broad knowledge. SFT and alignment make it useful and safe for human interaction.

---

## SFT — Supervised Fine-Tuning

Train the pretrained model on a **curated dataset of (prompt, response) pairs** using the same next-token prediction objective as pretraining.

### What It Does

Shifts the model's output distribution from "continuation of internet text" toward "helpful responses to instructions." The model already has the knowledge; SFT teaches it how to express it in the desired format.

### Data Quality Over Quantity

The LIMA paper showed 1,000 high-quality examples can outperform 50,000 mediocre ones. Key principle: **quality beats quantity**.

| Approach | Data size | Result |
|---|---|---|
| Mediocre web-scale data | 50K+ | Mediocre |
| Carefully curated examples | 1K–10K | Often better |

### Imitation Learning

Using a stronger proprietary model (e.g., GPT-4) to generate SFT training data for a smaller open model. Risks:
- Legal/policy issues with providers
- Smaller model may inherit failure modes of the teacher without inheriting its reasoning

### PEFT — Parameter-Efficient Fine-Tuning

Freeze most weights; only fine-tune a small subset (e.g., via LoRA — Low Rank Adaptation). Prevents **catastrophic forgetting** (when training on task B destroys performance on task A). Much cheaper than full fine-tuning.

### When to Use SFT Alone

- Adapting to a new domain's style or format
- Teaching a specific output structure (JSON, SQL, etc.)
- Small, well-defined tasks with high-quality labeled data

SFT alone doesn't teach the model to *prefer* good responses over bad ones — that requires preference learning.

---

## RLHF — Reinforcement Learning from Human Feedback

### Process

1. Collect **preference data**: humans compare pairs of model outputs, marking which is better
2. Train a **reward model** to predict human preferences from these comparisons
3. Use RL (PPO) to optimize the LLM's policy to maximize the reward model's score, while staying close to the SFT reference policy (KL penalty)

### KL Penalty

Without regularization, the LLM would find adversarial prompts that "hack" the reward model. The KL divergence penalty keeps the optimized model close to the SFT reference:

```
maximize: E[reward(response)] - β · KL(policy || reference)
```

### Challenges

- Reward model may be inaccurate or gameable
- PPO is computationally expensive and tricky to tune
- Requires a reward model trained separately before RL

---

## DPO — Direct Preference Optimization

### The Insight

The optimal policy under the RLHF objective can be expressed analytically in terms of a log probability ratio. This lets you **reparameterize the reward function directly in terms of the language model** — eliminating the need for a separate reward model.

### How It Works

Given preference pairs `(y_w, y_l)` — a preferred and a dispreferred response — DPO directly maximizes:

```
L_DPO(θ) = -E [ log σ( β · log[π_θ(y_w|x)/π_ref(y_w|x)] 
                      - β · log[π_θ(y_l|x)/π_ref(y_l|x)] ) ]
```

- `π_θ` = model being trained
- `π_ref` = frozen SFT reference model
- `β` = temperature (how strongly to enforce preferences)

The model is pushed to **increase the probability of preferred responses relative to the reference** and **decrease the probability of dispreferred responses relative to the reference**.

### DPO vs RLHF

| | RLHF | DPO |
|---|---|---|
| Reward model | Separate, must be trained | Implicit in the LM |
| RL step | Required (PPO) | Not needed |
| Stability | Tricky to tune | Simpler |
| Performance | Strong | Competitive |
| Compute | Higher | Lower |

### Gradient Intuition

The DPO gradient simultaneously:
1. Increases likelihood of preferred completions that the model currently underestimates
2. Decreases likelihood of dispreferred completions that the model currently overestimates

Where the model already ranks preferred > dispreferred, the gradient contribution is small (the weight `σ(...)` is small when the model is already correct).

---

## Summary: When to Use What

| Goal | Approach |
|---|---|
| Teach format / domain knowledge | SFT |
| Align to human preferences (cheap) | DPO |
| Align to human preferences (max performance) | RLHF |
| Fine-tune without forgetting | PEFT / LoRA |
| Math/code with verifiable rewards | RLVR (GRPO/PPO variant) → see [[training/reasoning-models]] |
| Adapt without forgetting prior capabilities | RL (on-policy) → see [[training/continual-learning]] |
