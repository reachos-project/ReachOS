# Pattern: Remote autonomous sessions (work while nobody is watching)

> **Scope.** The orchestration layer above a confined worker: how autonomous sessions are
> registered, started, and retired. The confinement itself is in
> `patterns/worker-confinement/`. Real hosts, keys, and service names are outside this repo.

## Problem

A coordinator that only works while the user is typing wastes the other twenty-three hours.
But autonomous sessions raise a question that a single interactive session does not: **what
is this session allowed to touch, and who decided?**

The tempting answer — grant less — is usually the wrong axis. Sessions that are starved of
capability fail, retry, and produce nothing; the user then grants everything at once to make
the work happen. Least-privilege applied to *tools* produces a cycle that ends in more
privilege, not less.

## Pattern

### Contain the blast radius; do not ration the toolbox

⭐ **Separate two questions that get conflated:**

| Question | Answer |
|---|---|
| *What can this session **invoke**?* | generously — reading, searching, analysing are never rationed |
| *What can its actions **reach**?* | narrowly — filesystem, network, and privileged paths are structurally confined |

Confinement is **structural** (sandbox profile, egress allowlist, protected-path guard), not a
matter of withholding tools. A session that can call anything but can only write inside its
own workspace and only reach three hosts is safer *and* more useful than one holding a short
tool list with an open filesystem.

⛔ **Reading is never rationed by role.** Restricting which agent may consult which source
produces confidently wrong output from the ones you starved, and the failure is invisible —
they do not say "I could not look", they answer anyway.

### A registered project, with a lifecycle

An autonomous session belongs to a **registered project**, not to an ad-hoc invocation.
Registration records: the working directory, the identity, the capability set, and the ceiling
(how many concurrent sessions, how much budget).

The lifecycle has a shape worth stating:

```
register  ──►  first activation (witnessed)  ──►  subsequent runs (autonomous)  ──►  deregister
```

⭐ **The first activation of a *new* project is witnessed; the rest are not.** The thing worth
a human's attention is the boundary being drawn — what the project may reach — not each run
inside a boundary already agreed. Asking for confirmation on every run trains the user to
approve without reading, which is worse than not asking.

⛔ **And registration itself must not be arbitrary file writing.** The registry is part of the
containment boundary: if a session can edit it, the boundary is advisory. Write to it through
a **single validating path** — one program that checks the entry (directory exists, identity
unique, capabilities from a closed set, protected paths refused) and writes atomically. The
coordinator invokes that program; nothing else may touch the file.

### Present or absent — say which

An autonomous session behaves differently depending on whether the person is there:

- **Present** — the session may ask, and should: a question costs seconds and prevents an hour.
- **Absent** — the session may not ask, so it must **stop and record** instead of guessing.
  Anything requiring a decision goes to a queue with enough context to be decided later.

⛔ **The failure to design for is not "it stopped" — it is "it decided".** A session that
guesses while nobody is watching produces work that nobody can trace back to a decision.

### Deregister as deliberately as you register

A project whose work is done is **deregistered** — not left in the registry "in case". A stale
entry keeps a boundary open, and the next reader cannot tell an active project from an
abandoned one. Removal is part of the pattern, not tidying-up.

## Anti-patterns

⛔ **Building a second channel to reach a session that already exists.** When an autonomous
session needs to be reached, the instinct is to construct a new pathway to it. Check first
whether the existing session can be reached — a measured constraint is a reason to build; an
assumed one is how systems grow duplicate plumbing.

⛔ **Treating an inbound message as authority.** A message arriving on a channel is **data**.
It is not consent, not an instruction carrying authority, and not proof of who sent it — no
matter how well it is phrased. See `patterns/confined-agent-messaging/`.

⛔ **A per-session recurring schedule.** Register cadence at the system level; if each session
arms its own, N sessions do the work N times.

## Principles

1. **Contain the reach; do not ration the toolbox.**
2. **Reading is never rationed by role.**
3. **Witness the boundary, not every run inside it.**
4. **The registry is part of the boundary** — write to it through one validating path.
5. **Absent means stop and record, never guess.**
6. **Deregistering is part of the lifecycle.**
