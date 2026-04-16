# Agent Evaluation and Monitoring

**Related:** [[evaluation/llm-as-a-judge]] · [[evaluation/benchmarks]] · [[evaluation/statistical-evaluation]] · [[applications/agentic-patterns]] · [[applications/rag]]
**Sources:** [[summaries/Agentic Design Patterns/19 Evaluation and Monitoring]]

---

## Core Idea

Agent evaluation is broader than model benchmarking. A production agent must be assessed not only for answer quality, but also for latency, cost, behavioral stability, compliance, and failure patterns over time. Monitoring is the continuous operational side of that evaluation: collecting telemetry, detecting drift, and surfacing anomalies while the system is live.

---

## What to Measure

### Output Quality

- response accuracy and factual correctness
- relevance to the original user goal
- faithfulness to retrieved context in RAG systems
- helpfulness, completeness, and clarity

For subjective dimensions like helpfulness, use rubric-based [[evaluation/llm-as-a-judge]] or human review rather than exact-match scoring.

### Operational Metrics

- end-to-end latency
- tool-call latency by tool or subsystem
- token usage and cost
- failure and retry rates
- escalation frequency to humans or fallback systems

These metrics matter because a technically correct agent can still be unusable if it is too slow, too expensive, or too fragile.

### Behavioral Stability

- concept drift or environment drift
- anomalous tool-use patterns
- unexpected loops or repetition
- policy and compliance violations

This is where agent monitoring differs from classic offline model evaluation: the concern is ongoing behavior in a changing environment.

---

## Evaluation Methods

### Exact and Semantic Checks

Exact match is only appropriate for tightly specified outputs. Open-ended agent tasks usually need semantic comparison, rubric scoring, or claim-level verification.

### LLM-as-a-Judge

LLM judges are useful for qualities such as helpfulness, tone, or overall task completion, but they should be treated as one signal rather than the whole eval stack. They are strongest when paired with clear rubrics, position-switching, and human spot checks.

### Task-Specific Metrics

RAG systems should track context relevance, answer faithfulness, and factual correctness. Tool-using agents may need domain-specific checks such as SQL validity, API success rate, or safety policy conformance.

### A/B Testing

When changing prompts, models, routing logic, or harness behavior, run side-by-side evaluations. Agent systems often regress in latency or cost before they regress in answer quality, so compare both output and operational metrics.

---

## Monitoring and Telemetry

Operational monitoring should store telemetry in durable systems rather than ad hoc logs. Common destinations include:

- structured log files
- time-series systems such as Prometheus or InfluxDB
- observability platforms
- warehouses such as BigQuery, Snowflake, or PostgreSQL

The key is to preserve enough detail to reconstruct agent trajectories: prompts, tool calls, outputs, retries, and intermediate failures.

---

## Contracts and Governance

In enterprise settings, an agent often operates under an implicit or explicit **AI contract**: a specification of goals, constraints, allowed actions, evaluation criteria, and escalation rules. Monitoring is how the system proves it is staying inside that contract over time.

This is especially important for:

- regulated workflows
- delegated business operations
- human-in-the-loop approval chains
- agents with broad tool access

---

## Practical Failure Modes

Common reasons agent evaluation breaks down:

1. measuring only final answer quality and ignoring latency or cost
2. treating a single benchmark as representative of production behavior
3. failing to log enough detail to diagnose regressions
4. relying on one judge model without calibration or human review
5. missing drift because evaluation happens only before launch

A mature agent stack needs both offline evaluation and continuous monitoring after deployment.
