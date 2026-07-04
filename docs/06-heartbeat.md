# 06 — Heartbeat (confined daemon with cost-based escalation)

> **Scope.** Describes the **pattern** of a periodic watchdog daemon. Real confinement
> profiles (sandbox), notification channels, and paths are excluded from this repo.

## Objective

A periodic, **confined** process that performs system health checks between sessions and,
when it finds something, escalates via the cheapest path possible — only using a language
model when strictly necessary, and never taking irreversible action on its own.

## Cost-based escalation (tiers)

```
Tier-0  Deterministic check (no LLM)
            │  found something that needs judgement?
            ▼
Tier-1  Triage with a small local model (data-only, closed schema, fail-safe)
            │  needs human action/decision?
            ▼
Tier-2  Enqueue for the next session + notify
```

- **Tier-0** resolves the majority of cases without any model — it is cheap and deterministic.
- **Tier-1** uses a small **local** model, restricted to data, with a closed-schema response
  and *fail-safe* behaviour (when in doubt, marks as "requires attention").
- **Tier-2** never executes risky actions: it **enqueues** what it found and **notifies**. The
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

## Principles

1. **The cheapest thing that resolves it** — deterministic before local, local before enqueueing.
2. **Never takes irreversible action alone** — risky action is always deferred to a human.
3. **Confined by design** — least possible privilege; minimal network and filesystem.
4. **Observable** — append-only log as the daemon's source of truth; liveness file per tick.
