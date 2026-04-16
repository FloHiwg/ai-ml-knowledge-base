# Chapter 10: Model Context Protocol

**Source:** [[raw/books/Agentic Design Patterns.pdf]]
**Book:** [[summaries/Agentic Design Patterns/00 Index]]
**Related:** [[summaries/Teaching Language Models to use Tools]] · [[summaries/Harness engineering leveraging Codex in an agent-first world  OpenAI]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

The Model Context Protocol (MCP) is presented as a standard interface for connecting LLM-based agents to external resources, prompts, and tools. Instead of building one-off integrations for every model and every system, MCP provides a client-server protocol that lets compliant agents discover capabilities and interact with them in a consistent way.

---

## Why MCP Exists

The chapter frames MCP as a response to integration sprawl. Tool use works, but ordinary function calling is often vendor-specific and tightly coupled to a given application. MCP aims at a broader ecosystem where models and services can interoperate through a shared contract.

The key promise is reuse: one compliant server can expose capabilities to many compliant clients.

## MCP vs Function Calling

The book makes a careful distinction here. Function calling is a direct way for a model to invoke a known capability during a single application flow. MCP is the higher-level standard that describes how capabilities are exposed, discovered, and consumed across systems.

So function calling is a mechanism; MCP is an interoperability layer.

## Resources, Tools, and Prompts

One of the chapter’s most useful clarifications is the three-way split:

- resources are static or retrievable data
- tools are executable capabilities
- prompts are templates that structure how the model should use those resources and tools

That breakdown matters because not every external thing should be modeled as an action. Some things are context, some are operations, and some are interface scaffolding.

## The Important Caveat

The strongest engineering point in the chapter is that MCP does not magically make bad APIs agent-friendly. If the underlying system returns the wrong shape of data or only exposes awkward low-level operations, wrapping it in MCP still leaves the agent with a poor interface.

The document uses this to argue for better deterministic infrastructure beneath agent layers. Agents work best when the surrounding APIs are already designed to support filtering, sorting, summarization, and machine-usable outputs.

## Architecture and Operations

The chapter walks through MCP’s client-server design, discovery flow, transport mechanisms, local vs remote deployment, and the importance of security and error handling. The discovery story is especially central: a client can query a server to learn what tools, resources, and prompts are available rather than being hardcoded against each one.

This makes MCP appealing for environments where capabilities change over time.

---

## Key Takeaways

- MCP is a standard for exposing agent capabilities, not just a single tool-calling trick.
- It formalizes how clients discover and use resources, prompts, and tools.
- The chapter contrasts MCP with direct vendor-specific function calling.
- Good MCP systems still depend on good underlying APIs and usable data formats.
- The biggest benefit is interoperability; the biggest risk is wrapping poor interfaces without improving them.
