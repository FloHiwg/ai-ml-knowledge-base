# Chapter 15: Inter-Agent Communication (A2A)

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[summaries/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]]

---

## Core Idea

Inter-agent communication gives independently built agents a standard way to discover one another, exchange tasks, and collaborate across framework boundaries. The chapter focuses on Google’s A2A protocol as an interoperability layer for multi-agent systems in the same way MCP serves as an interoperability layer for tools and context.

---

## Why A2A Exists

The chapter starts from a real limitation: individual agents and even agent frameworks become fragmented when each one has its own interface conventions. A2A addresses that by defining a common protocol so agents built with ADK, LangGraph, CrewAI, and other frameworks can interoperate without needing framework-specific glue for every pairing.

This makes the chapter as much about ecosystem design as about agent architecture.

## Core A2A Concepts

The protocol is introduced through several components:

- user
- client agent
- server or remote agent
- agent cards for identity and capability description
- discovery mechanisms
- tasks, messages, parts, and artifacts

The agent card is especially central. It acts like a machine-readable profile that tells other agents what capabilities are available, where to send requests, what interaction modes are supported, and how authentication works.

## Interaction Modes

The chapter lays out several communication patterns:

- synchronous request/response
- asynchronous polling
- server-sent event streaming
- push notifications via webhooks

This is important because it shows that inter-agent collaboration is not always a simple RPC call. Long-running work may need status tracking, streaming partial artifacts, or asynchronous completion notifications.

## Security and Discovery

The book also emphasizes discovery and security. Agents may advertise themselves through well-known URIs, curated registries, or direct configuration, but those discovery surfaces must still be protected. Access control, mTLS, and network restrictions matter because even metadata about capabilities can be sensitive.

That gives the chapter a more production-oriented feel than a purely academic protocol discussion.

## Practical Meaning

The broader idea is that multi-agent systems become much more flexible once agents can be treated as interoperable services. A client does not need to know how the remote agent works internally. It only needs a clear contract for requesting work and receiving results.

This shifts the design focus from internal implementation to stable external capability boundaries.

---

## Key Takeaways

- A2A is an interoperability protocol for agent-to-agent collaboration.
- Agent cards, discovery, tasks, and artifacts are the main building blocks.
- The protocol supports synchronous, asynchronous, streaming, and push-based interactions.
- The chapter treats agent interoperability as an ecosystem problem, not just a coding convenience.
- Clear contracts and secure discovery are essential if multi-agent systems are going to scale beyond one framework.
