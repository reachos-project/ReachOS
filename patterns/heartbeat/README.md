# Pattern: Heartbeat — confined daemon with cost-based escalation

> **Scope.** Engineering of a periodic between-session watchdog daemon. Real sandbox profiles,
> notification channels, and paths are outside the repo. Fictional paths:
> `/opt/halcyon/assistant/{queue,state,logs}`.

## Objective

A periodic and **confined** process that runs between interactive sessions, performs health
checks, and — when it finds something — escalates via the **cheapest path** that resolves it,
using a language model only when truly needed, and **never** acting irreversibly on its own.

## Cost-based escalation

```
L0  Deterministic check (no model)
            │ needs judgement?
            ▼
L1  Triage with a small LOCAL model (data-only, closed schema, fail-safe)
            │ needs a human decision / risky action?
            ▼
L2  Queue + notify — never executes the risky action itself
```

- **L0** resolves most cases (disk space, stuck queue, expiring certificate, stale files)
  without any model. Cheap and deterministic.
- **L1** uses a small **local** model, restricted to data, with **closed-schema response**
  and fail-safe behaviour (marks "requires attention" when in doubt). Does not call the
  external network or execute commands.
- **L2** **queues** the finding and **notifies**. The decision is deferred to the next
  interactive session or to a human.

## Idempotency under overlap

If two sessions (or two ticks) coincide, the same action must not run twice. The pattern is an
**atomic exclusive claim**:

```text
# PSEUDO-CODE
claim := "/opt/halcyon/assistant/state/tick.claim"
if not atomic_create_exclusive(claim):   # O_CREAT|O_EXCL — fails if it already exists
    exit(0)                              # another tick is already handling it; exit clean
try:
    do_tick()
finally:
    release(claim)
```

Exclusive creation is the mutual exclusion primitive: whoever creates the file wins the tick;
the others exit without doing anything.

## Operational security

| Mechanism | Function |
|---|---|
| **Kill-switch soft** | A flag file causes the daemon to abort at the top of the tick. Reversible without privileges. |
| **Kill-switch hard** | Deregister the service from the OS boot manager. |
| **Circuit-breaker** | On severe failure (repeated exceptions, burst, schema rejected by L1) the daemon **disables itself and does not auto-recover** — it requires explicit human acknowledgement. Auto-recovering after a severe failure is how a system enters a damage loop. |
| **Secret scrubber (fail-closed)** | Writing to the queue removes secrets; if the scrubber fails, it **does not write** (fail-closed), rather than writing in plaintext. |
| **Liveness file** | Each tick updates a liveness file — the basis for the reciprocal watchdog (see `../reciprocal-watchdog/`). |

## Confinement

The daemon runs under a **least-privilege sandbox profile**:

- **Filesystem:** writes only to `{queue, state, logs}`; denied on critical paths.
- **Network:** egress only to the local model and notification channel — nothing else.
- **Processes:** subprocess execution denied.
- **Database:** read-only.

> The real sandbox profile block (the concrete deny/allow rules) is **not** part of this
> repo — it is trust-system topology. Only the *concept* of confinement is shared.

## The queue: one file per finding, moved rather than deleted

The queue is a directory of one-line JSON files, not a log to be parsed. Each finding is
written once, under an id the daemon generates, and is consumed by **renaming** it:

```
/opt/halcyon/assistant/queue/<id>.json      ← the daemon writes here
/opt/halcyon/assistant/processed/<id>.json  ← the session moves it here
```

```json
{"id": "2026-09-07T0300-disk", "tier": 0, "severity": "warn",
 "check": "disk_free", "finding": "state volume at 91% of capacity",
 "evidence": "df: 47G used of 52G", "action_hint": "prune archived exports"}
```

Seven fields, and each earns its place: `id` (unique, sortable, also the filename), `tier`
(which escalation level produced it), `severity`, `check` (which check, so recurrence is
countable), `finding` (one sentence for a human), `evidence` (the raw measurement, so the
session need not re-run it), `action_hint` (a suggestion, never an instruction).

⭐ **`rename` is the whole consumption protocol.** It is atomic on a single filesystem, so two
sessions draining at once cannot both claim the same finding — the loser's rename fails and it
moves on. Nothing is deleted, so a finding processed by mistake is still on disk. And a
non-empty `queue/` is, by itself, an honest measure of what has not been seen.

⛔ **Never consume by deleting, and never by marking a field inside the file.** Deleting loses
the audit trail; an in-place edit is not atomic and gives two drainers the same work.

## L1's closed schema

The local model at L1 is given data and must answer in exactly this shape — three fields,
no free text outside them:

```json
{"verdict": "ok | needs_attention", "reason": "<= 200 chars", "confidence": 0.0}
```

⭐ **The fail-safe rule is what makes the schema load-bearing:** anything that is not a valid
instance of it — malformed JSON, an unexpected key, a `verdict` outside the two allowed values,
a timeout — is treated as `needs_attention` and escalated to L2. A model that cannot answer
in the schema has not said "fine"; it has said nothing, and nothing is not reassurance.

⚠️ **Two verdict values, deliberately.** A third ("critical", "urgent") would put a judgement
call in the layer least able to make it. Severity is L0's business, from the check that
produced the finding; L1 decides only whether a human needs to look.

## Session-side consumption

At the start of an interactive session, the coordinator **drains the queue**: it reads the
structured records, renames each one into `processed/`, presents alerts to the user, and
reconciles the history. The daemon does **not** write to the transactional store — the
interactive session does the consolidation. This way the daemon never needs write privilege
over the authoritative state.

## Principles

1. **The cheapest that resolves** — deterministic → local → queue.
2. **Never acts irreversibly on its own.**
3. **Confined by design** — minimal FS and network; no subprocesses.
4. **Severe failure disables; does not auto-recover.**
5. **Observable** — append-only log + liveness file per tick.
6. **Consume by moving, never by deleting** — the rename is the claim and the audit trail at once.
7. **An answer outside the closed schema is an escalation**, never a pass.
