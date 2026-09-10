# Pattern: Confined worker with egress-allowlist

> **Scope.** Engineering of an isolated autonomous worker. Real host allowlists, keys, and
> installation runbooks are outside the repo. Fictional paths and hosts (`worker.example`,
> `api.halcyon-consulting.example`).

## Objective

Running autonomous tasks — potentially long-running, potentially from not fully trusted input
— **without** giving the worker free access to the system or the network. The worker is a box
with very narrow doors.

## Architecture

```
 Coordinator                                Confined worker
     │  enqueues task (signed)                     │
     ▼                                             │
 ┌────────┐   verifies signature      ┌────────────────────┐
 │ QUEUE  │ ────────────────────────► │ sandbox (minimal    │
 └────────┘                           │ FS/network, no exec)│
     ▲                                └─────────┬───────────┘
     │ result                                   │ all output
     │                                          ▼
     │                               ┌────────────────────┐
     └───────────────────────────────│ EGRESS-PROXY        │
                                     │ (closed allowlist)  │
                                     └────────────────────┘
```

## Components

| Component | Function |
|---|---|
| **Signed queue** | The coordinator enqueues tasks with a signature (e.g.: HMAC with shared key). The worker only executes messages with a **valid** signature — prevents work injection by anyone without the key. |
| **Worker sandbox** | Least-privilege profile: filesystem and network reduced to the task minimum; subprocess execution denied. |
| **Egress-proxy** | **All** outbound network traffic passes through a proxy with a **closed** host allowlist. Everything else is denied and logged. |
| **Quarantine** | Suspicious input/output is isolated in a quarantine area, not processed. |
| **Concurrency limits** | Explicit cap on simultaneous workers, with a **hard maximum** above which you do not go without a security review. |

## Message verification (concept)

```text
# PSEUDO-CODE — the concrete key and algorithm are installation configuration.
msg := dequeue()
if not verify_signature(msg.body, msg.sig, SHARED_KEY):   # SHARED_KEY never in the repo
    quarantine(msg); alert("invalid signature — possible injection")
else:
    run_confined(msg.body)
```

## Why an egress-allowlist (and not a denylist)

A **denylist** fails by **omission** — a new malicious host passes because no one listed it.
An **allowlist** fails **safe** — only what is explicitly permitted exits; everything else is
denied by default. Discovering the legitimate hosts: run the task once with a minimal allowlist
and **observe the denial log**, adding only genuinely necessary destinations.

## Installation and go-live

- **Backup** of critical paths **before** any OS configuration change.
- Working tree with restricted permissions; signing key with `600` permissions.
- **Prove the confinement with a witnessed test** by a security reviewer **before** go-live
  (do not rely on code review — require at least one real execution that demonstrates egress
  blocks and signature rejects).
- Changes to critical files / OS startup are done **outside** the automated flow, with prior
  backup.

## Principles

1. **Sign the work** — the worker only trusts signed messages.
2. **Egress by allowlist** — deny by default, permit by observed exception.
3. **Least privilege** — FS and network reduced to the strictly necessary; no subprocesses.
4. **Prove before trusting** — witnessed confinement test, with real execution.
5. **Secrets outside the repo** — real keys and allowlists are never version-controlled
   publicly.
