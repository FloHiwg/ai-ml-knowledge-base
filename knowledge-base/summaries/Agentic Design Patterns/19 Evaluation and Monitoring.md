# Chapter 19: Evaluation and Monitoring

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Applying Statistics to LLM Evaluations]] · [[summaries/Using LLMs for Evaluation - by Cameron R. Wolfe, Ph.D.]] · [[summaries/The Anatomy of an LLM Benchmark]]

---

## Core Idea

Evaluation and monitoring are the patterns that make agent performance measurable in practice. The chapter distinguishes them from goal setting: instead of only tracking whether one agent-specific objective is met, evaluation and monitoring define broader performance metrics, detect drift, expose anomalies, and create feedback loops for production oversight.

---

## What Gets Measured

The chapter names a practical set of metrics and checks:

- output quality and response accuracy
- latency
- token usage and cost
- drift over time
- anomalous behavior
- compliance and auditability
- A/B comparisons between variants

This gives the chapter a strong operational focus. It is less about reasoning patterns and more about how to know whether an agent system is actually working at scale.

## Beyond Exact Match

One of the chapter’s useful points is that naive exact-match metrics are often insufficient. Two responses can express the same meaning with different wording, so evaluation needs richer methods: string-similarity metrics, semantic similarity, rubric-based evaluation, or LLM-as-a-judge for subjective dimensions like helpfulness.

The chapter does not claim any one metric is enough. It argues for layered evaluation matched to the behavior being tested.

## Operational Monitoring

Latency and token monitoring are treated as first-class concerns, not just cost details. In production systems, these should be logged to persistent observability infrastructure rather than printed ad hoc. The chapter explicitly mentions structured logs, time-series systems, data warehouses, and observability platforms as plausible destinations for that telemetry.

This reinforces the book’s broader theme that agents are systems, not prompts.

## The "AI Contract" Idea

One of the more distinctive ideas in this chapter is the shift from simple agent tracking toward a broader governance object: an AI "Contract" that codifies objectives, rules, and controls for delegated work. That framing pushes evaluation beyond model metrics toward accountable operational agreements inside enterprise settings.

It is a more governance-heavy lens than most other chapters adopt.

## Practical Lesson

The big practical message is that agent evaluation must include both outcome quality and process quality. You need to measure not only whether the final answer looked good, but whether the system stayed efficient, compliant, and stable while producing it.

---

## Key Takeaways

- Evaluation and monitoring make agent performance observable and governable.
- Useful metrics include quality, latency, token usage, drift, anomalies, and compliance.
- Simple exact-match scoring is often too weak for real agent evaluation.
- LLM-as-a-judge can help with nuanced qualities like helpfulness, but it is only one tool.
- Production agent systems need persistent telemetry and audit-friendly monitoring, not just offline benchmarks.
