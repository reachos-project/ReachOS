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

| Request domain | Agent | Mode |
|---|---|---|
| Market analysis, strategy | `{{AGENT_SLUG_STRATEGY}}` | D |
| Report writing and editing | `{{AGENT_SLUG_EDITOR}}` | D |
| Knowledge curation, memory | `{{AGENT_SLUG_KNOWLEDGE}}` | D |
| Personal or politically sensitive advice | `{{AGENT_SLUG_ADVISORY}}` | P |

See an instantiated map at `examples/halcyon-consulting/routing-map.md`.

### Delegation by default (the `Mode` column)

A delegation map answers *which* agent. It does not answer *whether the coordinator
should ask first* — and if that is left implicit, the coordinator asks every time, the
user tires of confirming, and delegation quietly stops happening.

Make it explicit, per row:

- **`D` — delegate by default.** The user's permission for this class of request is
  already given. The coordinator delegates without asking, and reports afterwards.
- **`P` — on explicit request only.** Sensitive, personal, or politically loaded domains
  where the user decides case by case whether a specialist is involved at all.

**Carve-out — what stays with the coordinator even in a `D` row:**

1. system and infrastructure work, and the governance rules themselves;
2. Routes 1 and 2 (by definition, no agent);
3. any request whose ground truth exists **only in the current conversation** and has not
   been written to a file the delegate can read.

Point 3 is the one that bites. An agent cannot verify what it cannot open. Either the
context is materialised into an artefact first, or the work is not delegated — a delegate
reasoning from a summary produces confident output nobody can check.

> **Why this is worth a column rather than a paragraph.** Measured in one deployment: **half
> the domain agents had received zero delegations**, and the large majority of all agent
> invocations went to two infrastructure agents. The map was correct and unused. The missing
> information was never *which* agent — it was *may I, without asking*.

⛔ **The honest caveat, and it is about this repo's own premise.** That reading — the map was
right, the permission was missing — is the one we acted on. It is not the only one the data
supports. The alternative is that **the partition by domain did not match the shape of the
work**: that infrastructure and coordination were most of what there was to do, and that
specialists for domains nobody was working in went unused because there was nothing to send
them. `docs/00` opens by asserting that specialisation with coordination is the answer to a
saturating generalist session. **This measurement is the closest thing in this repo to a test
of that assertion, and it does not settle it.**

⭐ **The test exists and is cheap.** Every delegation returns real telemetry — duration, tokens,
tool counts, the model actually resolved (`docs/14-runtime-observed.md`). That is enough to ask
*is delegation paying for itself, per domain?* rather than assuming it. If, after the permission
problem is removed, a domain still receives nothing, the answer was never the mode: it is that
the domain was not a domain. **Measure it before adding the next agent.**

⚠️ **Irreversible and outward-facing acts stay gated regardless of mode.** `D` removes the
question "should I involve an agent"; it never removes the question "should this be done".

### The delegation mandate

Choosing the agent is the easy half. What arrives with the task decides whether the answer is
verifiable — and a delegation that omits any of these produces confident output nobody can
check.

Every mandate carries **six** things:

| | | |
|---|---|---|
| 1 | **The goal, and what "done" looks like** | not the topic — the decision the output must support |
| 2 | **Where the ground truth lives** | literal paths to the artefacts. If it is not written down, write it down first or do not delegate |
| 3 | **The declared unknowns** | what the coordinator does *not* know, said plainly, so the agent does not silently invent it |
| 4 | **The source hierarchy** | which levels are expected for this task (below) |
| 5 | **The return format** | inline **and** a proposed file path — a sub-agent's write can fail for reasons it cannot observe, so the inline return is the guarantee |
| 6 | **The out-of-scope line** | what not to touch, what not to decide, what to escalate instead |

⛔ **And verify the return by execution, never by confidence.** A report that says a script
passes is not a passing script. Run it, open the file, check the number against the source.

### Source hierarchy

Every agent works down this ladder, and skipping a rung means answering from a worse source
than the one that was available:

1. **The system's own memory** — semantic **and** verbatim search. This question may already
   have been decided, measured, or refuted here.
2. **The system's own artefacts** — dossiers, runbooks, prior deliverables, the store.
3. **Authoritative domain sources** — the regulator, the standards body, the official registry.
   Anything normative or with a date of effect.
4. **Scientific literature** — indexed databases and preprints, for empirical claims and
   anything that will be cited.
5. **The open web** — orientation and vendor documentation. Never the basis for a cited claim.

⛔ **Level 1 is executed, not recalled**, and its result is stated even when empty — "not
found" is a finding; "I don't think we have that" is a guess.
⛔ **Level 5 never answers a level-3 or level-4 question.** A web summary of a regulation is
not the regulation. If the authoritative source is unreachable, mark the claim unverified
rather than substituting quietly.

Full version, written where the agent actually reads it:
`templates/agents/agent.template.md` § *Source hierarchy*.

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
