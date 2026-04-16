# Agentfile Quality: Agent-Written Files and Content Length

**Query:** Which article describes that agent-written CLAUDE.md/AGENTS.md files are worse, and that too much content is worse than too little?

---

## Answer

The findings come from the **ETH Zurich study** (138 agentfiles tested across real repos), surfaced and discussed in:

- **Primary source:** [[../summaries/Skill Issue Harness Engineering for Coding Agents  HumanLayer Blog]]
- **Also references it:** [[../summaries/AINews Is Harness Engineering real - Latent.Space]]

---

## Key Findings (ETH Zurich Study)

| Finding | Implication |
|---|---|
| LLM-generated agentfiles **hurt** performance, cost **20%+ more** | Write them by hand — never auto-generate |
| Human-written agentfiles helped only **~4%** | Every single line must earn its place |
| More instructions → agents spent 14–22% more tokens, took more steps, used more tools — **without better task resolution** | Instruction budget is finite; more content actively harms |
| Codebase overviews and directory listings gave no benefit | Agents discover structure on their own |

**The key asymmetry:** too much content is strictly worse (budget burns, performance degrades). Too few instructions is merely neutral. Less is more.

---

## Relevant Wiki Coverage

- [[../wiki/applications/agent-harness]] — Section **"CLAUDE.md / AGENTS.md: The Cheapest Lever"** and **"The Instruction Budget"** cover these findings in full, including the three levers for staying within the instruction budget (remove unused tools, use skills for progressive disclosure, use sub-agents as context firewalls).

---

## Practical Rules Derived

1. **Write by hand** — never auto-generate or let an agent write the agentfile
2. **Under 60 lines** — HumanLayer's own file is a reference benchmark
3. **Universally applicable only** — no complex conditionals, no task-specific instructions
4. **No structural content** — codebase overviews and directory listings don't help
5. **Progressive disclosure** — use Skills to inject instructions only when the relevant task starts, rather than front-loading everything
