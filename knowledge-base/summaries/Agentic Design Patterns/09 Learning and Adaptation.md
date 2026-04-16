# Chapter 9: Learning and Adaptation

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Continual Learning with RL for LLMs]] · [[summaries/Direct Preference Optimization (DPO)]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Learning and adaptation let an agent improve from experience instead of staying fixed after deployment. The chapter surveys several learning paradigms, then connects them back to agent behavior: agents can update strategies, refine decisions, and respond better to novel conditions when they retain feedback from the environment.

---

## The Learning Spectrum

The chapter sketches a broad map of learning approaches:

- reinforcement learning for action-and-reward settings
- supervised learning for labeled decisions
- unsupervised learning for pattern discovery
- few-shot and zero-shot adaptation with LLMs
- online learning for continuous updates
- memory-based learning for recall from prior episodes

The unifying message is that adaptation is not one method. It is a family of mechanisms that let agents alter behavior in response to new evidence.

## PPO and DPO

The chapter spends useful time on two alignment-relevant methods. PPO is described as a stable reinforcement-learning approach that constrains policy updates through clipping so the model does not drift too far from a known working strategy. DPO is presented as a simpler alternative for preference alignment: instead of training a separate reward model and then optimizing against it, the model is updated directly from preferred-versus-dispreferred examples.

The contrast matters because the chapter is not only about autonomous learning in the wild. It is also about how modern language-model agents become aligned and improved through different optimization pipelines.

## Adaptation in Real Systems

The practical examples include personalized assistants, trading bots, adaptive applications, autonomous vehicles, fraud detection, recommender systems, and game agents. Each example points to the same pattern: the agent improves when it can absorb feedback loops from use, environment, or performance outcomes.

The chapter also links adaptation to [[summaries/Agentic Design Patterns/14 Knowledge Retrieval (RAG)]], noting that dynamic knowledge stores can function as a practical learning substrate even when the base model weights do not change.

## SICA Case Study

The most distinctive section is the case study on the Self-Improving Coding Agent (SICA). Rather than only learning parameters, SICA improves by modifying its own code, selecting strong prior versions from an archive, testing changes, and iterating. The chapter uses SICA to illustrate a more ambitious idea of adaptation: agents can evolve their tools, editors, navigation strategies, and workflow structure over time.

That makes this chapter one of the book’s more concrete bridges from abstract learning theory to agent engineering.

## Design Lessons

The chapter implies that adaptation requires three ingredients:

- feedback signals
- memory or storage of past outcomes
- a mechanism for changing future behavior

Without all three, the system may look interactive but is not actually learning.

---

## Key Takeaways

- Learning and adaptation let agents change behavior from experience rather than remain static.
- The chapter surveys RL, supervised, unsupervised, in-context, online, and memory-based learning.
- PPO and DPO are presented as important but different alignment strategies.
- The SICA example shows adaptation at the system-design level, not just at the prompt level.
- In practice, adaptive agents need feedback, persistence, and a concrete update mechanism.
