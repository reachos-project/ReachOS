# 13 — What the runtime has to provide

> **Scope.** The host capabilities this architecture assumes. Everything else in this repo is
> written as if these already exist; this page says what "these" are, so a reader can decide
> whether their stack can host it before instantiating anything.

This repo describes patterns, not a product. But the patterns are not stack-neutral: they
assume seven things about the substrate. Six are properties of the runtime that executes the
assistant; the seventh is a property of your corpus. If your host provides all of them,
everything here instantiates. If it provides five, you can still build — you just need to know
**which two** you are compensating for, and how.

## The capabilities

| # | Capability | Why the architecture needs it | If it is missing |
|---|---|---|---|
| 1 | **A coordinator file loaded automatically into every session** | Rules 1-8 (`docs/01`) only bind if they are in context before the first turn. Governance the assistant has to be reminded of is not governance. | The rules apply on the turns someone pastes them and not on the others. Compensate by prepending the file to every prompt — and accept the token cost on every turn. |
| 2 | **Sub-agent files with `name` / `description` / `tools` / `model` frontmatter, read by a dispatcher** | Routing (`docs/02`) is *selection*, and the `description` is the selection surface (`templates/agents/agent.template.md`). Per-agent `tools` is what makes containment per-role rather than global. | There are no agents, only prompt styles. One context does every domain and re-saturates — the problem this architecture exists to solve. |
| 3 | **A pre-execution hook receiving a structured payload on stdin, with exit-code semantics (`0` = allow, `≠0` = block)** | Every guardrail in `docs/05` and `examples/guardrails/` is this shape. It is the only interception point that sees a proposed action *before* it happens. | Layer C2 does not exist. Nothing catches a destructive command at the boundary; you are left with the OS sandbox alone (#6), which is absolute but blind to intent. |
| 4 | **Session-opening and session-closing hooks** | The opening and closing of `docs/10` — the shelf read, the layer count, the queue drain, the two-sided index diff — are jobs that must run *without being asked*. | The opening becomes something the person has to request, so it happens on good days. The index diff is the loss that matters: it is the only detector of a silently altered always-loaded file. |
| 5 | **A per-agent workspace, enforced** | Rule 5, and the write-control layer. An agent that can write anywhere makes "who changed this" unanswerable. | Traceability degrades to trust. Every write is attributable only by asking. |
| 6 | **An OS-level sandbox (filesystem allow/deny, network egress control)** | `docs/12`. The rule layer is lexical and can be phrased around; the sandbox refuses the syscall. It is the only layer that sees inside scripts. | The blast radius of a mistake is the account's full reach. Confined workers (`docs/07`) and the heartbeat daemon (`docs/06`) cannot be built at all. |
| 7 | **A retrieval layer over the corpus — semantic search, plus exact search** | Route 1 of `docs/02` is *executed*, not answered from memory; question 0 of `docs/01` requires one semantic and one verbatim search before proposing a change; `docs/03` is a tiered memory whose warm and cold tiers are useless without retrieval. | Every "has this been decided before?" is answered from recollection — the failure mode question 0 exists to prevent. Grep over the corpus is a workable floor; no retrieval at all is not. |

⚠️ **That makes seven, and the page says six.** The count is left honest rather than tidy: the
first six are what the runtime must expose, the seventh is what the corpus must expose, and it
was omitted from the original six because it is easy to mistake for a nice-to-have. It is not —
three separate rules in this repo are unexecutable without it.

⛔ **Capabilities 3 and 6 are not redundant with each other**, and treating them as such is the
common design error. The hook sees the *proposed action*; the sandbox sees *every syscall,
including from inside a script the hook already approved*. Each catches what the other cannot.

⚠️ **Capability 1 has a ceiling nobody documents for you.** Whatever file loads every session
has a size limit in the host, and past it content is silently dropped. Find the limit, measure
against it at every close, and keep the file well below — see `templates/MEMORY-INDEX.template.md`.
On one host that limit is roughly 25 KB and the runtime warns you before you reach it, naming a
target of about 70% of the cap; `docs/14-runtime-observed.md` has the measurement, along with the
reason the cost is worse than it looks — comments in such a file are **not** stripped, and every
edit near the top of the prompt is paid at write prices.

## Order of instantiation

Ten steps, and the order is not arbitrary: each one is what makes the next verifiable.

1. **Copy the templates** — `templates/ORCHESTRATOR.template.md`,
   `templates/ACTIVE.template.md`, `templates/MEMORY-INDEX.template.md`, `templates/agents/`,
   `templates/rules/`, `templates/skills/` — into your project root.
2. **Create the store** from `examples/db/schema.example.sql`. Nothing else logs until it exists.
3. **Run the first-run interview** (`templates/onboarding-interview.md`) and fill the
   orchestrator's tokens from the answers, not from the defaults.
4. **Write the first agents** the interview proposed — three to five, each with a real
   `description` and a `mode` (`D`/`P`) the person actually agreed to.
5. **Write the routing map** from those agents, then check it against the interview's pain
   points: a domain that came up twice and has no row is a missing agent, not a fallback.
6. **Arm the guardrails** — workspace enforcement first (capability 3), read-only store second.
   Test each with two probes: one that must block, one that must pass.
7. **Arm the sandbox profile** (capability 6), with the same two probes, run as the constrained
   identity rather than as yourself.
8. **Arm the session hooks** (capability 4), and take the first snapshot of the memory index —
   the diff has nothing to compare against until there is a baseline.
9. **Run one real session end to end**, on a task the person named in the interview. An
   architecture that is only explained does not get used.
10. **Close it properly** — the close is what proves capability 4 works, and the narrative log
    it writes is the part nothing else reconstructs.

## Principles

1. **Name the substrate before writing rules that assume it** — a rule that needs a hook nobody
   has is prose.
2. **Interception and confinement are different layers** — the hook reads intent, the sandbox
   refuses syscalls.
3. **Every guardrail ships with two probes** — one denied, one allowed.
4. **The always-loaded file has a ceiling**; measure it rather than discovering it by truncation.
5. **Instantiate in dependency order** — the store before the logging, the baseline before the diff.
