# 02 — Smart routing (5 routes)

The coordinator classifies **every** request into one of five routes. Classification is
automatic and based on complexity, task type, and available agents.

## Route 1 — Direct (no agent)

**When:** questions about system state, task status, simple approvals, anything the coordinator
answers with information it already has.
**Action:** immediate response, no delegation.
**Examples:** *"How many agents do we have?"* · *"What is the status of task 3?"* · *"Approved."*

## Route 2 — Micro-edit (coordinator executes)

**When:** simple edits to system configuration files, < 5 min, no research or content creation.
**Action:** the coordinator executes directly with read + edit.
**Examples:** *"Fix this typo in the rules file."* · *"Add this entry to the roster."*

## Route 3 — Single-agent

**When:** the domain clearly matches an existing agent; single, clear deliverable.
**Action:** the coordinator delegates to the appropriate agent and logs the task.

Each organisation maintains a **delegation map** — domain → agent. Generic example:

| Request domain | Agent |
|---|---|
| Market analysis, strategy | `{{AGENT_SLUG_STRATEGY}}` |
| Report writing and editing | `{{AGENT_SLUG_EDITOR}}` |
| Knowledge curation, memory | `{{AGENT_SLUG_KNOWLEDGE}}` |

See an instantiated map at `examples/atlas-consulting/routing-map.md`.

## Route 4 — Pipeline (hiring)

**When:** the request requires a domain that no agent covers.
**Action:** hiring pipeline (skills research → persona design → confirmation),
described in `docs/01-orchestration.md`.

## Route 5 — Parallel

**When:** the request has several independent sub-tasks, each for a different agent.
**Action:** decompose, launch agents simultaneously, synthesise at the end.
**Example:** *"Analyse market X **and** prepare material on topic Y"* → two agents in parallel.

## Fallback rules

1. **Ambiguous domain** — fits more than one agent → ask the user to clarify.
2. **Non-existent agent** — activate Route 4 (hiring).
3. **Request too vague** — ask for the desired outcome before delegating.
4. **Agent error** — retry once with refined instructions; if it fails, escalate to the user.

## "quality-sensitive" flag

For visual deliverables, for third parties, or for publication, apply a stricter quality gate
and suggest human review before finalising (see `docs/04-quality-gate.md`).

## Decision diagram

```
Request
  ├─ Answerable from existing info? ──────────────────► Route 1
  ├─ Micro-edit to config (< 5 min)? ─────────────────► Route 2
  ├─ Clear domain + agent exists? ─────────────────────► Route 3
  ├─ Requires an agent that does not exist? ───────────► Route 4
  └─ Multiple independent sub-tasks? ──────────────────► Route 5
```
