# 01 — Orchestration

The coordinator is governed by a small set of golden rules. They are intentionally
few and stable — complexity lives in the agents, not in the coordinator.

## Rule 1 — Total delegation

The coordinator **never** does operational work directly. It always delegates to the
appropriate specialist agent. The only exception: configuration micro-tasks (< 5 min)
in the system's own files.

> *Why:* concentrating execution in the coordinator re-saturates the context and erases specialisation.

## Rule 2 — Chain of command

The flow of any request is always the same:

```
User → Coordinator → Agent → Coordinator → User
```

No agent communicates directly with the user. All communication passes through the coordinator,
which performs the final synthesis. This guarantees a single point of coherence and quality control.

## Rule 3 — Traceability

Every task, delegation, and deliverable is logged in a transactional store (see
`examples/db/schema.example.sql`). The user can query the history at any time.
The minimum log per task:

1. Create the task upon receiving the request.
2. Log each delegation between agents.
3. Update the task on completion (status + result summary).
4. Log the deliverable when a file is delivered.

## Rule 4 — Quality gate

Before delivering any output, the coordinator runs a quality checklist
(`docs/04-quality-gate.md`). If the deliverable does not pass, it does not go out. The gate
result is logged to enable longitudinal quality metrics.

## Rule 5 — Privacy and security

Respect user privacy. Never expose sensitive data. Agents only write in their designated
workspaces; any write outside that is blocked by a guardrail (`docs/05`).

## Rule 6 — Pre-change validation (for critical config)

Before applying any change to critical configuration files ("Tier-1"), run a
*dry-run* that validates the change's assumptions:

- Do the items to **remove** actually exist in the current state?
- Are the items to **add** already there (redundant change)?
- Does the assumed structure still hold?

If there is a divergence between the assumed state and the real one, **stop** and re-evaluate
before applying. This prevents regressions caused by changes designed against stale state.

## Rule 7 — Backup before destructive operations

Before running any process capable of deleting, moving, or truncating critical configuration
files, create a **verifiable backup** (archive + hash manifest) and confirm backup integrity
**before** proceeding. Read and semantically inspect any script that touches those paths —
syntax validation is not enough.

> *Why:* a destructive command embedded in a script does not pass through the authorisation
> layer that only intercepts at the coordinator→tool boundary. Without a backup, the loss is
> irreversible.

## Hiring new agents (pipeline)

When a domain is needed that no existing agent covers:

1. **Skills research** — an agent investigates the ideal profile and produces a report.
2. **Persona design** — another agent designs the identity and writes the agent file.
3. **Confirmation** — the coordinator registers the new agent and updates the roster.

See the template at `templates/agents/agent.template.md`.
