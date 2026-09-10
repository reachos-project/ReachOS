# 05 — Guardrails (defence-in-depth)

> **Scope.** This document describes the defence-in-depth **pattern** conceptually.
> It does not include real detection rules or executable skeletons — publishing detection
> signatures gives an attacker reconnaissance. Adapt the concept to your environment.

## Core idea

No single control is sufficient. Defence is built from **independent layers**: if one
fails or is bypassed, another catches it. The goal is for the joint probability of a
destructive action passing through all layers to be effectively zero.

## The three layers

```
Action proposed by the agent
        │
        ▼
[C1] Authorisation matcher    ── authorises/denies by static pattern (allow/deny)
        │  (passed)
        ▼
[C2] Content inspection       ── examines the command/file in depth before execution
        │  (passed)
        ▼
[C3] Backups + reversibility  ── even if something gets through, it is recoverable
        │
        ▼
   Execution
```

### C1 — Authorisation matcher (at the tool boundary)

A list of `allow`/`deny` rules evaluated statically against the requested action. Fast and
deterministic. **Important limitation:** it only intercepts at the coordinator→tool boundary.
Commands **embedded inside a script** do not pass through this matcher — they run as any
binary would. Hence the need for the subsequent layers.

### C2 — Content inspection (pre-execution)

A hook that receives the action before it occurs and examines it in depth:

- Extracts the command **robustly** (structured parsing, not a fragile regex that breaks on
  the first escaped quote).
- Detects destructive operations on critical paths, even when referenced indirectly
  (as an argument to another command).
- **Fail-safe:** if the analysis fails (malformed input), it blocks as a precaution (over-block)
  rather than letting the action through.
- Exit convention: code 0 = allow, code ≠ 0 = block, with the reason sent to the error channel
  (for the model/operator to see).

### C3 — Backups + reversibility

Before any operation capable of destroying critical configuration, a verifiable backup
(archive + hash manifest) is created and its integrity confirmed. The markdown source of truth
and an append-only activity history ensure that almost everything is reversible.

## Common guardrail patterns

| Guardrail | What it does |
|---|---|
| **Workspace enforcement** | An agent can only write in its workspace; writes outside it are denied and logged. |
| **Database read-only by default** | Destructive SQL operations (DELETE/DROP/etc.) are blocked; reads are free. |
| **URL verification** | Before recommending or contacting a URL, require several converging legitimacy signals. |
| **Secret protection** | Block the exposure or reading of credential files. |
| **Deny-by-default on critical paths** | Configuration/identity files are denied for writes by default, with an explicit, short maintenance window. |

## Know the residual of each layer — and write it where the control lives

The most dangerous document about a control is one that describes it as complete: whoever
reads it stops looking.

⭐ **Every layer has a residual. Establish yours, and record it in the file that implements
the control** — not in a ticket, not in a review that gets archived. In the artefact, where
the next reader arrives.

⛔ **Then keep that record internal.** The residual of *your* deployment is an operational
document, not a publishable one: it tells a reader what your controls do not reach, which is
useful to exactly one audience. Publish the mechanism and the discipline; keep the gap
analysis in the house.

⚠️ Two questions worth answering for any layer you build, in writing, for yourself:
*does this match the spelling of an action or its effect?* and *what happens when this control
itself fails — does it block, or does it let the action through?* A control whose failure mode
resembles success needs an independent liveness check (see `patterns/reciprocal-watchdog/`).

## Controls decay, and they do it quietly

⛔ **A control that asserts state starts lying the day the state changes**, and nothing about
it looks broken — the sentence still reads well.

Two habits keep this in check:

1. **Prefer discovery to declaration.** A hand-maintained list of what is watched drifts from
   what is actually watched; derive the list from the live configuration instead. A list that
   is derived cannot disagree with its subject.
2. **Ask the behaviour, not the inventory.** A hash proving a file has not changed does not
   prove the control still bites. Periodically fire something the control *should* catch, and
   confirm it does. A verifier is audited by its **silences**: if it never goes quiet in the
   nominal state, it will be ignored; if it never speaks, nobody knows whether it works.

## Principles

1. **Independent layers** — each fails differently; they do not share the same blind spot.
2. **Fail-safe / over-block** — when in doubt, block.
3. **Log everything** — every denial and every authorised exception goes to an auditable log.
4. **Never trust self-reported identity** of a caller for security decisions.
5. **The concrete rule is not public** — the *pattern* is shareable; the detection signatures are not.

## See also

- `patterns/defense-in-depth/` — the layer topology in engineering detail,
  and how to establish each layer's residual.
