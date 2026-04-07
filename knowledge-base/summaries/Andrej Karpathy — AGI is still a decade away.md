# Andrej Karpathy — AGI is still a decade away

**Source:** [[raw/articles/Andrej Karpathy — AGI is still a decade away]]  
**Author:** Andrej Karpathy (interviewed by Dwarkesh Patel)  
**Related:** [[summaries/Continual Learning with RL for LLMs]] · [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]]

---

## Core Idea

Karpathy argues for calibrated optimism: LLMs are impressive but cognitively incomplete. AGI will arrive on a decade timescale — not months — because the missing capabilities (continual learning, genuine reasoning, culture, self-play) are tractable but difficult. When it does arrive, it will blend into the existing exponential of technological progress rather than producing a discontinuous explosion.

---

## AGI Is a Decade Away

### Why Not a Year?

Karpathy reacts against "year of agents" hype. Current agents are early — impressive but unreliable. Deployed as an employee/intern analog, they fail because:

- Insufficient intelligence for novel, non-boilerplate tasks
- No continual learning — can't retain information across sessions
- Cognitive deficits across many dimensions
- Missing the "march of nines" of reliability needed for production use

### Why Not 50 Years?

Problems are tractable. 15 years of field experience calibrates intuition that the challenges are solvable, just not fast.

---

## LLM Cognitive Deficits

Karpathy's brain-part framing: transformers ≈ cortical tissue (highly plastic, general-purpose). But missing:

| Brain Region | Function | LLM Status |
|---|---|---|
| Prefrontal cortex | Planning, reasoning | Partial (reasoning traces) |
| Basal ganglia | RL-based learning | Partial (RLHF/PPO) |
| Hippocampus | Long-term memory consolidation | Missing |
| Amygdala | Emotions, instincts | Missing |

**The key gap:** No equivalent of sleep's distillation process — taking context-window experience, analyzing it, doing synthetic data generation, and crystallizing it back into weights.

---

## In-Context Learning vs. Weights

| | Weights (pretraining) | Context window |
|---|---|---|
| Analogy | Hazy recollection of what you read a year ago | Working memory |
| Compression | 15T tokens → billions of params (~0.07 bits/token) | 320 KB per token in KV cache |
| Access | Diffuse, imprecise | Direct, precise |
| Effect | Background knowledge | Active reasoning |

In-context learning may implement a form of gradient descent internally — papers have shown transformers can learn linear regression in-context using attention-based mechanics analogous to an optimizer.

---

## RL Is Terrible (But Everything Else Is Worse)

### The Problem With Outcome-Based RL

> "Sucking supervision through a straw."

Standard RL process: run hundreds of rollouts, get a final binary reward, upweight *every token* in successful trajectories regardless of quality. Problems:

- Every wrong turn en route to a correct answer gets upweighted
- Reward signal is delayed and sparse across the entire trajectory
- High variance — noise dominates signal
- No equivalent of human review: "these steps were good, those weren't"

**Humans don't do this.** Human learning involves reflective review of which sub-steps were good or bad, not blanket trajectory upweighting.

### Process-Based Supervision: Why It's Hard

Assigning partial credit at each step requires an automatable credit-assignment scheme. LLM judges for this are gameable: models find adversarial inputs that get 100% reward despite producing nonsense (e.g., "dhdhdhdh"). There are infinitely many such adversarial examples.

### What's Needed

- Reflect-and-review: models that assess their own trajectory sub-steps
- Synthetic problem generation with diversity (not collapsed distribution)
- Something analogous to human sleep: distilling context-window experience into weights

---

## Model Collapse

LLMs are "silently collapsed" — their output distribution covers a tiny manifold of possible responses.

- Ask for a joke: you get the same 3 jokes every time
- Any individual sample looks reasonable, but the *distribution* lacks entropy

**Why it matters for synthetic data:** Training on model-generated data imports this collapse. The model will eventually drift off-rails if the training loop becomes too self-referential.

**Human analogy:** Children are not yet collapsed — they say surprising, off-distribution things. Adults become increasingly collapsed over their lifetimes (learning rates slow, diversity of thought decreases).

**Dreaming hypothesis:** Sleep/dreaming may be an evolutionary mechanism to inject entropy and prevent biological overfitting — putting you in weird situations unlike waking reality.

---

## Pre-Training as "Crappy Evolution"

Evolution ≠ pre-training, but they're analogous:

