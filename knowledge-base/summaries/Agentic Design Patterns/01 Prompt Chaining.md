# Chapter 1: Prompt Chaining

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Patterns for Building LLM-based Systems & Products]] · [[summaries/AI Agents from First Principles]] · [[summaries/Teaching Language Models to use Tools]]

---

## Core Idea

Prompt chaining treats a complex task as a pipeline of smaller steps, where each step's output becomes the next step's input. The chapter presents this as a foundational agent pattern: it improves reliability, makes intermediate reasoning inspectable, and creates clean handoff points for validation, structured output, and tool use.

---

## Why Single Prompts Fail

The chapter argues that large, monolithic prompts often overload the model. When one prompt asks for multiple transformations at once, the model is more likely to skip instructions, lose context, propagate early mistakes, or hallucinate details.

The motivating example is a market-research workflow that asks for summarization, trend extraction, supporting evidence, and final email drafting in one shot. The book's claim is that each of those operations should usually be isolated so the model only does one cognitively narrow job at a time.

## How Prompt Chaining Improves Reliability

The core mechanism is sequential decomposition:

1. Summarize the source material.
2. Extract trends and supporting evidence from the summary.
3. Draft the final communication from that structured result.

This makes the system easier to control and debug because each stage can be inspected independently. It also allows different prompt roles per stage, such as analyst first and writer later, rather than forcing one generic persona to do everything.

## Structured Outputs Matter

The chapter emphasizes that prompt chains are only as strong as the data passed between steps. If an intermediate answer is vague, the next step inherits that ambiguity. Its main recommendation is to prefer structured outputs like JSON or XML for handoffs between stages.

That pattern turns free-form text into a machine-readable contract. In practice, it makes downstream prompting, parsing, and validation much more predictable.

## Practical Use Cases

The chapter frames prompt chaining as a general workflow pattern for:

- multi-stage information processing
- complex question answering
- extraction and normalization from unstructured documents
- content generation pipelines
- conversational flows that preserve state across turns
- code generation and refinement
- multimodal reasoning where text, labels, tables, or tool outputs need to be combined

A recurring theme is that real systems often mix parallel work and chained work: independent retrieval or extraction can happen concurrently, then the dependent synthesis and refinement steps run in sequence.

## Implementation Notes

The hands-on example uses LangChain and LCEL to build a two-step chain:

1. Extract technical specifications from raw text.
2. Transform the extracted specs into JSON.

The implementation is simple, but the design lesson is broader: chains should be composed so each step has one clear purpose and the boundary between steps is explicit.

## Context Engineering vs Prompt Engineering

The chapter also broadens the discussion from prompt wording to context engineering. Its argument is that strong outputs depend less on clever phrasing alone and more on the full information package delivered to the model: system instructions, retrieved documents, tool outputs, user history, and current state.

That makes prompt chaining not just a prompt tactic, but part of a larger runtime architecture for building context-aware agents.

---

## Key Takeaways

- Prompt chaining is the default pattern for tasks that are too complex for one prompt.
- Intermediate outputs should be explicit and preferably structured.
- Chaining improves observability because each step can be tested and validated independently.
- The pattern works especially well when combined with tools, retrieval, and deterministic checks between model calls.
- The chapter positions prompt chaining as a foundational building block for more advanced agent workflows.
