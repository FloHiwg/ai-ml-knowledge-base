# Chapter 18: Guardrails/Safety Patterns

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Design Patterns for Securing LLM Agents against Prompt Injections]] · [[summaries/Prompt injection What's the worst that can happen]] · [[summaries/Findings from a Pilot Anthropic - OpenAI Alignment Evaluation Exercise]]

---

## Core Idea

Guardrails are the protective controls that keep agents safe, policy-compliant, and predictable. The chapter treats them as a layered defense system applied before, during, and after model execution: validate inputs, constrain behavior, restrict tool use, filter outputs, and escalate to humans when necessary.

---

## Safety as a Layered System

The chapter emphasizes that no single mechanism is enough. Guardrails can appear as:

- input validation and sanitization
- behavioral constraints in prompts and agent configuration
- tool restrictions and callback checks
- output filtering and moderation
- logging and observability
- human review for critical or ambiguous cases

This is one of the chapter’s strongest ideas: safety is a pipeline property, not just a model property.

## What the Chapter Protects Against

The examples cover offensive or unsafe content, biased outputs, prompt-injection attempts, brand-safety issues, policy bypasses, legal overreach, and unsafe recommendations in high-stakes domains like education and scientific assistance.

The book is clear that guardrails are not only for public chatbots. They matter anywhere an agent can affect users, business systems, or reputation.

## Practical Implementations

The CrewAI example builds a dedicated policy-enforcer agent and validates its structured JSON decision with a Pydantic schema. That pairing is important because it combines semantic screening with deterministic validation: the model makes a policy judgment, but the system still enforces machine-checkable output structure.

The Vertex AI example pushes the pattern closer to execution control by using callbacks to validate tool arguments before a tool can run. That shows guardrails operating not just around language, but directly around actions.

## Monitoring and Observability

Another recurring theme is observability. Logs of tool use, inputs, outputs, and agent decisions are treated as part of the safety system because they make auditing and incident investigation possible. Safety is therefore not just prevention, but traceability.

This is especially relevant for multi-step agents where the risk often lies in the trajectory, not just the final answer.

## Design Tradeoffs

The chapter warns against both under- and over-constraining the system. Too few guardrails create obvious risk. Too many can make the agent brittle, expensive, or unhelpful. The design goal is targeted controls that reduce harm without destroying usefulness.

---

## Key Takeaways

- Guardrails are a layered safety architecture, not a single moderation filter.
- They can operate on inputs, prompts, tools, outputs, and human escalation paths.
- Structured validation and callback-based tool checks are practical ways to enforce policy.
- Observability is part of safety because it enables auditing and diagnosis.
- The main engineering challenge is balancing safety, usability, and cost.
