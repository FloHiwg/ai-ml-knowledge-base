# Skill Issue: Harness Engineering for Coding Agents — HumanLayer Blog

**Source:** [[raw/articles/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]]
**Author:** HumanLayer (Dex Horthy et al.)
**Related:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]] · [[summaries/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]] · [[summaries/AI Agents from First Principles]]

---

## Core Idea

Coding agent failures are rarely model problems — they are **configuration problems**. The article frames the configuration surface of a coding agent as its **harness** (system prompt, tools/MCPs, context, sub-agents, hooks, skills), and argues that **harness engineering** — systematically fixing each failure mode so it never recurs — is the highest-leverage activity for improving agent reliability. Harness engineering is itself a subset of **context engineering**: the discipline of carefully managing what lands in the agent's context window.

---

## Harness Engineering as Context Engineering

Four customization levers (from Viv's framing):
1. System prompt
2. Tools / MCP servers
3. Context
4. Sub-agents

The article adds two more underemphasized levers:
- **Hooks** — automated, deterministic control flow at lifecycle events
- **Skills** — progressive disclosure of instructions and tools

The definition used: *anytime the agent makes a mistake, engineer a solution so it never makes that mistake again* (Mitchell Hashimoto).

A key caveat on post-training coupling: models post-trained on a specific harness can be **over-fitted** to it. Terminal Bench 2.0 data: Claude Opus 4.6 ranks #33 in the Claude Code harness it was trained on, but climbs to #5 in a different harness. Tight harness coupling is not always an advantage.

---

## CLAUDE.md / AGENTS.md

The cheapest, highest-leverage starting point before any other harness work. These markdown files at the repo root are **deterministically injected** into the system prompt.

### ETH Zurich Study Findings (138 agentfiles across various repos)

| Finding | Implication |
|---|---|
| LLM-generated agentfiles hurt performance, cost 20%+ more | Write them by hand |
| Human-written ones helped only ~4% | Every line must earn its place |
| Agents spent 14–22% more tokens processing instructions, took more steps, ran more tools — without better resolution | Instruction budget is real and finite |
| Codebase overviews and directory listings didn't help | Agents discover structure on their own |

### Principles for good CLAUDE.md files
- **Write it by hand** — never auto-generate
- **Less is more** — include only universally applicable instructions
- **Progressive disclosure** — don't dump everything upfront
- **Concise and unconditional** — avoid complex conditional rules
- HumanLayer's own file is under 60 lines

---

## MCP Servers: Tools, Not Everything

MCP servers are primarily for extending the tool surface — not resources, prompts, or elicitations (those are poorly supported by most clients).

**How they inject context:** tool definitions, descriptions, and argument schemas are added directly to the system prompt. This burns instruction budget even for tools the agent never uses.

### Too Many Tools Problem

Too many MCP tools fill the context window with unused definitions, pushing the agent into the "dumb zone" faster. Anthropic released experimental MCP tool search (progressive disclosure) to address this.

**Rules of thumb:**
- If not actively using a large-tool server, disconnect it
- If a tool duplicates a CLI well-represented in training data (GitHub, Docker, most DBs), use the CLI instead — it's composable with `grep`/`jq` and more context-efficient

### Context-Efficient Tool Wrapping

HumanLayer replaced the Linear MCP server with a custom CLI that exposes only the 6 commands they actually use, with example invocations in CLAUDE.md. Result: thousands of tokens saved per session from avoided tool definitions and verbose MCP responses.

### Security Warning

MCP server tool descriptions are injected into the system prompt — connecting an untrusted server is a prompt injection vector. STDIO servers running via `npx`/`uvx` also execute arbitrary code on the host. Treat skill registries like `npm install random-package` — read before installing.

---

## Skills: Progressive Disclosure of Knowledge

Skills are instruction modules that load into the agent's context window **on demand** rather than upfront. Originally an Anthropic/Claude Code concept, now an open standard (Codex, OpenCode).

### Activation Mechanism

When a skill is activated, its `SKILL.md` file is loaded as a user message. The file can reference companion files in the skill's directory:

```
example-skill/
├── SKILL.md
├── response_template.md
└── CLIs/
    ├── linear-cli
    └── tunnel-cli
```

The `SKILL.md` can instruct the agent on what else exists in the skill directory and when to read it — enabling multi-level progressive disclosure.

### Why Skills Beat Upfront Instructions

Stuffing all instructions into the system prompt exhausts the **instruction budget** before the agent starts working. Skills solve this: the agent gets only the instructions relevant to the current task when it actually needs them.

Skills can bundle CLIs and executables as an alternative to MCP servers for delivering tools.

---

## Sub-Agents: Context Firewalls

Sub-agents are not for persona separation ("frontend engineer," "backend engineer" — this doesn't work). They are for **context isolation**: encapsulating an entire agent session so only the condensed result flows back to the parent.

### Context Rot (Chroma Research)

Chroma tested 18 models on needle-in-a-haystack tasks. Findings:
- Performance degrades as context length increases — even on simple tasks
- When semantic similarity between query and relevant content is low, degradation is steeper
- Distractor effects compound at longer context windows

Every irrelevant tool call, grep result, or file read in the parent session is a potential distractor. Sub-agents are the structural fix.

### Why Bigger Context Windows Don't Help

Extended-context models use positional encoding extensions (e.g., YaRN) on the same model weights — they don't improve needle-finding ability, just make the haystack bigger. Each user message is at least one instruction; more context = deeper in the dumb zone. Sub-agents provide a fresh, small, high-relevance context window for each discrete task.

### Sub-Agent Design Principles

- Return **highly condensed responses** with `filepath:line` citations — parent gets pointers, not raw content
- Specify clearly: what the sub-agent should do, what it should NOT do, what to return and how, what tools it has
- Use **cheaper models** (Sonnet/Haiku) for sub-agents; reserve Opus for the parent orchestrator
- Many harnesses lack native sub-agent support — can be emulated via an MCP server that launches a new agent session

### Good Sub-Agent Use Cases

- Locating definitions or implementations in the codebase
- Analyzing codebase patterns for a specific type of work
- Tracing request flows across service boundaries
- Research tasks that require many tool calls but have a simple answer

---

## Hooks: Deterministic Control Flow

Hooks (Claude Code) / plugins (OpenCode) execute automatically at agent lifecycle events. Conceptually similar to git hooks but more flexible. Codex currently lacks an equivalent.

### What Hooks Can Do

- Run silently on events (e.g., on stop)
- Return additional context to the agent alongside a tool result
- Surface build/type errors before the agent finishes (forcing it to fix them)
- Automatically approve or deny tool calls based on rules more expressive than the default permission model

### Common Use Cases

| Use Case | Example |
|---|---|
| **Notifications** | Play a sound when the agent finishes or needs approval |
| **Approval enforcement** | Auto-deny `Bash()` calls that run database migrations; instruct agent to ask user instead |
| **Integrations** | Send Slack message, open GitHub PR, or spin up a preview env when agent stops |
| **Verification** | Run typecheck/build on stop; surface errors; force agent to fix before finishing |

### Hook Design Principle

Success should be **silent** — nothing enters the agent's context. Only errors produce output. Exit code `2` re-engages the agent to fix the issue; exit `0` releases it.

---

## Back-Pressure: Verification Mechanisms

The likelihood of successfully completing a coding task is strongly correlated with the agent's ability to verify its own work. High-leverage investments:

- Typechecks and build steps (especially in strongly-typed languages)
- Unit and integration tests
- Code coverage reporting (hook that prompts agent to increase coverage if it drops)
- UI interaction testing (Playwright, agent-browser)

**Critical constraint:** verification must be context-efficient. Running the full test suite floods the context window with passing test output, causing the agent to lose focus. Swallow stdout on success; surface only errors.

---

## Practical Lessons

**What didn't work:**
- Designing the ideal harness upfront before hitting real failures
- Installing dozens of skills and MCP servers "just in case"
- Running the full test suite (5+ min) at end of every session
- Micro-optimizing which sub-agents could access which tools (causes tool thrash)

**What did work:**
- Start simple; add configuration only when the agent actually fails
- Design, test, iterate — throw away what doesn't help
- Distribute battle-tested configs to the team via repository-level config files
- Optimize for iteration speed, not one-shot success
- Give the agent a capability (e.g., Linear), then carefully pare down exposure based on actual usage

---

## Key Takeaways

- **It's a configuration problem, not a model problem.** GPT-6 won't save you; harness engineering will.
- **Instruction budget is finite and real.** Every tool definition, agentfile line, and system prompt instruction costs tokens that could have been used for reasoning.
- **Progressive disclosure** is the master principle: skills, sub-agents, and context-efficient tool wrappers all serve the same goal — give the agent what it needs, when it needs it, and nothing else.
- **Sub-agents are context firewalls**, not personas. Use them to isolate noise, not to simulate team roles.
- **Hooks enforce determinism**. They add control flow that prompting alone cannot achieve reliably.
- **Verification must be silent on success.** Back-pressure only helps if failures surface clearly and successes produce no noise.
- **Models can be over-fitted to their harness.** Don't assume the default harness is optimal.
