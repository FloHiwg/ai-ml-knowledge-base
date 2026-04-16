# Chapter 3: Parallelization

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]]

---

## Core Idea

Parallelization improves agent efficiency by running independent work at the same time instead of in strict sequence. The chapter presents it as a performance pattern: if multiple lookups, tool calls, or sub-agents do not depend on one another, they should execute concurrently and only rejoin when synthesis is required.

---

## Sequential vs Parallel Work

The motivating example compares two research workflows. In a sequential design, the agent gathers and summarizes one source before moving to the next. In a parallel design, it searches multiple sources simultaneously, then summarizes them simultaneously, and only performs the final synthesis step after the parallel branches complete.

The key rule is dependency. Parallelization is appropriate only when tasks are independent enough that one branch does not need another branch's result.

## Where the Pattern Helps

The chapter highlights several common uses:

- gathering information from multiple sources
- calling several APIs at once
- running multiple analyses over the same dataset
- generating several content components in parallel
- validating inputs with multiple independent checks
- processing multiple modalities at the same time
- producing alternative outputs for comparison or selection

In each case, the benefit is reduced wall-clock time rather than a fundamentally different answer.

## Framework View

LangChain and LangGraph are presented as natural fits because they already model workflows as composable runnables or graph branches. Google ADK is positioned as especially strong for multi-agent concurrency, where separate agents can work in parallel under a shared orchestration layer.

The implementation lesson is architectural: concurrency should be an explicit property of the workflow graph, not an accidental side effect of tool calls.

## Practical Caveats

The chapter is clear that not every task should be parallelized. Parallel branches still need a convergence point, and the final answer often remains sequential because the system must gather, compare, or synthesize the results.

There is also an operational cost. Parallel execution can increase resource usage, API spend, and coordination complexity. So the gain is usually speed and responsiveness, not simplicity.

## Implementation Notes

The hands-on LangChain example builds several independent chains for summarization, question generation, and key-term extraction, then runs them in parallel before combining the outputs. That example captures the broader pattern well: a parallel stage produces multiple views of the same input, then a later stage integrates them.

The chapter’s ADK framing extends the same idea to multi-agent systems, where concurrency is handled more explicitly by the orchestration layer.

---

## Key Takeaways

- Parallelization is the right pattern when sub-tasks are independent.
- Its main benefit is lower latency and better responsiveness.
- It is especially valuable for API-heavy and research-heavy agent workflows.
- Parallel branches usually still need a later synthesis or decision step.
- The main design challenge is identifying true independence without introducing race conditions, extra cost, or unnecessary complexity.
