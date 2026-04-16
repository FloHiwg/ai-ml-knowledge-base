# Chapter 11: Goal Setting and Monitoring

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Goal setting and monitoring give agents direction and a way to judge progress. The chapter’s central point is simple: agents need explicit objectives and feedback loops, otherwise they can execute actions without any structured sense of whether those actions are actually moving toward success.

---

## Goals as Operational Targets

The chapter describes goals as target states rather than vague aspirations. A useful goal tells the agent what counts as success, what constraints matter, and what signals indicate whether the system is on track.

This turns agent behavior from reactive task completion into objective-driven work. The system is not just doing steps; it is measuring whether those steps are accomplishing the intended result.

## Monitoring as Ongoing Evaluation

Monitoring is the mechanism that keeps goals live during execution. The agent watches relevant signals, checks whether the current state still aligns with the target, and decides whether to continue, revise, or escalate.

The examples include customer-support resolution, student learning progress, project milestones, trading risk control, autonomous driving, and content moderation. In each case, the pattern combines an explicit aim with continuous progress checks.

## Relationship to Planning and Reflection

Although the chapter repeats some planning language, the underlying emphasis is different. Planning decomposes the route; goal setting and monitoring define what the route is trying to achieve and whether it is still working. Reflection then becomes a corrective loop that can use those monitored signals to revise outputs or strategy.

This chapter is therefore best read as the control layer above planning rather than a duplicate of planning itself.

## Implementation Notes

The hands-on code example builds an iterative coding agent that keeps generating and reviewing Python code until its stated goals are met or a maximum number of iterations is reached. The important design move is not the code generation itself but the success predicate: the system explicitly checks whether goals have been satisfied instead of assuming the first answer is good enough.

That makes the pattern especially useful for agents that must stop, continue, or revise based on measurable criteria.

## Practical Tradeoffs

The chapter suggests that the quality of this pattern depends on the quality of the goals. Vague goals produce vague monitoring. If the success test is weak, the agent can optimize for the wrong proxy or prematurely declare victory.

So in practice, much of the engineering work is deciding what the agent should measure and how strict those measures need to be.

---

## Key Takeaways

- Goal setting gives the agent a clear target state.
- Monitoring lets the agent track progress and detect failure or drift during execution.
- The pattern matters in long-running, high-stakes, or multi-step tasks.
- It complements planning by defining success, not just sequence.
- The hardest part is specifying goals and monitors that are concrete enough to guide behavior reliably.
