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

## Principles

1. **Independent layers** — each fails differently; they do not share the same blind spot.
2. **Fail-safe / over-block** — when in doubt, block.
3. **Log everything** — every denial and every authorised exception goes to an auditable log.
4. **Never trust self-reported identity** of a caller for security decisions.
5. **The concrete rule is not public** — the *pattern* is shareable; the detection signatures are not.
