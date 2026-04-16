# Chapter 5: Tool Use (Function Calling)

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Teaching Language Models to use Tools]] · [[summaries/AI Agents from First Principles]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]]

---

## Core Idea

Tool use turns a language model from a text generator into an operational agent. The chapter explains function calling as the mechanism that lets an LLM decide when it needs an external capability, emit a structured call, receive the result, and then continue reasoning with that result in context.

---

## The Basic Tool Loop

The chapter presents tool use as a six-stage process:

1. define the tool and its arguments
2. expose those definitions to the model
3. let the model decide whether a tool is needed
4. parse the structured tool call
5. execute the real function or API
6. feed the result back to the model for the next step or final answer

This pattern matters because it breaks the closed world of pretraining. Instead of relying only on static model knowledge, the agent can query current systems, databases, APIs, or code execution environments.

## Function Calling vs Tool Calling

The chapter broadens the concept from "functions" to "tools." A tool might be a literal code function, but it might also be an API endpoint, a database query, or even another agent. That reframing is important because it treats the LLM as an orchestrator across external capabilities rather than as a standalone problem solver.

In practice, the book is arguing for a wider action space: the model should reason, then reach outward.

## Where Tool Use Matters

The examples include weather lookup, e-commerce inventory, financial calculations, email sending, code interpretation, and smart-home control. These cover the main reasons tool use exists:

- retrieving current information
- accessing user or system state
- performing precise deterministic operations
- triggering real-world actions

The chapter’s core claim is that modern agents become useful only when reasoning and execution are combined.

## Implementation Notes

The LangChain section shows a simple search tool wrapped and bound into an agent. The broader lesson is that tools must be clearly described, use explicit schemas, and return results in a form the model can reason over.

The chapter also points to frameworks like LangChain, LangGraph, and Google ADK as orchestration layers that handle the boundary between model output and actual execution.

## Design Constraints

Tool use is powerful, but it introduces new failure modes: wrong tool selection, bad parameter extraction, tool failure, and misleading or ambiguous tool outputs. So the value of function calling depends heavily on tool design, interface clarity, and downstream handling.

This chapter pairs naturally with routing and exception handling. Once an agent has tools, it also needs logic for choosing among them and recovering when they fail.

---

## Key Takeaways

- Tool use is the pattern that lets an LLM act on the world instead of only describing it.
- Function calling is the structured mechanism most frameworks use to implement that behavior.
- Good tool interfaces need clear descriptions, schemas, and predictable outputs.
- The pattern is essential for real-time retrieval, deterministic computation, and external action.
- Tool use expands agent capability, but it also makes orchestration and error handling more important.
