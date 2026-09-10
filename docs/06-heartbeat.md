# 06 — Heartbeat (confined daemon with cost-based escalation)

> **Scope.** Describes the **pattern** of a periodic watchdog daemon. Real confinement
> profiles (sandbox), notification channels, and paths are excluded from this repo.

## Objective

A periodic, **confined** process that performs system health checks between sessions and,
when it finds something, escalates via the cheapest path possible — only using a language
model when strictly necessary, and never taking irreversible action on its own.

## Cost-based escalation (tiers)

```
L0  Deterministic check (no LLM)
            │  found something that needs judgement?
            ▼
L1  Triage with a small local model (data-only, closed schema, fail-safe)
            │  needs human action/decision?
            ▼
L2  Enqueue for the next session + notify
```

- **L0** resolves the majority of cases without any model — it is cheap and deterministic.
- **L1** uses a small **local** model, restricted to data, with a closed-schema response
  and *fail-safe* behaviour (when in doubt, marks as "requires attention").
- **L2** never executes risky actions: it **enqueues** what it found and **notifies**. The
  decision is left to a human or to the next interactive session.

## Confinement

The daemon runs under a **sandbox profile** that restricts:

- **Filesystem:** writes only to `{queue, state, logs}`; denied to critical paths.
- **Network:** egress only to the local model and the notification channel — nothing else.
- **Processes:** subprocess execution denied.
- **Database:** read-only access.

## Operational security

| Mechanism | Function |
|---|---|
| **Soft kill-switch** | A flag file (`DISABLED`) makes the daemon abort at the top of the tick. |
| **Hard kill-switch** | Deregister the service from the OS boot manager. |
| **Circuit-breaker** | On serious failure (repeated exceptions, burst, rejected schema) the daemon disables itself and **does not self-recover** — requires human acknowledgement. |
| **Idempotency** | Exclusive claims (atomic creation) prevent running the same action twice if there is an overlap. |
| **Secret scrubber** | Queue writes remove secrets in a *fail-closed* manner. |

## Session-side consumption

At the start of an interactive session, the coordinator drains the queue: reads the structured
records, moves each one to "processed" (atomically), presents the alerts to the user, and
reconciles the history. The daemon does **not** write directly to the transactional store —
the interactive session consolidates.

## Scheduled routines: reminded is not done

⚠️ **This section states the failure; `docs/09-clocks-and-routines.md` is where the doctrine
lives.** Read that one for the full treatment — how clocks and routines differ, where their
state belongs, **how far a routine may go on its own**, and what happens to the verdict of a
routine that proposes but may not write. What follows here is only the part the daemon needs.

Once the daemon also carries **periodic routines** — things that should happen weekly, or
every N days — a second question appears, and it is easy to answer wrongly: *did this
routine actually run?*

⛔ **The obvious implementation measures the wrong event.** If "last fired" is read from the
notification record, it records that the routine was **enqueued**, not that anything was
**done**. A routine can be reminded every week for two months and executed zero times, and
the dashboard stays green throughout. Measured here: 10 of 18 routines had no record of
completion at all, and one had been enqueued six times and carried out none.

Two separate facts, two separate fields:

| Field | Written by | Means |
|---|---|---|
| `reminded_at` | the daemon, when it enqueues | the reminder was produced |
| `completed_at` | the session, when the work is done | the work happened |

⭐ **Declare, per routine, what constitutes completion** — the concrete action whose presence
in the activity log proves the routine ran. Then have something *read* that declaration.

⚠️ **And check that the reader exists.** In this deployment the per-routine "completion
action" field was already defined in the configuration, and nothing ever read it: the
startup code loaded only the notification file. The gap was not a missing field — it was a
**missing reader for a field that was already there**. Before designing a new mechanism,
grep for the one you may already have shipped.

⚠️ **A "missed" count is only meaningful inside the window where the routine was alive.**
Periods before its first successful run are not failures, and counting them produces an
alarm that is wrong on day one — which teaches everyone to ignore it.

## Principles

1. **The cheapest thing that resolves it** — deterministic before local, local before enqueueing.
2. **Never takes irreversible action alone** — risky action is always deferred to a human.
3. **Confined by design** — least possible privilege; minimal network and filesystem.
4. **Observable** — append-only log as the daemon's source of truth; liveness file per tick.
