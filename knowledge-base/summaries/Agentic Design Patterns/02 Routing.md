# Chapter 2: Routing

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/AI Agents from First Principles]] · [[summaries/Patterns for Building LLM-based Systems & Products]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]]

---

## Core Idea

Routing adds conditional control flow to agent systems. Instead of always following one fixed chain, the agent first classifies the situation, then selects the most appropriate next step, tool, workflow, or specialist. The chapter frames routing as the bridge from deterministic pipelines to adaptive systems that can respond differently based on intent, state, or context.

---

## Why Routing Matters

The chapter contrasts routing with prompt chaining. Chaining is useful when the path is already known; routing becomes necessary when the system must choose among multiple possible paths. A customer-support example runs throughout the chapter: the same incoming request might need order lookup, product information, technical troubleshooting, or a clarification loop.

That makes routing a control mechanism rather than a knowledge mechanism. Its main job is to decide what should happen next.

## Routing Mechanisms

The book outlines four broad routing strategies:

- LLM-based routing, where the model classifies the input and emits a route label
- embedding-based routing, where semantic similarity is used to map an input to the closest capability
- rule-based routing, where keywords or explicit conditions choose the path
- model-based routing, where a separate trained classifier handles dispatch

The core tradeoff is flexibility versus determinism. Rule systems are predictable and fast; LLM routing handles nuance better; embedding and classifier approaches sit between those poles depending on how the system is built.

## Where Routing Appears in Agent Workflows

Routing can happen at more than one layer:

- up front, to classify the overall request
- mid-workflow, to decide the next operation after an intermediate result
- inside a tool-selection step, to choose which external capability to invoke

The chapter emphasizes that routing is not just a chatbot trick. It is a general mechanism for steering agent execution in graphs, state machines, and multi-step tool workflows.

## Practical Uses

The examples span virtual assistants, tutoring systems, document-processing pipelines, AI coding assistants, and multi-agent research systems. In each case, the system becomes more useful once it can dispatch work to the right downstream handler instead of treating every request as the same type of task.

One recurring benefit is specialization. Routing lets a system connect narrow, reliable components into a broader agent without forcing one model prompt to handle everything.

## Implementation Notes

The implementation section uses LangChain and Google ADK. The LangChain example sets up a coordinator that classifies a request into a small set of handler types and then delegates to the appropriate function. The ADK framing treats routing more like agent orchestration inside a managed execution environment.

The design lesson is that routing logic should have explicit outputs and stable route names. If the router emits vague natural language instead of a constrained decision, the downstream workflow becomes brittle.

## Limits and Design Guidance

The chapter implicitly argues that routing quality determines system reliability. A bad route means the rest of the workflow starts from the wrong assumptions. That means the router should usually be narrow, observable, and easy to test, rather than overloaded with too many subtle categories.

Routing also works best when paired with strong downstream modules. Good dispatch alone does not fix weak tools or poorly designed specialist branches.

---

## Key Takeaways

- Routing is the pattern that gives agents conditional behavior.
- It is useful when the next step depends on user intent, context, or intermediate state.
- The chapter distinguishes LLM, embedding, rule-based, and classifier-based routing.
- Good routing makes specialization possible by sending work to the right handler or agent.
- The main engineering challenge is to keep route decisions explicit, constrained, and testable.
