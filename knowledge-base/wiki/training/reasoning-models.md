# Reasoning Models

**Related:** [[training/fine-tuning]] · [[training/pretraining]] · [[inference/prompting-and-reasoning]] · [[inference/decoding-strategies]] · [[evaluation/benchmarks]]  
**Sources:** [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]

---

## What Is a Reasoning Model?

A reasoning model generates a long **chain of thought (long CoT)** before producing its final answer. This reasoning trace — thousands of tokens of internal deliberation — exhibits search-like behaviors the standard next-token paradigm cannot:

- Problem decomposition
- Backtracking when a path fails
- Exploring alternative solutions
- Self-critique and error detection

The key shift from a standard LLM is the **two-phase output**: think first (long CoT), then answer.

---

## Two New Scaling Axes

Standard LLM progress is driven by pretraining scale (more data + larger models). Reasoning models add two orthogonal levers:

| Axis | How to scale | Effect |
|---|---|---|
| **Train-time** | More RL training | Better reasoning capabilities |
| **Inference-time** | Longer CoT (more tokens) | Better answers on harder problems |

Both axes show consistent improvements — this is a qualitatively new form of scaling beyond pretraining.

---

## RLVR — RL with Verifiable Rewards

The fundamental training mechanism for reasoning models. Instead of a neural reward model (trained on human preferences), use a **rules-based verifier** as the reward signal.

### Verification by domain

| Domain | Verification method |
|---|---|
| Math | Extract final answer → string match vs. ground truth (or LLM judge for format variants) |
| Code | Execute in sandbox → check all test cases pass |
| Format | Check output structure (e.g., `<think>…</think><answer>…</answer>`) |
| Length/style | Simple rule checks |

### Why rules-based over neural rewards?

- **No reward hacking** — deterministic, cannot be gamed
- **No reward model to train** — saves compute, simplifies pipeline
- **Reliable at scale** — neural rewards become increasingly gameable during extended RL

**Limitation:** Only applies to verifiable domains. Open-ended tasks (creative writing) still need neural reward models — with their reward-hacking risk.

---

## GRPO — Group Relative Policy Optimization

The RL algorithm used by DeepSeek-R1. Alternative to PPO:

- **No critic model** (PPO uses a value network the same size as the policy — expensive)
- Generate a group of K responses → compare them relative to each other → reward the better ones
- Cheaper and simpler than PPO with competitive performance

The trend: RL algorithms for LLMs are simplifying (PPO → GRPO → REINFORCE variants) while RL training scale increases.

---

## Inference-Time Strategies

### Parallel Decoding (Best-of-N / Majority Vote)

Generate K outputs independently, aggregate:
- **Majority vote:** pick the most common final answer
- **Weighted voting:** weight by confidence / reward score
- **Best-of-N (rejection sampling):** score all K outputs with a verifier, pick the best

Linear scaling: K outputs = K× inference cost = meaningful performance boost. Used explicitly by o1 models (their evaluation plots show "64 parallel samples").

### Sequential Self-Refinement

Generate → get feedback → revise → repeat:
- **Extrinsic feedback** (from verifier, code interpreter, external tool): generally effective
- **Intrinsic feedback** (LLM critiques its own output): works on simple tasks; unreliable on complex reasoning

### Long CoT as a Compute Dial

CoT length is a continuous knob: longer trace = more tokens = more compute = better answers. o3-mini makes this explicit with low/medium/high effort settings.

---

## DeepSeek-R1: Open Replication of o1

Built on DeepSeek-v3 (671B MoE, open weights).

### R1-Zero: Pure RL, No SFT

```
Base model (DeepSeek-v3)
  ↓ GRPO with two rewards:
  • Accuracy reward (correct final answer)
  • Format reward (<think>…</think><answer>…</answer>)
  ↓
DeepSeek-R1-Zero
```

**What emerges from RL alone:**
- Progressively longer CoTs as training advances (model learns to use more thinking time)
- Backtracking and alternative solution exploration — not explicitly trained, emergent
- AIME 2024: 15.6% → 71.0% (86.7% with 16-sample majority vote)

