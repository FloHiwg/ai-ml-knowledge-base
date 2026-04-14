# Scaling Managed Agents: Decoupling the brain from the hands — Anthropic

**Source:** [[raw/articles/Scaling Managed Agents Decoupling the brain from the hands  Anthropic]]
**Author:** Lance Martin, Gabe Cemaj, and Michael Cohen (Anthropic)
**Related:** [[summaries/Harnessing AI Agents The Design and Evolution of Harness Engineering  Weng Jialin]] · [[summaries/AI Agents from First Principles]] · [[summaries/Design Patterns for Securing LLM Agents against Prompt Injections]]

---

## Core Idea

Anthropic's Managed Agents is a hosted agent service built around a key insight borrowed from OS design: virtualize the components of an agent into stable interfaces so that implementations can be swapped freely as models improve. By decoupling the **brain** (Claude + harness) from the **hands** (sandboxes, tools) and the **session** (durable event log), each layer becomes independently replaceable and survivable — turning brittle "pet" containers into resilient "cattle."

---

## The Pet Problem: Why Coupling Failed

The initial single-container design bundled the harness, sandbox, and session into one unit:

- **Debuggability**: failures in harness vs. event stream vs. container presented identically through the WebSocket event stream; diagnosis required shell access inside containers holding user data
- **Infrastructure coupling**: the harness assumed all resources sat next to it — connecting to customer VPCs required network peering or running Anthropic's harness inside the customer's environment
- **Scalability**: each "brain" required its own container, so every session paid full container setup cost even for sessions that never touched the sandbox

The Pets vs. Cattle framing applies: a coupled container is a pet — named, hand-tended, unaffordable to lose. The fix is to turn every component into cattle.

---

## The Three-Interface Architecture

Managed Agents virtualizes agent infrastructure into three independent interfaces:

| Interface | Role | Key operations |
|---|---|---|
| **Session** | Append-only durable event log (lives outside harness) | `getSession(id)`, `getEvents()`, `emitEvent(id, event)` |
| **Harness (Brain)** | Orchestration loop; stateless — can crash and reboot | `wake(sessionId)` resumes from last event |
| **Sandbox (Hands)** | Execution environment; provisioned on demand | `provision({resources})`, `execute(name, input) → string` |

### Harness Leaves the Container

The harness calls the sandbox through the same interface as any other tool: `execute(name, input) → string`. A container failure is caught as a tool-call error, passed back to Claude. If Claude retries, a new container is initialized via `provision({resources})`. No more nursing.

### Session as External Context Store

Because the session log lives outside the harness:
- Harness crashes don't lose context — a new harness reboots with `wake(sessionId)` and fetches events
- `getEvents()` supports positional slices: pick up from the last read position, rewind before a specific moment, re-read context before a consequential action
- Events can be transformed in the harness before passing to Claude's context window (prompt cache optimization, context engineering) without losing recoverability

This directly addresses a fundamental agent challenge: irreversible context decisions (compaction, trimming) can lose tokens needed by future turns. The session log keeps everything; the harness applies whatever context engineering is needed.

---

## Security: Structural Credential Isolation

In the coupled design, untrusted code Claude generated ran in the same container as credentials — prompt injection could exfiltrate tokens and spawn unrestricted sessions. Narrow-scoping is a mitigation, but it encodes assumptions about what Claude can't do with a limited token, and those assumptions go stale as models improve.

The structural fix: **credentials must never be reachable from the sandbox where Claude's generated code runs**.

Two patterns:

| Pattern | Mechanism |
|---|---|
| **Auth bundled at init** | e.g., Git: repo access token clones the repo during sandbox initialization, wired into local git remote. `push`/`pull` work without the agent ever seeing the token. |
| **Vault + proxy** | Custom MCP tools: OAuth tokens stored in a secure vault. Claude calls MCP tools via a dedicated proxy. The proxy fetches credentials from the vault and calls the external service. The harness never sees credentials. |

---

## Performance: TTFT Improvements

Decoupling brain from hands had direct latency payoff:

- Before: every session paid container setup cost upfront; inference waited for container provisioning
- After: containers provisioned only when needed via `execute()`. Inference starts as soon as the orchestration layer pulls pending events from the session log.

**Results:**
- p50 TTFT dropped ~60%
- p95 TTFT dropped >90%

Scaling to many brains means starting many stateless harnesses; containers only attach if the task requires them.

---

## Many Brains, Many Hands

### Many Brains

- Stateless harnesses can scale horizontally — each is just a loop connecting to the session log and calling tools
- Customers can run the harness in their own VPC against their own resources without network peering, since the harness no longer assumes resources are co-located

### Many Hands

Each hand is just a tool: `execute(name, input) → string`. The harness is agnostic to whether the sandbox is a container, a phone, or anything else. Because no hand is coupled to any brain:
- Brains can reach into multiple execution environments simultaneously
- Brains can pass hands to one another

Earlier models couldn't reason reliably about multiple execution environments. As intelligence scaled, the single-container assumption became the bottleneck rather than a simplification.

---

## Harness Staleness and the Meta-Harness Design

The article opens with a concrete example: context-reset logic added to address Claude Sonnet 4.5's "context anxiety" (premature task wrap-up near context limit) became dead weight on Claude Opus 4.5, where the behavior had disappeared. Harness assumptions go stale as models improve.

Managed Agents is a **meta-harness**: opinionated about the *interfaces* around Claude (session, sandbox, tools), not about the specific harness implementation. It can accommodate Claude Code, task-specific harnesses, or future harnesses not yet designed — matching the underlying principle of OS design where abstractions (process, file, read()) outlasted the hardware they virtualized.

---

## Key Takeaways

- **Decouple brain, hands, and session** into independent interfaces. Each becomes cattle — replaceable and independently survivable.
- **Session as external log** solves both durability and context recoverability. It is not Claude's context window; it is the ground truth that the harness queries and transforms.
- **Credential isolation must be structural**: proxies and init-time auth bundling keep credentials out of the sandbox where Claude's code runs, regardless of how capable Claude becomes.
- **TTFT improves dramatically** when containers provision on demand rather than upfront — p50 -60%, p95 -90%.
- **Harness assumptions go stale**. Design for this by putting assumptions in the harness (swappable) not in the infrastructure (durable).
- **Many brains, many hands** become natural once each is a stateless service connected via a simple interface.
