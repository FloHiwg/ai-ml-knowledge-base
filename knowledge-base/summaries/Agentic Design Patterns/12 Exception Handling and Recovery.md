# Chapter 12: Exception Handling and Recovery

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]] · [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Exception handling and recovery make agents resilient in imperfect environments. The chapter treats failure as normal rather than exceptional: tools break, APIs time out, inputs are malformed, devices go offline, and plans collide with reality. A robust agent needs to detect those failures, contain them, and recover gracefully whenever possible.

---

## Three Layers of Resilience

The chapter organizes the pattern into three stages:

- error detection
- error handling
- recovery

Detection includes malformed outputs, explicit API failures, long latency, or nonsensical model responses. Handling includes logging, retries, fallbacks, notifications, and graceful degradation. Recovery includes rollback, diagnosis, self-correction, replanning, or escalation to a human.

That structure is useful because it keeps "recovery" from collapsing into a single retry loop. Different failures need different responses.

## Real-World Importance

The practical examples include customer-service chatbots, trading bots, smart-home systems, document processors, web scrapers, and robotics. In all of them, the key requirement is continuity. The system should not catastrophically fail just because one tool call or one item in a batch fails.

This is one of the clearest chapters in the book about operational maturity: an agent is not production-ready just because it produces good outputs under ideal conditions.

## Reflection as a Recovery Aid

The chapter briefly connects recovery to reflection. If an attempt fails, the agent may inspect the failure, revise the prompt or plan, and try again with a better approach. That is a stronger pattern than blind retry because it introduces diagnosis before re-execution.

So reflection can be seen as one recovery strategy among several.

## Implementation Notes

The ADK example uses a sequential arrangement with a primary handler, a fallback handler, and a response agent. The primary tries to fetch precise information; if it fails, state is updated so the fallback can pursue a broader, less precise alternative; the final agent then communicates the result clearly to the user.

That example captures a larger design lesson: resilient systems often recover by changing the level of ambition rather than insisting on full success or total failure.

## Design Tradeoffs

The chapter suggests that recovery behavior should be explicit and policy-driven. Too little recovery makes the system brittle. Too much retrying makes it noisy, expensive, or even dangerous. Good exception handling therefore needs boundaries: when to retry, when to degrade, and when to escalate.

---

## Key Takeaways

- Failures are normal in real-world agent systems, so recovery must be designed in from the start.
- The chapter breaks resilience into detection, handling, and recovery.
- Typical responses include logging, retries, fallbacks, graceful degradation, and escalation.
- Reflection can improve recovery by helping the agent diagnose before retrying.
- The goal is not perfect success, but dependable behavior under imperfect conditions.
