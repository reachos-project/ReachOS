# 07 — Confined worker with egress allowlist

> **Scope.** Pattern for running autonomous work (a "worker") in isolation. Real host
> allowlists, keys, and installation runbooks are excluded from this repo.

## Objective

Execute autonomous tasks — potentially long-running, potentially from not fully trusted
input — without giving the worker free access to the system or the network. The worker is a
box with very narrow openings.

## Architecture

```
   Coordinator                          Confined worker
       │  enqueues task                       │
       ▼  (signed message)                    │
  ┌─────────┐   validates signature  ┌──────────────────┐
  │  QUEUE  │ ──────────────────────► │  sandbox (FS/net │
  └─────────┘                        │  minimal)         │
       ▲                             └────────┬──────────┘
       │ result                               │ outbound network
       │                                      ▼
       │                             ┌──────────────────┐
       └───────────────────────────  │  EGRESS-PROXY     │
                                     │  (closed allowlist│
                                     │   of hosts)       │
                                     └──────────────────┘
```

## Components

| Component | Function |
|---|---|
| **Signed queue** | The coordinator enqueues tasks with a signature (e.g., HMAC). The worker only executes messages with a valid signature — prevents work injection. |
| **Worker sandbox** | Profile that restricts filesystem and network to the minimum needed for the task. |
| **Egress-proxy** | All outbound network traffic passes through a proxy with a **closed allowlist** of hosts. Everything else is denied and logged. |
| **Quarantine** | Suspicious input or output is isolated in a quarantine area instead of being processed. |
| **Concurrency limits** | An explicit cap on simultaneous workers, with a hard maximum above which no scaling occurs without review. |

## Why egress-allowlist (and not denylist)

A *denylist* fails by omission — a new malicious host gets through. An **allowlist** fails
safe: only what is explicitly permitted leaves; everything else is denied by default. To
discover the legitimate hosts, run the task once with a minimal allowlist and observe the
denial log to add only the genuinely necessary destinations.

## Installation and go-live (concept)

- Backup critical paths **before** any OS configuration change.
- Create the working directory tree with restricted permissions; signing key with `600` permissions.
- Prove confinement with a test witnessed by a security reviewer before go-live.
- All changes to critical files or OS startup configuration are made outside the automated
  flow, with a prior backup.

## Principles

1. **Sign the work** — the worker trusts no message except signed ones.
2. **Egress by allowlist** — deny by default, allow by observed exception.
3. **Least privilege** — filesystem and network reduced to the strictly necessary.
4. **Prove before trusting** — witnessed confinement test before production.