| | Evolution | Pre-Training |
|---|---|---|
| What it produces | Organisms with baked-in priors | LLMs with baked-in knowledge + algorithms |
| Process | Outer-loop optimization over generations | Gradient descent on internet text |
| Feasibility | Can't do this artificially | Practically achievable today |

LLMs are not "animals" — they are **ghosts/spirits**: fully digital, born from imitation of human text, a different kind of intelligence starting from a different point in intelligence-space.

Pre-training does two things simultaneously:
1. Encodes knowledge from the internet
2. Develops cognitive algorithms (in-context learning, reasoning circuits, etc.)

**The problem:** Models memorize too much. The knowledge distracts from cognitive function. Karpathy's vision of a **cognitive core**: a model stripped of encyclopedic memory that only retains reasoning algorithms, forced to look things up, ~1B parameters.

---

## AGI Will Blend Into 2% GDP Growth

### The Continuous View

AI is an extension of computing, which has always been automation. Historical pattern:
- Compilers automated assembly code writing
- Search engines are AI (ranking = ML)
- Self-driving is computers performing labor

None of these show up as discontinuous jumps in GDP — they diffuse gradually into the existing exponential.

**Karpathy's prediction:** AI will do the same. No discrete "God in a box" moment. Gradual deployment, gradual capability growth, same 2% growth trajectory.

### The Autonomy Slider

Rather than instant replacement, Karpathy expects:
- AI does 80% of volume; delegates 20% to humans
- Humans supervise teams of AI agents
- New interfaces for managing imperfect AI workers
- Gradual slide from human-primary to AI-primary

### Why Coding First

Code was the natural first domain because:
- Always text-based — perfect fit for text processors
- Pre-built infrastructure (IDEs, diffs, version control)
- LLMs have dense training coverage of code

Non-text domains (slides, physical tasks) lack this infrastructure and are harder to deploy.

---

## Self-Driving as Analogy

**The march of nines:** Each additional 9 of reliability requires the same constant amount of work. A demo at 90% reliability is just the first nine. Getting to 99.999% requires five nines of work.

**Demo-to-product gap:** Impressive demos are easy; production-grade products are hard. Self-driving had a perfect demo in 2014 — yet still not fully deployed at scale.

**Implications for AI:**
- LLM coding agents share this property: mistakes in production code can be catastrophic
- Self-driving is not done yet — deployments are minimal and economically marginal
- Teleoperation centers still exist; humans are more in-the-loop than visible

---

## Multi-Agent Systems and LLM Culture

Two powerful multi-agent ideas that haven't been claimed:

1. **LLM culture:** LLMs editing a growing shared scratchpad, writing books for other LLMs, passing knowledge across instances — no equivalent exists today
2. **Self-play:** LLMs generating problems for other LLMs to solve; always increasing difficulty — like AlphaGo's self-play mechanism

Why not yet? Models are cognitively like "savant kids" — impressive narrow feats, but don't yet have the general cognition to create culture. Culture requires a level of general intelligence we haven't reached.

---

## Education and Eureka Labs

### Vision

Building Starfleet Academy: an elite institution for technical knowledge. Physical + digital tiers.

### What Good Tutoring Is

A good human tutor:
- Rapidly builds a model of the student's current knowledge
- Probes exactly where understanding breaks down
- Serves material at precisely the right difficulty level
- Makes the student the only bottleneck — everything else is solved

No LLM does this today. It's a future research problem.

### Pre-AGI vs Post-AGI Education

| Phase | Motivation | Analogy |
|---|---|---|
| Pre-AGI | Economic — education → employment | Traditional school |
| Post-AGI | Intrinsic — learning for flourishing | Going to the gym |

Post-AGI: people will learn anything because it will be trivially accessible and intrinsically rewarding — like gym culture. The physical strength analogy: we don't need human physical labor for lifting but people still lift weights. We won't need human cognitive labor but people will still want to learn.

---

## Key Takeaways

- **"Decade of agents, not year of agents"** — the bottlenecks are real: reliability, continual learning, cognitive completeness
- **RL is terrible but everything else is worse** — sparse reward signal, high variance, no reflective review; we need fundamental algorithmic improvements
- **Model collapse is a real barrier** — silently collapsed distributions undermine synthetic data generation
- **Cognitive core** — future models may be ~1B params, stripped of encyclopedic memory, forced to look things up
- **AGI blends into 2% GDP growth** — no discontinuous explosion; gradual diffusion just like computers, mobile phones, electrification
- **LLM culture and self-play remain unclaimed** — major capability unlocks that nobody has convincingly solved
- **Education is Karpathy's chosen frontier** — building the equivalent of gym culture for the mind
