# Chapter 16: Resource-Aware Optimization

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]] · [[summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]]

---

## Core Idea

Resource-aware optimization teaches agents to reason not only about correctness, but also about budgets. The chapter focuses on how agents trade off accuracy, latency, compute, and cost while deciding which model, tool, or workflow path to use. It is essentially operational optimization layered on top of normal planning.

---

## What Counts as a Resource

The chapter treats resources broadly:

- computational power
- time and latency
- financial budget
- bandwidth or data movement
- available agent capacity in multi-agent systems

This matters because many agent papers optimize only for answer quality, while real systems also need to optimize for response time and spend.

## Dynamic Model Choice

The central pattern in the chapter is dynamic model selection. Simple or low-risk tasks can be routed to a fast, cheap model; high-value or high-complexity tasks can be escalated to a more capable, slower, and more expensive model. That same logic can apply to tools, data retrieval strategies, or the depth of reasoning the system is willing to pay for.

The travel-planner example captures the idea well: deep itinerary planning goes to a stronger model, while routine lookups like prices and availability can be delegated to faster, cheaper components.

## Fallbacks and Graceful Degradation

The chapter also treats fallback as a resource pattern. If a preferred model is unavailable, overloaded, or throttled, the system should degrade gracefully to a backup model rather than fail completely. This ties reliability directly to resource management, not just to exception handling.

That makes the pattern useful for both cost optimization and continuity of service.

## Router and Critic Roles

One interesting design thread in the chapter is the use of a router agent and a critic agent. The router decides which model or path should handle the request. The critic reviews whether the decision and output were appropriate, which creates a feedback loop that can later improve routing quality and reduce wasted spend.

So the chapter is not just about fixed heuristics. It also points toward adaptive resource policy.

## Practical Framing

The examples include model routing, budget-sensitive inference, edge-device constraints, bandwidth-aware retrieval, and adaptive task allocation in multi-agent systems. The broader message is that efficient agents must be able to make "good enough" decisions when ideal solutions are too slow or too expensive.

---

## Key Takeaways

- Resource-aware optimization balances quality against latency, compute, and cost.
- A key pattern is routing simple work to cheap models and hard work to stronger models.
- Fallbacks are part of optimization because availability is also a resource constraint.
- Router and critic components can improve resource allocation over time.
- The goal is not maximum intelligence at all times, but the best feasible behavior under budget and timing limits.
