# Demystifying Reasoning Models

**Source:** [[raw/articles/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]  
**Author:** Cameron R. Wolfe  
**Related:** [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]] · [[summaries/Direct Preference Optimization (DPO)]] · [[summaries/The Anatomy of an LLM Benchmark]]

---

## Core Idea

Reasoning models are a new paradigm beyond standard LLMs. Instead of directly generating a final answer, they first produce a long chain of thought (long CoT) — thousands of tokens of internal reasoning — before answering. This reasoning trace enables search-like behaviors (decomposition, backtracking, self-critique) and creates a new compute scaling axis: more thinking time at inference = better answers.

---

## Closed Reasoning Models (OpenAI o-series)

| Model | Key result |
|---|---|
| o1-preview | First public reasoning model; rivals PhD experts on GPQA Diamond |
| o1 | 74–93% on AIME 2024 (vs GPT-4o's 12%); top 11th percentile on Codeforces |
| o1-mini | 80% cheaper; strong on coding despite limited world knowledge |
| o3 | 87.5% on ARC-AGI (first to beat human baseline of 85%); 25.2% FrontierMath (prev. SOTA: 2%); 71.7% SWE-Bench Verified |
| o3-mini | Controllable reasoning effort (low/medium/high); 24% faster than o1-mini; supports tool use |

OpenAI provides minimal technical details — only that performance scales with both train-time RL and inference-time compute.

---

## Fundamentals: How Reasoning Models Work

### Two Scaling Axes

1. **Train-time compute via RL** — more RL training → better reasoning capabilities
2. **Inference-time compute** — more thinking → more tokens → better answers

### Long CoT vs Standard CoT

| Standard CoT | Long CoT |
|---|---|
| ~100 tokens | Thousands of tokens |
| Human-readable | Not optimized for readability (shown as summary to users) |
| Single linear rationale | Backtracking, self-correction, solution exploration |
| Elicited by prompting | Trained via RL |

### Inference-Time Strategies

**Parallel decoding:** Generate K outputs, aggregate via majority vote, weighted voting, or Best-of-N (pick top output using a reward model). Linear scaling: K outputs = K× compute = meaningful performance gain.

**Sequential self-refinement:** Generate → critique → revise. Extrinsic refinement (external verifier or code interpreter) works well; intrinsic refinement (LLM critiques itself) works on simple tasks but struggles on complex ones.

### RLVR — RL with Verifiable Rewards

The fundamental training mechanism. Replace the neural reward model of RLHF with a **rules-based verifier**:
- **Math:** extract answer, compare to ground truth via string match (or LLM judge for format variations)
- **Code:** execute in sandbox, check test cases
- **Format:** check token structure, output length, language consistency

Advantages over neural reward models:
- No reward hacking (deterministic signal)
- No separate reward model to train and maintain
- Simpler, cheaper pipeline

Limitation: only applies to verifiable domains. Creative tasks still require neural reward models (with reward hacking risk).

---

## DeepSeek-R1: Open Replication of o1

Built on **DeepSeek-v3** — a 671B Mixture-of-Experts base model with open weights.

### DeepSeek-R1-Zero: Pure RL, No SFT

Train DeepSeek-v3 directly with RL using **GRPO** (Group Relative Policy Optimization — no critic model, cheaper than PPO) and two rewards:
1. **Accuracy reward** — correct final answer (string match or test case pass)
2. **Format reward** — output structured as `<think>…</think><answer>…</answer>`

**What emerges without any SFT:**
- Model learns to generate progressively longer CoTs as training advances
- Develops backtracking, self-correction, and alternative solution exploration spontaneously
- AIME 2024: 15.6% → 71.0% accuracy (86.7% with majority vote over 16 samples)

**Shortcomings:** Poor readability, language mixing, weaker on coding.

### DeepSeek-R1: Four-Stage Pipeline

```
Stage 1: Cold Start SFT
  Small dataset of long CoT examples (thousands)
  Sourced: few-shot prompting of DeepSeek-v3 + human-selected R1-Zero outputs
  Purpose: stable starting point for RL; seeds reasoning style

Stage 2: Reasoning-Oriented RL (same as R1-Zero)
  Adds language consistency reward
  Slightly reduces reasoning peak performance but improves output readability

Stage 3: Rejection Sampling → Large SFT Dataset
  Generate candidate trajectories with stage-2 model
  Filter by correctness (rules-based) + quality (DeepSeek-v3 as weak verifier)
  Result: 600K reasoning + 200K general-purpose examples (800K total)
  Non-reasoning data gets CoT added by DeepSeek-v3 for complex queries

Stage 4: General-Purpose RLHF
  Rules-based rewards for reasoning problems
  Neural reward models (trained on human preferences) for general data
  Trains helpfulness (on final answer only) and harmlessness (full trajectory)
```

**Performance:** Matches or surpasses o1 on most reasoning tasks; strong on general tasks too. Still weaker than standard LLMs on instruction-following benchmarks (IFEval).

### Is SFT Necessary?

- R1-Zero proves SFT is **not required** for reasoning capabilities to emerge
- Cold start SFT is **practically valuable**: stabilizes early RL, speeds convergence, improves quality
- Bottom line: SFT not necessary, but useful if high-quality CoT data is available

### Distilled Models

Fine-tune smaller base models (Qwen-2.5, LLaMA-3) via SFT on the 800K examples from Stage 3 — nothing else.

Key results:
- Distilled Qwen2.5-14B outperforms QwQ-32B-Preview (prior best open reasoning model)
- Distilled 32B/70B models exceed o1-mini on most benchmarks
- **Distillation > direct RL on small models**: reasoning patterns from large models transfer more efficiently than re-learning them from scratch

---

## Benchmark Landscape (Reasoning Era)

| Benchmark | Status | Notes |
|---|---|---|
| GSM-8K, MATH | Saturated | Grade school / high school math — now trivial for reasoning models |
| AIME 2024 | Active frontier | GPT-4o: 12% → o1: 74–93% → o3: ~97% |
| GPQA Diamond | Active frontier | PhD-level science; experts ~70-80% accuracy |
| ARC-AGI | Active frontier | Grid puzzles; GPT-4o: 5% → o3: 87.5% (first to beat human baseline) |
| FrontierMath | Active frontier | Research-level math; previous SOTA 2% → o3: 25.2% |
| SWE-Bench Verified | Active frontier | Real-world coding tasks; o3: 71.7% |

---

## Key Trends

1. **Long CoT as a compute dial** — variable-length reasoning enables dynamic cost/quality trade-offs at inference time
2. **Self-evolution through RL** — reasoning behaviors emerge autonomously from correctly-incentivized RL; no manual behavior engineering needed
3. **Less human supervision** — rules-based rewards replace human preference labeling for reasoning tasks
4. **Distillation is highly effective** — strong reasoning transfers to small models cheaply via SFT on teacher-generated trajectories
5. **New open problems** — safety in long CoT, minimizing overthinking, optimal SFT/RL balance, instruction following in reasoning models, efficient hosting

---

## Key Takeaways

- The move from standard LLMs to reasoning models is **a new training paradigm**, not just a prompting trick
- RLVR + long CoT training + rules-based rewards = the minimal recipe for strong reasoning
- DeepSeek-R1 is the first fully open, replicable reasoning model at o1-level capability
- Inference-time scaling (think longer) and train-time scaling (train with more RL) are both independent performance levers
- The field is reinventing itself: few-shot prompting degrades R1 performance; established practices need revisiting
