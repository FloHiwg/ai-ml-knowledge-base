# Teaching Language Models to use Tools

**Source:** [[raw/articles/Teaching Language Models to use Tools]]
**Author:** Cameron R. Wolfe, Ph.D.
**Related:** [[summaries/AI Agents from First Principles]] · [[summaries/LLM Powered Autonomous Agents  Lil'Log]] · [[summaries/Understanding and Using Supervised Fine-Tuning (SFT) for Language Models]]

---

## Core Idea

LLMs have well-known limitations — arithmetic errors, knowledge cutoffs, hallucinations, poor temporal reasoning — that can be addressed more reliably by delegating those tasks to specialized external tools than by trying to bake all capabilities into model weights. This article surveys how LLMs are taught to use tools, from early fine-tuning approaches (Toolformer) to the prompt-based approach enabled by instruction-tuned models like GPT-4.

---

## Three Forms of LLM Learning

| Form | Modifies weights? | When used |
|---|---|---|
| **Pre-training** | Yes | One-time, expensive; establishes all parametric knowledge |
| **Fine-tuning (SFT/RLHF)** | Yes | Task adaptation, alignment, capability injection |
| **In-context learning** | No | Prompt-time adaptation; zero-shot or few-shot; no gradient updates |

For tool use, both fine-tuning (Toolformer) and in-context learning (GPT-4 plugins) are viable, with the field converging toward the latter.

---

## Why Tools?

LLM limitations that tools address directly:

| Limitation | Tool |
|---|---|
| No access to current information (knowledge cutoff) | Web search, Wikipedia search |
| Arithmetic errors | Calculator |
| No temporal awareness (current date) | Calendar API |
| Low-resource language gaps | Translator |
| Need for precise factual lookup | QA systems, vector DBs |

The key insight: rather than fine-tuning the LLM to improve at arithmetic (expensive, unreliable), delegate arithmetic to an external calculator that is always correct.

---

## Toolformer: Self-Supervised Fine-Tuning for Tool Use

**Paper:** Schick et al. (2023), "Toolformer: Language models can teach themselves to use tools"  
**Base model:** GPT-J (6B parameters)

### Tools Available (5 text-to-text APIs)

| Tool | What it does |
|---|---|
| **Question Answering** (Atlas) | Fact-based QA |
| **Calculator** | Arithmetic evaluation |
| **Wikipedia Search** | Short snippet retrieval by search term |
| **Translator** | Any language → English |
| **Calendar** | Returns current date |

All tools expose a text-to-text API: the LLM sends a text string, the tool returns a text string. API calls are formatted inline in the token stream.

### Dataset Construction (Self-Supervised, No Human Labels)

Prior approaches (e.g., LaMDA) required massive human-annotated datasets of tool-using dialogues. Toolformer automates this:

1. **Prompt augmentation**: Use a pre-trained LLM's in-context learning ability + few examples per tool to generate candidate API calls inserted into a large text corpus (e.g., pre-training data)
2. **Filtering**: Keep only API calls that improve next-token prediction:
   - Measure cross-entropy loss on tokens *after* the API call — **with the tool response**
   - Compare against loss **without the tool** and loss **with the API call but no response**
   - Discard if improvement is below a threshold
   - Assign higher weight to tokens spatially close to the API call (the tool should be called when needed, not randomly)
3. **Fine-tune** on the filtered dataset using standard next-token prediction objective

This produces a dataset where every example demonstrates a tool call that genuinely helps the model.

### Key Results

- Toolformer (6B GPT-J) outperforms GPT-3 (175B) on several benchmarks when tools are available
- Calendar tool dramatically improves temporal reasoning
- QA and Wikipedia tools improve factual accuracy
- Calculator tool improves math benchmark performance
- **Perplexity preserved**: fine-tuned Toolformer achieves comparable perplexity to base GPT-J on held-out pre-training data — it remains a general-purpose LM

### Critical Finding: More Tool Use ≠ Better

Increasing the probability of tool calls beyond what the model naturally learns *degrades* performance. The filtering step is what makes Toolformer work — it calibrates the model to call tools only when they genuinely help, not indiscriminately. Tool use has latency (and sometimes monetary) cost; unnecessary calls add noise.

---

## Prompt-Based Tool Use: The GPT-4 Plugin Approach

As instruction-following improves, explicit fine-tuning for tool use becomes unnecessary. The GPT-4 plugin workflow requires only:

1. A **textual description** of the plugin's purpose
2. A **schema** describing the input/output format of the tool's API

GPT-4's strong steerability (trained via RLHF to follow detailed instructions) allows it to:
- Determine when a tool is relevant based on the description
- Format API calls correctly based on the schema
- Integrate tool output into its response

No gradient updates required. This represents the convergence of the field: as models become better instruction followers, tool use becomes a prompting problem rather than a fine-tuning problem.

---

## Evolution of Tool Use Approaches

| Approach | Training needed | Generalization | Example |
|---|---|---|---|
| Human-annotated fine-tuning | Large annotated dataset | Task-specific | LaMDA, TALM |
| Self-supervised fine-tuning | Automated dataset (Toolformer) | General-purpose | Toolformer |
| Prompt-based (schema + description) | None (ICL only) | Any new tool instantly | GPT-4 plugins, MCP |

---

## Key Takeaways

- Tools address LLM limitations more reliably than training: always-correct calculators beat fine-tuning LLMs to do arithmetic
- Toolformer: self-supervised dataset construction via LLM-generated + filtered API call examples; no human annotation required
- Filtering criterion: keep API calls that lower cross-entropy loss on subsequent tokens; calibrates *when* to call tools, not just *how*
- More tool calls ≠ better; over-triggering degrades performance — the filtering step is essential
- Toolformer preserves general LM capability (similar perplexity) after tool-use fine-tuning
- Prompt-based tool use (GPT-4): textual description + API schema is sufficient for instruction-tuned models; no fine-tuning needed
- The field converged: as instruction following improved, tool use shifted from fine-tuning to in-context learning (see MCP)
