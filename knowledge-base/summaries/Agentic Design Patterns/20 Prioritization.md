# Chapter 20: Prioritization

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]] · [[summaries/AI Agents from First Principles]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]]

---

## Core Idea

Prioritization is the pattern that decides what an agent should do next when many actions are possible but resources, time, or attention are limited. The chapter frames it as the decision layer that ranks tasks by urgency, importance, dependencies, and available resources so the agent can focus on the most consequential work first.

---

## What Prioritization Evaluates

The chapter identifies several common criteria:

- urgency
- importance
- dependencies
- resource availability
- cost-benefit tradeoffs
- user preferences

This makes prioritization broader than deadline handling. It is a general scoring and ranking mechanism for action selection.

## Levels of Prioritization

The pattern can operate at multiple scales:

- high-level goal prioritization
- sub-task ordering inside a plan
- immediate action selection from a set of options

That is a useful distinction because agents often need prioritization at all three levels. A system may first choose which objective matters most, then which step within that objective comes next, then which concrete action is best right now.

## Dynamic Reprioritization

One of the important themes in the chapter is that priorities should change when the environment changes. New deadlines, incidents, dependencies, or resource shortages can all force a reorder. So prioritization is not just a setup step; it is part of the ongoing control loop.

That makes this chapter closely related to planning, routing, and monitoring.

## Practical Uses

The use cases span customer support, cloud scheduling, autonomous driving, financial trading, project management, cybersecurity, and personal-assistant behavior. These examples share a common problem: the agent cannot satisfy every demand equally, so it must explicitly decide what deserves attention first.

The chapter argues that this ability is what makes agents effective in multi-objective environments rather than merely reactive.

## Implementation Notes

The hands-on example uses a project-manager agent with tools for creating tasks, assigning priorities, and assigning owners. The main design point is that prioritization becomes much more usable when task state is externalized and editable rather than hidden inside a single prompt.

That supports a broader lesson: prioritization works best when it is backed by explicit state and stable ranking criteria.

---

## Key Takeaways

- Prioritization is the action-selection pattern for resource-constrained environments.
- It ranks tasks using criteria like urgency, importance, dependencies, and available capacity.
- The pattern can operate at the level of goals, sub-tasks, or immediate actions.
- Effective agents reprioritize dynamically as conditions change.
- The main design challenge is defining scoring criteria that reflect real business or user value rather than shallow proxies.
