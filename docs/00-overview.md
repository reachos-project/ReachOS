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
- **Interprets** the request and classifies it into a route (`docs/02-smart-routing.md`).
- **Delegates** to the appropriate agent (or several, in parallel).
- **Synthesises** the results into a coherent response.
- **Never** does operational work — the only exception is minor configuration micro-edits.

Each agent:
- Has a **persona** (identity, expertise, style, constraints) defined in its own file.
- Operates only within its designated **workspace**.
- Returns the result to the coordinator — **never** communicates directly with the user.

## The pillars

| Pillar | Document | Core concept |
|---|---|---|
| Orchestration | `01-orchestration.md` | Governance rules for the coordinator. |
| Routing | `02-smart-routing.md` | 5 routes to classify any request, and who may be delegated to without asking. |
| Memory | `03-memory-3tier.md` | 3-tier persistence, markdown as SoT. |
| Quality gate | `04-quality-gate.md` | Blocking checklist before delivery. |
| Security | `05-guardrails.md` · `06-heartbeat.md` · `07-worker-confinement.md` | Defence-in-depth + confined automation. |
| Data governance | `08-control-via-audit.md` | Free, auditable, and reversible writes. |
| Provenance | `patterns/provenance-and-dating/` | How a note records what it knows, and since when. |
| Instrument lifecycle | `patterns/retiring-instruments/` | Decommissioning without leaving a trap behind. |
| Time | `09-clocks-and-routines.md` | Clocks die when answered; routines recur. State in the store, not in prose. |
| Session lifecycle | `10-session-lifecycle.md` | Opening, closing, and the narrative log of the working relationship. |
| Review culture | `patterns/adversarial-review/` | Keeping an advisor from serving the framing it was given. |
| Autonomous sessions | `patterns/remote-autonomous-sessions/` | Registering, running, and retiring work that happens unattended. |
| Host substrate | `11-persistent-sessions.md` · `12-os-sandbox.md` | Where the work actually runs: persistent sessions, and the OS sandbox under the rule layer. |
| Scheduled daemons | `patterns/scheduled-daemons/` | Installing, approving and retiring background jobs — and finding the payload that actually runs. |
| Runtime substrate | `13-runtime-requirements.md` | The six host capabilities everything above assumes, and the order to instantiate them in. |
| Runtime behaviour | `14-runtime-observed.md` | Field notes: how one such host actually behaves, measured from its own transcripts. Dated, version-bound, and not a vendor statement. |
| Verification | `15-verification.md` | Probes that can fail; reading a verifier's output, not its return code; auditing it by its silences. |
| Decision discipline | `patterns/decision-questions/` | Six questions carried into every recommendation mandate; question 0 is executed and is the gate. |
| Cross-lineage review | `patterns/cross-lineage-red-team/` | A bounded dialogue with a model of another lineage when the coordinator is an interested party. |
| Learning from outside | `patterns/external-practice-radar/` | A funnel from a daily scout to a weekly human adoption decision, with integrity carried downstream. |
| Documentation that stays true | `patterns/domain-manuals/` | One manual per domain holds the paths; everything else refers to it by section name. |

**Before any of it, in this order:** `13-runtime-requirements.md` — whether your host can
carry this at all — then `templates/onboarding-interview.md`, the first-run interview that
tells the system who it is working for. Skipping the second is the difference between an
architecture and an assistant; skipping the first is building on an assumption.

## Cross-cutting principles

1. **Traceability.** Every task, delegation, and deliverable is logged. The history is queryable.
2. **Separation of concerns.** One agent = one domain. The coordinator does not invade domains.
3. **Explicit source of truth, split by kind.** Human-readable files are authoritative for
   **knowledge and reasoning**; the transactional store is authoritative for **state** — clocks,
   routines, tasks, deliverables (`docs/09-clocks-and-routines.md`). Indexes are derived from
   either and are never authoritative for anything.
4. **Fail-safe.** When in doubt, controls block (over-block) rather than let things through.
5. **Reversibility.** Prefer free writes + audit over prior approval that stalls the flow.

## How to read this repo

After those two, start with `01` and `02` (the orchestration core), then `03` (memory) and
`04` (quality), and `15` (verification) — the verb the other chapters use without defining.
Documents `05`–`07` describe the security posture **conceptually** — runnable implementations
are deliberately excluded from this repo. Instantiate the `templates/` with the help of the
example in `examples/halcyon-consulting/`.
