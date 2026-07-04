# 00 — Overview

## The problem

A single generalist assistant session degrades when it tries to be everything at once:
context saturates, tone drifts, and there is no separation of concerns. The answer is
**specialisation with coordination** — many focused agents, one coordinator that orchestrates them.

## The model

```
                    ┌─────────────────┐
        User   ───► │   COORDINATOR   │ ───► User
                    │  (virtual CEO)  │
                    └───────┬─────────┘
                            │ delegates
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Agent A  │  │ Agent B  │  │ Agent C  │
        │ (domain) │  │ (domain) │  │ (domain) │
        └──────────┘  └──────────┘  └──────────┘
```

The coordinator:
- **Interprets** the request and classifies it into a route (`docs/02`).
- **Delegates** to the appropriate agent (or several, in parallel).
- **Synthesises** the results into a coherent response.
- **Never** does operational work — the only exception is minor configuration micro-edits.

Each agent:
- Has a **persona** (identity, expertise, style, constraints) defined in its own file.
- Operates only within its designated **workspace**.
- Returns the result to the coordinator — **never** communicates directly with the user.

## The five pillars

| Pillar | Document | Core concept |
|---|---|---|
| Orchestration | `01-orchestration.md` | Governance rules for the coordinator. |
| Routing | `02-smart-routing.md` | 5 routes to classify any request. |
| Memory | `03-memory-3tier.md` | 3-tier persistence, markdown as SoT. |
| Quality gate | `04-quality-gate.md` | Blocking checklist before delivery. |
| Security | `05-guardrails.md` · `06-heartbeat.md` · `07-worker-confinement.md` | Defence-in-depth + confined automation. |
| Data governance | `08-control-via-audit.md` | Free, auditable, and reversible writes. |

## Cross-cutting principles

1. **Traceability.** Every task, delegation, and deliverable is logged. The history is queryable.
2. **Separation of concerns.** One agent = one domain. The coordinator does not invade domains.
3. **Explicit source of truth.** Human-readable files are authoritative; indexes are derived.
4. **Fail-safe.** When in doubt, controls block (over-block) rather than let things through.
5. **Reversibility.** Prefer free writes + audit over prior approval that stalls the flow.

## How to read this repo

Start with `01` and `02` (the orchestration core), then `03` (memory) and `04` (quality).
Documents `05`–`07` describe the security posture **conceptually** — implementation skeletons
are deliberately excluded from this repo. Instantiate the `templates/` with the help of the
example in `examples/atlas-consulting/`.
