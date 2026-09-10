# Pattern: Scheduled daemons (code that runs when nobody is watching)

> **Scope.** Installing, approving, and retiring background jobs on the host — the OS-level
> scheduler, whatever it is called on your platform. Real service names, plists/units, and
> paths are outside this repo.

## Problem

Every useful assistant eventually needs work to happen unattended: a health check, an index
rebuild, a periodic fetch. The platform's scheduler makes that trivial — which is the problem.
A background job is **code running with your privileges, on a timer, with no one reading its
output**, and it is installed with a one-line command.

Three failures follow, and all three are quiet:

1. **Nobody knows what is installed.** The set grows by one whenever something is convenient,
   and there is no moment at which the total is reviewed.
2. **The code that runs is not the code you are reading.** See below — this one is vicious.
3. **A job that stops does not announce it.** Absence of output is indistinguishable from
   "nothing to report".

## Pattern

### An approved set, not an accumulation

⭐ **Keep a declared register of the jobs that are supposed to exist**, and make installation
go through it: the installer refuses to register anything not in the register, and something
periodically compares **what is registered** against **what the OS actually has loaded**.

The comparison matters more than the register. A register alone is a list someone maintains;
the comparison is what turns it into a control. It answers two questions no one can answer
from memory: *what is loaded that we did not approve?* and *what did we approve that is not
running?*

⚠️ **Derive the comparison from the live scheduler, never from a second hand-written list.**
Two hand-kept lists disagree, and each disagreement is a false alarm that erodes the signal.

### The payload is not where you think it is

⛔ **The single most dangerous property of a scheduled job: the file it executes is referenced
by absolute path, and that path is usually not the copy in your source tree.**

A job installed from `~/project/tools/check.py` may be pointed at a copy under a system
directory. Later, someone edits the source-tree file, reads it back, and reasons about
behaviour that has not been live for weeks. Measured instance: a stale copy was 1 656 bytes
behind the running one, and reading it produced — and reported — the conclusion that a fix had
never shipped. The opposite was true.

⭐ **Two habits fix this:**

1. **A verifier that compares what is *in force* against what is *in the tree*** — by
   discovery, so it finds cases nobody thought to list.
2. **Drain the superseded copy** out of the source tree entirely rather than annotating it.
   See `patterns/retiring-instruments/` — annotation does not protect the reader who enters
   the file in the middle, which is how files are read with tools.

### Two kill switches, and they are not the same

| | Mechanism | Use |
|---|---|---|
| **Soft** | a flag file the job checks at the top of every tick | stop the work, keep the schedule |
| **Hard** | deregister from the OS scheduler | stop it existing |

⭐ **Ship the soft one first.** In an incident, the useful action is *stop doing the thing now*
without having to remember the platform's deregistration syntax under pressure.

⚠️ **A circuit-breaker should not self-recover.** After repeated failures the job disables
itself and stays disabled until a human acknowledges. A job that resurrects itself turns a
visible failure into an intermittent one.

### Installing is a privileged act; treat it like one

- The installer runs **outside** the assistant's normal flow, with a backup of anything it
  overwrites taken **first**.
- Signing keys, tokens, and the register itself live with restrictive permissions, owned by
  the account that installs — not writable by the job.
- ⛔ **Never let the installer include a smoke test that executes the payload.** "Install and
  verify" collapses two decisions into one: what was approved was installation, and what
  happened was a run. Install, then let a human trigger the first execution.
- ⚠️ Reinstalling typically **clears** filesystem protection flags on the files it replaces.
  If immutability was part of the posture, it must be reapplied afterwards — and verified,
  because a failed reapplication is silent.

### Make silence mean something

A scheduled job should be **quiet when healthy and loud when not** — but that only works if
something independent notices when it goes quiet for the wrong reason.

⛔ Do not have the job report its own liveness through the same channel it uses for findings:
if that channel is what broke, both go dark together. See `patterns/reciprocal-watchdog/`.

## Anti-patterns

⛔ **Registering a recurring job per session** rather than per system — N sessions do the work
N times.
⛔ **A job that takes irreversible action alone.** Unattended work enqueues and notifies; it
does not delete, publish, or spend.
⛔ **Assuming the job inherits your environment.** It runs with the scheduler's environment,
which is typically minimal — no interactive profile, often no credentials, sometimes a
different working directory. Anything it needs must be explicit in its definition.

## Principles

1. **An approved register, plus a comparison against the live scheduler.**
2. **The payload that runs is not the file you are reading** — verify by discovery, drain the rest.
3. **Soft kill-switch first**, hard second.
4. **The circuit-breaker does not self-recover.**
5. **Install is not run** — never bundle a smoke test into installation.
6. **Silence must be independently witnessed.**