**Shortcomings:** Language mixing, poor readability, weaker coding.

### R1: Four-Stage Pipeline

```
Stage 1 — Cold Start SFT
  Thousands of long CoT examples (from DeepSeek-v3 + R1-Zero outputs)
  Seeds reasoning style; stabilizes RL starting point

Stage 2 — Reasoning RL
  Same as R1-Zero + language consistency reward
  Boosts reasoning; slight readability improvement

Stage 3 — Rejection Sampling → Large SFT Dataset
  Generate trajectories → filter by correctness/quality
  600K reasoning + 200K general examples = 800K total SFT dataset

Stage 4 — General RLHF
  Rules-based rewards for reasoning problems
  Neural reward models (helpfulness + harmlessness) for general data
```

**Result:** Matches o1 on most reasoning benchmarks; handles general tasks well.

### Is SFT Necessary?

R1-Zero proves SFT is **not required** for reasoning to emerge. But cold start SFT:
- Eliminates instability in early RL training
- Speeds convergence
- Improves output quality and readability

Verdict: not necessary, but practically valuable when high-quality CoT data is available.

---

## Distillation: Cheap Reasoning for Small Models

Take the 800K SFT dataset from Stage 3 of R1's training. Fine-tune smaller base models (Qwen-2.5, LLaMA-3) on it via standard SFT. That's it.

**Results:**
- Distilled Qwen2.5-14B > QwQ-32B-Preview (prior best open reasoning model)
- Distilled 32B/70B > o1-mini on most benchmarks
- **Distillation > direct RL on small models** — reasoning patterns from large models transfer more efficiently than learning from scratch

**Key insight:** The reasoning *patterns* discovered by large models via expensive RL are what matter — and those can be transferred to small models via cheap SFT.

---

## Model Landscape

| Model | Provider | Notable results |
|---|---|---|
| o1-preview / o1 | OpenAI | AIME 2024: 74–93% (vs GPT-4o 12%) |
| o1-mini | OpenAI | 80% cost reduction; strong coding |
| o3 | OpenAI | ARC-AGI 87.5%, FrontierMath 25.2%, AIME ~97% |
| o3-mini | OpenAI | Controllable effort; fastest o-series |
| Gemini 2.0 Flash Thinking | Google | 1M context; lags behind o1 |
| Grok-3 reasoning beta | xAI | Closest competitor to o3-mini at release |
| DeepSeek-R1-Zero | DeepSeek | First open pure-RL reasoning model |
| DeepSeek-R1 | DeepSeek | Matches o1; fully open with replication details |

---

## Benchmark Context

| Benchmark | Pre-reasoning SOTA | Reasoning model SOTA |
|---|---|---|
| GSM-8K / MATH | Near-saturated | Fully saturated — no longer useful |
| AIME 2024 | GPT-4o: 12% | o3: ~97% |
| GPQA Diamond | GPT-4o: ~50% | o1/R1: rivals PhD experts |
| ARC-AGI | GPT-4o: 5% | o3: 87.5% (first to beat human 85%) |
| FrontierMath | ~2% | o3: 25.2% |

---

## Key Trends

1. **Long CoT is the medium, RL is the teacher** — the reasoning trace enables search; RL discovers the strategy
2. **Self-evolution** — backtracking, reflection, exploration emerge from incentives alone, not from explicit programming
3. **Less human supervision** — verifiable rewards replace preference labels for core reasoning training
4. **Distillation democratizes reasoning** — cheap SFT transfers powerful reasoning to accessible model sizes
5. **New open problems** — overthinking, safety in long CoT, instruction following in reasoning models, efficient hosting

---

## Relationship to Other Concepts

- Builds on [[training/fine-tuning]] SFT + RLHF foundations, but replaces the reward model with rules-based verifiers
- Long CoT is a trained capability, not just a prompting technique (contrast with [[inference/prompting-and-reasoning]] CoT)
- Creates new benchmark saturation pressure — see [[evaluation/benchmarks]]
- Represents a new [[concepts/scaling-and-the-bitter-lesson|scaling law]]: compute at inference time, not just training time
