# AINews: Is Harness Engineering Real? — Latent.Space

**Source:** [[raw/articles/AINews Is Harness Engineering real - Latent.Space]]
**Author:** swyx (Latent.Space / AINews)
**Related:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]] · [[summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]] · [[summaries/The Bitter Lesson]]

---

## Core Idea

A debate synthesis from Latent.Space's AINews (March 2026) framing the central tension in agent engineering: **Big Model** (harnesses are temporary scaffolding that better models will make obsolete) vs. **Big Harness** (the harness is the product, and context/workflow engineering is the primary leverage point). The article presents evidence on both sides and concludes harness engineering has real value — with Cursor's $50B valuation as market proof.

---

## The Framing: Seat vs. Skill

The article opens with a finance analogy: when a trader makes $3M in profits, how much is the trader's skill vs. the institution/position/seat? The same question applies to coding agents: when an agent solves a hard problem, how much credit goes to the model vs. the harness?

This is the **Big Model vs. Big Harness** divide.

---

## Big Model Arguments

Evidence that harnesses are noise or temporary scaffolding:

| Source | Argument / Evidence |
|---|---|
| **Claude Code team (Boris Cherny, Cat Wu)** | "All the secret sauce is in the model. This is the thinnest possible wrapper over the model. We literally could not build anything more minimal." Claude Code has been rewritten from scratch every 3–4 weeks; complexity consistently drops over time. |
| **Noam Brown (OpenAI)** | Pre-reasoning-model era: elaborate agentic scaffolding made many calls to GPT-4o to simulate reasoning. Reasoning models arrived and rendered that scaffolding unnecessary — "you just give the reasoning model the same question without any sort of scaffolding and it just does it." Predicts current scaffolds will similarly be replaced. Also notes model routers will become unnecessary as labs move toward a single unified model. |
| **METR evaluation** | Found that Claude Code and Codex don't beat a basic scaffold on the tasks they tested. |
| **Scale AI SWE-Atlas** | Opus 4.6 scores 2.5 points better in Claude Code than in SWE-Agent, but GPT-5.2 shows the reverse — making harness choice essentially noise within margin of error across models. |

---

## Big Harness Arguments

Evidence that the harness is the primary leverage point:

| Source | Argument / Evidence |
|---|---|
| **"The Harness is the Product"** | Every production agent converges on the same core loop: `while (model returns tool calls): execute tool → capture result → append to context → call model again`. Claude Code, Cursor's agent, and Manus all fit inside that loop. The loop itself is the product. |
| **Jerry Liu (LlamaIndex)** | "The biggest barrier to getting value from AI is your own ability to context and workflow engineer the models. This is especially true the more horizontal the tool you're using." |
| **Pi blog** | "Improving 15 LLMs at Coding in One Afternoon — Only the Harness Changed": dramatic improvements across all 15 models when the harness was optimized. |

---

## The Synthesis

Neither camp is disinterested: Big Model labs sell models; Big Harness companies sell harnesses. The traditional AI field response is a milquetoast "compound AI" position that says both are valuable.

But the article argues the times are changing. Evidence that harness engineering has real, durable value:
- **Cursor valued at $50B** — a product that is fundamentally harness engineering on top of frontier models
- **AI Engineer Europe** added the world's first Harness Engineering track
- The "Bitter Lesson" applies differently in agentic settings: general methods at scale beat hand-crafted approaches over time, but the harness is the channel through which model capability is expressed — optimizing it has non-trivial leverage while model improvements are uncertain and out of the builder's control

See [[wiki/concepts/scaling-and-the-bitter-lesson]] for the Bitter Lesson context, and [[wiki/applications/agent-harness]] for the engineering details.

---

## Key Takeaways

- **The Big Model / Big Harness debate is not resolved.** Evidence exists for both positions, and motivated reasoning from each side is real.
- **The Bitter Lesson predicts harness complexity will shrink over time** as models absorb capabilities that scaffolding previously provided. This already happened with reasoning models replacing agentic scaffolding for reasoning tasks.
- **Market evidence favors harness value**: Cursor ($50B), the emergence of a dedicated Harness Engineering conference track, and the Pi results all suggest the harness is not a rounding error.
- **Claude Code's explicitly minimal design** is itself a harness philosophy — not absence of opinion, but a deliberate choice to keep complexity in the model.
- **Harness choice matters differently across models**: SWE-Atlas data shows harness improvements are model-specific, not universal. A harness that helps Claude may hurt GPT-5.2.
- **The core loop is irreducible**: `while (model returns tool calls): execute → capture → append → call` is the minimal harness. Everything above this is optional leverage.
