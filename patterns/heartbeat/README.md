# Pattern: Heartbeat — confined daemon with cost-based escalation

> **Scope.** Engineering of a periodic between-session watchdog daemon. Real sandbox profiles,
> notification channels, and paths are outside the repo. Fictional paths:
> `/opt/atlas/assistant/{queue,state,logs}`.

## Objective

A periodic and **confined** process that runs between interactive sessions, performs health
checks, and — when it finds something — escalates via the **cheapest path** that resolves it,
using a language model only when truly needed, and **never** acting irreversibly on its own.

## Cost-based escalation

```
Tier-0  Deterministic check (no model)
            │ needs judgement?
            ▼
Tier-1  Triage with a small LOCAL model (data-only, closed schema, fail-safe)
            │ needs a human decision / risky action?
            ▼
Tier-2  Queue + notify — never executes the risky action itself
```

- **Tier-0** resolves most cases (disk space, stuck queue, expiring certificate, stale files)
  without any model. Cheap and deterministic.
- **Tier-1** uses a small **local** model, restricted to data, with **closed-schema response**
  and fail-safe behaviour (marks "requires attention" when in doubt). Does not call the
  external network or execute commands.
- **Tier-2** **queues** the finding and **notifies**. The decision is deferred to the next
  interactive session or to a human.

## Idempotency under overlap

If two sessions (or two ticks) coincide, the same action must not run twice. The pattern is an
**atomic exclusive claim**:

```text
# PSEUDO-CODE
claim := "/opt/atlas/assistant/state/tick.claim"
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
| **Circuit-breaker** | On severe failure (repeated exceptions, burst, schema rejected by Tier-1) the daemon **disables itself and does not auto-recover** — it requires explicit human acknowledgement. Auto-recovering after a severe failure is how a system enters a damage loop. |
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

## Session-side consumption

At the start of an interactive session, the coordinator **drains the queue**: it reads the
structured records, moves each one to "processed" **atomically**, presents alerts to the user,
and reconciles the history. The daemon does **not** write to the transactional store — the
interactive session does the consolidation. This way the daemon never needs write privilege
over the authoritative state.

## Principles

1. **The cheapest that resolves** — deterministic → local → queue.
2. **Never acts irreversibly on its own.**
3. **Confined by design** — minimal FS and network; no subprocesses.
4. **Severe failure disables; does not auto-recover.**
5. **Observable** — append-only log + liveness file per tick.
