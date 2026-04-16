# Chapter 4: Reflection

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Experimenting with LLMs to Research, Reflect, and Plan]] · [[summaries/Demystifying Reasoning Models - by Cameron R. Wolfe, Ph.D.]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Reflection introduces a feedback loop into agent behavior. Instead of producing one answer and stopping, the agent critiques its own output, identifies weaknesses, and generates a refined version. The chapter treats this as a core quality-improvement pattern for tasks where correctness, completeness, style, or reliability matter more than speed alone.

---

## The Reflection Loop

The chapter breaks the pattern into a repeatable cycle:

1. generate an initial output
2. evaluate or critique that output
3. revise based on the critique
4. iterate until a stopping condition is met

This transforms the workflow from a one-pass chain into a self-correcting system. The main gain is not new external knowledge, but better use of the model's own evaluative capacity.

## Producer and Critic Roles

One of the chapter's strongest ideas is the separation between a producer and a critic. A producer generates the draft or plan; a critic reviews it under a different instruction set and against explicit criteria. The book argues this often works better than single-agent self-review because the critic is optimized for finding flaws rather than defending the first answer.

That design shows up in both the conceptual explanation and the code examples. It is essentially a structured version of revision, not just a vague "try again."

## When Reflection Helps

The practical use cases include:

- creative writing and editing
- code generation and debugging
- long-form summarization
- multi-step planning
- conversational repair
- complex reasoning problems where intermediate steps may be wrong

In each case, the point is that first-pass answers are often useful but not final. Reflection helps the system close that gap.

## Connections to Other Patterns

The chapter explicitly connects reflection to [[summaries/Agentic Design Patterns/08 Memory Management]] and [[summaries/Agentic Design Patterns/11 Goal Setting and Monitoring]]. Memory helps the system remember earlier critiques and avoid repeating them. Goal setting gives reflection a target: the system can ask not just "is this good?" but "does this advance the stated objective?"

That makes reflection more powerful when it is cumulative rather than isolated.

## Implementation Notes

The LangChain example uses an iterative loop to improve a Python function, with critique framed as if it came from a senior engineer. The ADK example uses a clearer producer-reviewer split. Both implementations reinforce the same lesson: reflection is most effective when the critique is explicit, structured, and grounded in concrete criteria.

The chapter also suggests that real iterative reflection usually needs stronger state management than a single chain call can provide.

## Limits and Tradeoffs

Reflection improves quality, but it increases latency and token usage. It can also become circular if the system keeps refining without meaningful gains. So the pattern works best when there is a clear success test, a maximum iteration count, or some external check that tells the agent when to stop.

---

## Key Takeaways

- Reflection adds self-correction to agent workflows.
- The most effective version often separates producer and critic roles.
- It is especially valuable for code, planning, summarization, and other quality-sensitive tasks.
- Memory and explicit goals make reflection more useful over time.
- The main tradeoff is cost and latency in exchange for better outputs.
