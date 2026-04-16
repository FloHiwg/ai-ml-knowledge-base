# Guardrails

**Related:** [[applications/prompt-injection]] · [[applications/agentic-patterns]] · [[inference/prompting-and-reasoning]]
**Sources:** [[summaries/Patterns for Building LLM-based Systems & Products]] · [[summaries/Agentic Design Patterns/18 Guardrails-Safety Patterns]] · [[summaries/Agentic Design Patterns/13 Human-in-the-Loop]]

---

## What Are Guardrails?

Guardrails are validation and constraint mechanisms that intercept LLM inputs or outputs to enforce correctness, safety, and format compliance. Unlike prompting, which *requests* behavior, guardrails *enforce* it — either by constraining the generation process itself or by filtering before/after generation.

---

## Five Layers of Guardrails

| Layer | What it checks | When applied |
|---|---|---|
| **Structural** | Format compliance (JSON schema, XML, regex) | Output — validate generated structure |
| **Syntactic** | Grammar, sentence well-formedness | Output — catch malformed text |
| **Semantic / Factuality** | Faithfulness to source material, NLI consistency | Output — detect hallucinations and contradictions |
| **Safety** | Toxic content, PII leakage, off-topic responses | Both input and output |
| **Input** | Prompt injection detection, input validation, length | Input — screen before processing |

Defense-in-depth: multiple layers provide redundancy. A prompt injection that bypasses the input filter may still be caught by semantic validation if it attempts an unexpected action.

For agentic systems, it helps to think in execution order:

| Stage | Typical guardrail |
|---|---|
| **Before model call** | Input sanitization, moderation, prompt-injection screening |
| **Inside agent policy** | System prompt constraints, role scoping, escalation rules |
| **Before tool call** | Parameter validation, auth checks, allow/deny rules |
| **After tool call / before user output** | Output validation, redaction, moderation, schema checks |
| **Critical decision boundary** | Human review or approval |

---

## Structural Guardrails: Guidance and Token Healing

### Guidance (Microsoft)

Constrains generation at the **token level** by specifying a grammar or schema that outputs must conform to. At each generation step, only tokens consistent with the currently valid grammar state are allowed. Format violations become structurally impossible — the model cannot produce invalid JSON because non-JSON tokens are excluded at generation time.

Useful for: structured outputs (function calls, tool use, JSON), multi-step templates where each field must follow a specific pattern.

### Token Healing

Addresses a BPE tokenization artifact: the boundary token at the end of a prompt may be suboptimal because it was tokenized without knowing the continuation. Token healing backtracks one token and regenerates from the corrected boundary, ensuring the first generated token represents the full character sequence rather than a fragmented one.

Particularly important for prompts that end mid-word or mid-format-string.

---

## Semantic / Factuality Guardrails

### NLI-Based Validation

Use a Natural Language Inference (NLI) model to check whether the generated response is entailed by the source material. Responses that contradict or are unsupported by the retrieved context can be flagged or regenerated.

### SelfCheckGPT

Detects hallucinations without a reference document by exploiting sampling inconsistency:

1. Sample the same prompt multiple times (e.g., 3–5 times)
2. Compare facts across samples
3. Facts consistent across all samples → likely grounded
4. Facts that vary across samples → likely hallucinated

No ground truth or retrieved context required. Works on any LLM that supports sampling. Effective on long-form generation where individual fact verification is expensive.

---

## Guardrails Frameworks

### Guardrails (guardrails-ai)

Python package for defining output validators as "guards." Provides:
- Schema validation (Pydantic integration)
- Custom validators with retry logic — if validation fails, the guard can re-prompt the model
- Structured output parsers with error correction
- Built-in validators for common patterns (regex, type checks, length)

### NeMo-Guardrails (NVIDIA)

Defines programmable rails using Colang, a domain-specific language for conversation flow and validation:

| Rail type | Purpose |
|---|---|
| **Input rails** | Screen and reject/transform incoming messages |
| **Dialog rails** | Control conversation flow; enforce topics and personas |
| **Output rails** | Validate responses before returning to user |

LLM-based validation: NeMo-Guardrails uses a secondary LLM call to evaluate whether a response violates a defined policy. More flexible than rule-based approaches; can handle nuanced policy violations. Integrates with LangChain and other agent frameworks.

### Pydantic-Validated Guardrail Agents

For high-signal policy checks, a useful pattern is to ask a fast model to return a structured compliance decision and then validate that decision with a deterministic schema checker such as Pydantic. The model handles semantic judgment; the schema enforces machine-readable structure and prevents malformed control outputs from silently passing through.

---

## Safety Guardrails

Detecting and filtering harmful outputs:

| Tool | What it detects |
|---|---|
| **Perspective API** (Google) | Toxicity, severe toxicity, identity attacks, insults, threats |
| **LLM classifiers** | Policy-specific violations; can be fine-tuned on organization-specific examples |
| **Regex blocklists** | PII patterns (SSN, credit card, email), specific terms |
| **Off-topic classifiers** | Detect responses that leave the intended use case |

For agentic systems, input guardrails that detect prompt injection are especially critical — see [[applications/prompt-injection]].

### Tool-Time Guardrails

Tool use creates a second attack surface. Even if the prompt is safe, the agent may still call a tool with unsafe parameters or on behalf of the wrong user. A strong agent harness therefore validates tool arguments at execution time:

- confirm the session user matches the requested user identifier
- block calls outside the allowed resource scope
- enforce allowlists or regex checks on dangerous parameters
- reject or escalate mismatched or ambiguous tool requests

This is the point where guardrails stop being "content moderation" and become action governance.

---

## Defensive UX

Guardrails at the model level must be paired with defensive interface design. Three established frameworks:

**Microsoft HAI Guidelines (18 guidelines):** Help users calibrate trust, make uncertainty visible, allow corrections, explain model behavior, provide graceful fallbacks.

**Google PAIR Guidebook (23 patterns):** Show model reasoning, explain data sources, handle disagreement constructively, communicate confidence levels.

**Apple HIG for Machine Learning:** ML features should feel native; never surprise users; always provide opt-out; make it clear when ML is involved.

Common principle across all three: **surface uncertainty, give users control, explain model behavior, plan for failures.**

---

## Design Considerations

- **Guardrails add latency** — NLI models, secondary LLM calls, and complex validators run synchronously in the critical path. Profile carefully.
- **Guardrails can be bypassed** — sophisticated adversaries will probe guardrail thresholds. Defense-in-depth across layers is more robust than a single strong guardrail.
- **Structural guardrails are the most reliable** — token-level constraints (Guidance) make format violations impossible rather than merely unlikely.
- **Combine with human-in-the-loop** — for high-stakes actions, no automated guardrail replaces explicit user confirmation.
- **Observability is part of the safety system** — log tool calls, inputs, outputs, and escalation events so violations can be audited and incidents investigated.
