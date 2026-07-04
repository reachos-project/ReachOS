# Pattern: Reciprocal watchdog (who watches the watcher)

> **Scope.** Engineering the "who watches the watchman" problem. Real alarm channels and
> machine identities are outside the repo.

## Problem

A watchdog daemon that dies **silently** is worse than having no daemon at all: it gives a
false sense of coverage. A confined process can be killed by the OS, enter a circuit-breaker,
or become stuck without writing. An independent signal is needed that detects the **absence**
of the watchdog.

## Pattern

Two **independent** liveness signals, and an alarm that lives **outside** the system being
watched:

```
 Watched daemon  ──► updates a liveness file on every tick
                                  │
      ┌───────────────────────────┘
      ▼
 Watchdog  ──► reads the age of the liveness file
      │   is it stale (not updated for > N)?
      ▼
 Pushes STALE / DEAD to an alarm channel INDEPENDENT of the watched daemon
```

Design rules:

- **Independence.** The watchdog cannot share the fate of what it watches. If both die from
  the same cause (same process, same cron, same sandbox), there is no real oversight.
- **State outside the watched TCB.** The liveness state the watchdog consults lives **outside**
  the trust system being watched — otherwise compromising the target compromises the observer.
- **Push, not pull.** The watchdog **pushes** the alarm to a channel the operator sees even
  with the rest of the system down — it does not wait for someone to **pull** the state.
- **Dumb and external alarm.** The final layer is a simple, external, and well-tested alarm —
  not another intelligent component that can also fail.

## The infinite regress, and where to stop

"Who watches the watchdog?" is an infinite regress. It is not solved by another intelligent
layer — it is solved by making the **final** layer an **external, dumb, and trivially
verifiable** alarm (e.g.: a third-party notification service that fires if it does not receive
a periodic signal). Reliability comes from simplicity and externalness, not from more logic.

## Principles

1. **Detect absence, not just errors** — silence is the dangerous failure mode.
2. **Fate independence** — watcher and watched cannot die together.
3. **Observer state outside the watched TCB.**
4. **Push to a channel that survives the system going down.**
5. **The final layer is external, dumb, and tested** — that is where the regress stops.
