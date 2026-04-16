# Chapter 6: Planning

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Planning is the pattern that lets an agent discover the "how" of a task rather than only executing a known workflow. The chapter treats planning as goal-directed decomposition: given an initial state, a target state, and some constraints, the agent constructs an action sequence that can move the system from one to the other.

---

## Planning as Discovery

The chapter’s core distinction is between a dynamic planning agent and a fixed task-execution agent. If the steps are already known, a predetermined workflow is safer and more predictable. Planning is only worth the extra complexity when the path itself must be inferred at runtime.

The offsite-planning example makes this concrete. The agent is given an outcome and constraints, not a step list. It must create the sequence, detect blockers, and revise its plan when reality changes.

## Adaptability and Replanning

One of the strongest themes in the chapter is that plans should not be treated as rigid scripts. A useful planner monitors new constraints and replans when assumptions break. Venue unavailable, vendor booked out, missing data, conflicting requirements: these are not edge cases but normal operating conditions for a planning agent.

That makes planning closely related to monitoring, routing, and exception handling. The plan is an evolving control structure, not a static checklist.

## Common Use Cases

The practical applications include:

- business-process orchestration
- autonomous navigation and robotics
- structured research and report generation
- customer-support diagnosis and escalation
- long, interdependent workflows where order matters

The common thread is that the problem cannot be solved with one action or one model response. It requires a coherent series of dependent steps.

## Implementation Notes

The code example uses CrewAI to first generate a plan and then use that plan to write a short summary. The example itself is simple, but the design pattern is broader: the system should externalize the plan as an explicit intermediate artifact rather than hiding it inside one giant prompt.

The chapter then connects that idea to Google Deep Research, which is presented as a richer planning system: it decomposes the research task, proposes a plan, lets the user review it, then executes a long-running search-and-synthesis workflow asynchronously.

## Tradeoffs and Scope

The book is careful not to over-apply planning. Planning increases autonomy, but it also increases uncertainty, cost, and the chance that the system explores bad paths. When the workflow is routine and well understood, a constrained chain is usually the better engineering choice.

So planning is best treated as a capability reserved for tasks where discovery and adaptation are part of the job.

---

## Key Takeaways

- Planning is what lets an agent infer a path to a goal rather than follow a fixed script.
- It matters most when the "how" is unknown at the start.
- Good planning systems must support revision as conditions change.
- The chapter treats plans as explicit artifacts that can guide later execution.
- The main tradeoff is flexibility versus predictability; not every workflow should be handled by a planner.
