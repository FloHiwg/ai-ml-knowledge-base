# AGI and the Nature of Intelligence

**Related:** [[concepts/scaling-and-the-bitter-lesson]] · [[concepts/foundation-models]] · [[training/pretraining]] · [[training/continual-learning]] · [[training/reasoning-models]]  
**Sources:** [[summaries/Andrej Karpathy — AGI is still a decade away]]

---

## What LLMs Are (and Aren't)

LLMs are not artificial animals. They are **ghosts** — fully digital entities born from imitating human text, starting from a different point in intelligence-space than biological minds.

| | Animals | LLMs |
|---|---|---|
| Origin | Evolution (outer loop) | Gradient descent on internet text |
| Prior knowledge | Baked in via DNA/brain wiring | Compressed from training corpus |
| Learning process | Evolution + lifetime experience | Pretraining + RLHF/fine-tuning |
| Memory consolidation | Sleep / synaptic replay | No equivalent — stateless at inference |

**Pre-training as "crappy evolution":** Pretraining is the practically achievable substitute for evolution. It produces a starting point with broad knowledge and cognitive algorithms, analogous (imperfectly) to what evolution bakes into an organism's brain.

---

## LLM Cognitive Architecture

Transformers ≈ cortical tissue — highly plastic, domain-general, trainable on any modality. Beyond that, the brain-part analogy gets approximate:

| Brain Region | Function | LLM Analog |
|---|---|---|
| Cortex | General pattern learning | Transformer layers |
| Prefrontal cortex | Planning, reasoning | Reasoning traces (thinking models) |
| Basal ganglia | RL-based reinforcement | RLHF / PPO fine-tuning |
| Hippocampus | Long-term memory formation | **Missing** |
| Sleep / synaptic replay | Distilling experience into memory | **Missing** |

### The Missing Sleep Equivalent

Humans distill context-window experience into long-term memory during sleep:
- Review the day's events
- Generate synthetic scenarios
- Consolidate important patterns into weights

LLMs have no equivalent. Every session starts from scratch with zero tokens. The analogy: as if you went to sleep and woke up with no memory of yesterday, but with all your general knowledge intact.

---

## Memory: Weights vs. Context Window

| | Weights (pretraining) | Context window (KV cache) |
|---|---|---|
| Analogy | Hazy long-term memory | Active working memory |
| Compression | ~0.07 bits per training token | ~320 KB per context token |
| Precision | Diffuse, probabilistic | Exact and directly accessible |
| Lifetime | Permanent (until fine-tuned) | Session-only |

Everything in the context window is immediately accessible. Everything in the weights is a hazy recollection — like remembering a book you read a year ago vs. having it open in front of you.

**Implication:** Giving a model relevant text in context dramatically outperforms relying on its parametric memory for specific facts.

---

## The Cognitive Core

Current LLMs memorize too much — encyclopedic recall of internet text that may actually impede generalization. The vision of a **cognitive core**:

- A model stripped of encyclopedic memory, retaining only reasoning algorithms
- Forced to look things up externally; knows what it doesn't know
- Estimated: ~1B parameters once trained on a high-quality cognitive curriculum
- Analogous to human intelligence: humans are poor at memorization, which is a *feature* — it forces generalization

The internet is mostly low-quality text. Current large models are big partly because they have to compress enormous amounts of noise alongside the signal. Better pre-training data → smaller models with the same cognitive capability.

---

## LLM Cognitive Deficits

Why agents aren't yet reliable employees:

- **Continual learning:** No persistent memory across sessions; see [[training/continual-learning]]
- **Reliability / march of nines:** Each 9 of reliability requires constant work; demos ≠ products
- **Model collapse:** Outputs are silently collapsed — low entropy, limited diversity
- **Novel code / novel tasks:** Strong on common patterns from training data; struggles with genuinely new architectures or off-distribution problems
- **Off-data-manifold reasoning:** Heavy reliance on memorized patterns prevents going beyond what's in training data

---

## Model Collapse

LLM outputs are "silently collapsed" — any individual sample looks plausible, but the *distribution* occupies a tiny manifold:

- Ask for a joke: same 3 jokes every time
- Ask for 10 reflections on a chapter: nearly identical results

**Why this matters:**

1. **Synthetic data generation:** Training on model-generated data imports the collapse, eventually causing the model to drift or degrade
2. **Creative tasks:** Models won't explore the full space of valid responses
3. **Self-improvement loops:** Recursive self-training amplifies the collapse

**Human analogy:** Children (uncollapsed) say surprising, off-distribution things. Adults increasingly revisit the same thoughts. The collapse worsens with age/overfitting.

**Dreaming hypothesis:** Sleep/dreaming may prevent biological collapse by injecting out-of-distribution scenarios, maintaining entropy in neural representations.

---

## RL Limitations

See [[training/reasoning-models]] for full RLVR/GRPO coverage. Karpathy's critique of standard RL:

**"Sucking supervision through a straw"**

Standard outcome-based RL:
1. Run hundreds of rollouts
2. Check only the final answer
3. Upweight *every token* in correct trajectories — including detours and wrong turns

Problems:
- High variance: noisy signal broadcast across entire trajectory
- No credit assignment: good sub-steps can't be distinguished from lucky bad ones
- Not how humans learn: humans reflectively review which sub-steps were good/bad

**Process-based supervision** would fix this but is hard: LLM judges are gameable — models find adversarial inputs (e.g., "dhdhdhdh") that fool the judge into assigning full reward.

What's needed: reflect-and-review mechanisms where models assess their own reasoning trajectories sub-step-by-step.

---

## AGI and Economic Impact

### The Gradual Diffusion View

AI is an extension of computing. Historical pattern: every major technology (computers, mobile phones, the internet) diffuses gradually into the economy without producing a discontinuous jump in GDP growth.

- Computers are labor automation — yet no GDP kink is visible
- Self-driving is computers performing physical labor — still no macroeconomic jump
- AI coding assistants follow the same pattern

**Prediction:** AI will blend into the existing ~2% GDP growth exponential, not produce a sharp takeoff.

### Why Coding First

Code was the first domain to show genuine economic AI value:
- Always text-based — perfect for text processors
- Rich pre-existing infrastructure (IDEs, diffs, version control, test suites)
- Dense training data coverage

Non-text domains (slides, physical manipulation) lack this infrastructure.

### The Autonomy Slider

Automation is continuous, not binary. The pattern: AI does 80% of volume, humans handle the remaining 20% and supervise AI teams. Gradual abstraction upward, not instant replacement.

---

## Multi-Agent Systems and LLM Culture

Two powerful multi-agent ideas not yet demonstrated convincingly:

**1. LLM culture:** LLMs maintaining a growing shared scratchpad, writing artifacts for other LLMs, passing knowledge across instances. Analogous to human cultural accumulation of knowledge across generations.

**2. Self-play:** LLMs generating problems for other LLMs to solve, with ever-increasing difficulty. Analogous to AlphaGo's self-play dynamic, or evolution's competitive pressure driving intelligence.

**Why not yet:** Current models are cognitively like savant children — impressive narrow feats, no general cognition. Culture requires the level of general intelligence to know what's worth recording and transmitting.

---

## Intelligence Timelines

Karpathy's framework:
- Problems are tractable but difficult
- Missing capabilities (continual learning, genuine RL reform, culture, self-play) require multiple research breakthroughs
- Each reliability improvement = another nine; demos are at one or two nines
- Self-driving as calibration: perfect Waymo demo in 2014, still not commercially viable at scale in 2025

**"It's the decade of agents, not the year of agents."**

