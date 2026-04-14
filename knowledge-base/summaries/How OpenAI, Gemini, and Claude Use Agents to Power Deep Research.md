# How OpenAI, Gemini, and Claude Use Agents to Power Deep Research

**Source:** [[raw/articles/How OpenAI, Gemini, and Claude Use Agents to Power Deep Research]]  
**Author:** ByteByteGo  
**Related:** [[summaries/AI Agents from First Principles]] · [[summaries/Building Multi-Agent Systems (Part 3) - by Shrivu Shankar]] · [[wiki/applications/agentic-patterns]]

---

## Core Idea

Deep Research features on major LLM platforms (ChatGPT, Gemini, Claude, Perplexity, Grok, Copilot, Qwen) are multi-agent systems that coordinate planning, parallel web retrieval, and structured synthesis to produce lengthy, cited research reports from a single user query. A typical request triggers dozens of searches, multiple rounds of filtering, and 15–30 minutes of coordinated agent activity before producing a final report.

---

## High-Level Architecture

All Deep Research systems share a common three-phase structure:

```
User Query → [Orchestrator/Lead Agent]
                 ↓ delegates subtasks
         [Sub-Agent 1] [Sub-Agent 2] ... [Sub-Agent N]  ← parallel execution
           (search + extract + cite)
                 ↓ returns content + citations
         [Synthesizer Agent] + [Citations Agent]
                 ↓
           Final cited research report → User
```

**Key roles:**
- **Orchestrator/Lead Agent**: interprets the query, produces a research plan, delegates subtasks, manages dependencies
- **Sub-agents (web search agents)**: each handles a specific angle, region, time period, or dimension of the question; returns content snippets + source citations
- **Synthesizer agent**: collects all sub-agent output, identifies themes, resolves overlaps, writes the narrative
- **Citations agent**: reviews the draft and inserts citations at correct locations (in some systems this is part of the synthesizer)

In some systems (e.g., Anthropic's Advanced Research), the orchestrator itself doubles as the synthesizer, so no separate synthesizer agent is needed.

---

## Provider-by-Provider Architecture Variations

| Provider | Key differentiator |
|---|---|
| **OpenAI Deep Research** | Reasoning model trained with RL; agent learns to plan multi-step tasks, decides when to search vs. read vs. combine; interactive clarification before starting (asks follow-up questions to refine scope) |
| **Gemini Deep Research** | Multimodal (integrates text + images + other media); autonomously generates a comprehensive multi-step plan for user review/approval before research begins |
| **Claude Advanced Research** | Clearly defined lead agent + parallel sub-agents; each sub-agent explores a specific angle simultaneously; results flow back to orchestrator for synthesis |
| **Perplexity Deep Research** | Iterative retrieval loop — repeatedly adjusts retrieval based on new insights; hybrid model selection (routes subtasks to the best underlying model for that function) |
| **Grok DeepSearch** | Segment-level processing pipeline with credibility assessment per segment; sparse attention for concurrent reasoning across documents; dynamic allocation between retrieval and analysis modes; secure sandbox |
| **Microsoft Copilot Researcher/Analyst** | Two separate agents: Researcher (multi-step research over web + enterprise data) and Analyst (chain-of-thought data analytics, raw data → insights); designed for enterprise security |
| **Qwen Deep Research** | Dynamic research blueprinting — generates initial plan then refines it interactively; concurrent task orchestration (retrieval, validation, synthesis in parallel) |

---

## Planning Phase

The first critical stage converts an often vague user query into a precise, machine-executable research plan. Two main approaches:

**Interactive clarification (OpenAI):** Before committing to a long research run, the agent asks the user follow-up questions to refine scope, clarify objectives, and confirm constraints. Research begins only after the agent has a precise understanding of intent.

**Autonomous plan proposal (Gemini):** The agent generates a comprehensive multi-step plan autonomously, then presents it to the user for review, editing, and approval before execution. The user can remove sub-tasks or add constraints at this stage.

Plan quality directly determines report quality — a flawed or incomplete plan results in missing key information.

---

## Sub-Agent Delegation and Parallel Execution

The orchestrator delegates via structured API calls. Each sub-agent payload contains:
- A precise prompt with a specific research goal
- Constraints (time ranges, data sources, page limits)
- Tool access permissions

**Specialization is common:** Rather than general-purpose research agents, systems use pools of specialized agents:
- **Web search agents**: optimized for effective query formation, search engine interaction, and snippet interpretation
- **Data analysis agents**: have code interpreter access; perform statistical analysis, process CSV files, generate visualizations

**Parallel + dependency-aware**: Most sub-tasks run simultaneously; tasks with dependencies on other sub-tasks wait until their inputs are ready.

---

## Tool Use

Sub-agents interact with the outside world through tools (they have no direct web/file access):

| Tool | Function |
|---|---|
| `web_search(query=...)` | Calls external search API (Google/Bing), returns URLs + snippets |
| `browse(url=...)` | Fetches full text of a webpage |
| `code_interpreter` | Executes Python in a sandboxed environment; processes data, computes results |

When initial search results are weak, agents self-correct by refining queries (adding keywords like "PDF," "quarterly report," specific year).

Each sub-agent maintains its own short-term memory/context to track findings and avoid repeated work. Output is a self-contained packet: content snippets + their source citations.

---

## Synthesis and Report Generation

Once all sub-agent packets are returned:

1. **Aggregation & thematic analysis**: Orchestrator/synthesizer collects packets, identifies themes, overlaps, and logical connections across sub-agent findings
2. **Narrative outline**: Structure is chosen to best fit the material (chronological, thematic, problem/solution)
3. **Narrative writing**: Draft is written with transitions; redundant information from multiple sub-agents is merged
4. **Citation insertion**: Each claim is connected to its source via a dedicated citations agent (or the synthesizer itself)

The outcome is a polished, fully-cited research document ready for the user. This citation step is crucial for preventing hallucinations — every assertion must trace back to a verified source.

---

## Key Takeaways

- Deep Research is fundamentally a **multi-agent orchestration problem**: the value comes from coordinated parallel exploration, not from a single powerful model
- **Planning quality is the upstream bottleneck**: a bad plan produces a bad report regardless of downstream execution quality
- The **orchestrator–sub-agent–synthesizer** structure is shared across all major providers; providers differ primarily in how they handle planning (interactive vs. autonomous) and what specialized sub-agents they provide
- **Tools are the mechanism** by which agents interact with the real world; agents themselves are stateless with respect to external systems
- **Citation tracking is essential** throughout the pipeline — content and sources must be kept paired from retrieval through synthesis to prevent hallucinations in the final report
- As LLMs improve in planning, reasoning, and tool use, Deep Research systems will become more capable, reliable, and comprehensive

See [[wiki/applications/agentic-patterns]] for the broader framework of multi-agent system design.
