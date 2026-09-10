# 11 — Persistent sessions and where the work actually runs

> **Scope.** The host-side pattern for running a long-lived assistant that survives
> disconnection and is reached from more than one device. Real hostnames, paths, and access
> topology are outside this repo.

## Problem

An assistant that lives inside a terminal window dies with the window. Close the laptop, lose
the connection, switch rooms — and the session, its context, and anything mid-flight are gone.
The obvious fix is a terminal multiplexer, and it works. What is not obvious is what the fix
**breaks**.

## Pattern: one host, many surfaces

Run a **persistent multiplexer server on the machine that does the work**. Every client —
local terminal, remote shell from another device, an editor's terminal pane — attaches to the
*same* server. Detaching leaves everything running.

⭐ **The consequence worth stating explicitly: two axes that people conflate.**

| Axis | Varies? | What it decides |
|---|---|---|
| **Execution host** | **No** — always the machine running the server | which shell, which paths, which tools exist |
| **Presentation surface** | **Yes** — wherever the person is sitting | what "open this", "print this", "copy this" mean |

Almost every confusion in a multi-device setup comes from treating these as one thing. The
assistant's commands always run on the execution host. Only actions that reach the *person* —
opening a file, printing, the clipboard, a path they will click — depend on the surface.

⭐ **So do not ask about the surface at start-up.** Assume the last one signalled, and ask only
at the moment an action actually depends on it. A question at every session start, answered
identically every time, is friction that teaches the person to answer without reading.

## The trap: environment variables freeze

⛔ **Do not detect the execution environment by inspecting session variables.**

Connection variables, terminal identifiers, and the like are captured **when the multiplexer
server started** and inherited by every shell it spawns afterwards. If the server was started
locally and you attach over a remote connection a week later, the variables still describe the
local start-up. They are not stale by seconds — they are stale by however long the server has
been up, and they are **confidently** wrong.

⭐ **Prefer a stated default plus a cheap correction** over an inference that cannot fail
loudly. "Assume A; the person says otherwise when it matters" is more honest, and recovers in
one sentence.

⚠️ The same freezing applies to anything else read from the process environment: a value
exported after the server started is invisible to processes it spawned. Restarting the shell
is not enough — the **server** carries the snapshot.

## Configuration vaults: the same assistant, two configs

A common shell setup switches the assistant's configuration directory depending on how the
session was entered — one vault when local, another when remote. It is a reasonable idea, and
it has a sharp edge: **the branch is evaluated once, at shell start-up**, by the same frozen
variables described above. Under a persistent server started locally, the remote branch never
fires, and a person attaching remotely is silently using the local vault.

⛔ **Operational consequence: apply configuration and permission changes to *both* vaults.**
Otherwise a change "applied" is live on one entry path and absent on the other, and which one
you get depends on how the server happened to be started days earlier.
See [`templates/settings.sync.md`](../templates/settings.sync.md) for what has to be identical.

## Permission mode is configuration, not session state

The mode that decides what the assistant may run unattended (an "auto" mode, an allow/deny
list, a sandbox profile) must come from **files in the vault**, never from anything the
session inferred at start-up. Three consequences, each learned the hard way:

- **The mode lives in both vaults, identical**, so it does not depend on which entry path the
  multiplexer happened to take. A mode present in one vault and absent in the other is a
  coin flip, and the coin was tossed when the server started.
- **Under an allow-unless-blocked mode, removing an `allow` entry blocks nothing.** Unlisted
  commands run anyway; only a `deny` blocks. Hooks written for the older "allow-listed only"
  semantics must be **deny-only** — a hook that emits `allow` is redundant at best and, at
  worst, short-circuits the judgement layer for everything it matches.
- **The processed configuration is not the source file.** The runtime may merge, rewrite, or
  cache what it reads. Verify a permission change by *behaviour* (one command that should be
  blocked is blocked, one that should pass passes) after a restart — not by reading the file
  back.

## Surface-dependent actions — the table, so nobody re-derives it

The execution host never changes; only the handful of actions that reach the person do.
Keep one table per installation and read from it instead of guessing:

| Action reaching the person | Surface = the host itself | Surface = a remote client (other OS) |
|---|---|---|
| Open a file or a browser page | host's `open`-equivalent | the client OS's action, or a path the person can click |
| Print | host shortcut | client shortcut |
| Clipboard | host clipboard tool | client clipboard tool |
| A synced-folder path for the person to open | host-side mount path | client-side mount path of the **same** file |

⭐ The synced file is one file; only the *spelling of its path* differs by surface. The
assistant reads and writes it by the host path always, and translates only when the
destination is the person's screen.

## The one exception: the host is offline

If the execution host is down there is no server to attach to, and execution — not just
presentation — moves to whatever machine the person is on. This is **signalled explicitly by
the person**, never inferred, and it flips the whole table above (paths, shell, tools). Treat
it as a named mode with its own checklist, not as a degraded version of the normal one.

## Surviving a crash

Two complementary records, and they capture different things:

| | Written by | Captures |
|---|---|---|
| **Passive snapshot** | a hook, every N tool calls, automatically | what was *done* — survives an abrupt death |
| **Iteration log** | the assistant, at meaningful turns | what was *intended* — why, what failed, what is pending |

⭐ **Keep both.** The passive one costs nothing and is complete but shallow; the deliberate one
is sparse but carries reasoning. After an abrupt end, read the deliberate log first and
cross-check it against the passive one for whatever happened after the last entry.

⚠️ **Mark the iteration log as active on the active shelf** (`templates/ACTIVE.template.md`),
so a resumed session reads it *before* touching that domain — and remove the mark when the
iteration closes. The shelf, not the memory index: the two have opposite lifecycles (`docs/10`).
A permanent marker is noise; an absent one is a lost thread.

## Principles

1. **One execution host, many presentation surfaces** — never conflate them.
2. **Never infer the environment from variables a persistent server has frozen.**
3. **Ask about the surface at the moment it matters**, not at start-up.
4. **Apply config changes to every vault the entry paths can select.**
5. **Permission mode is configuration in both vaults** — verified by behaviour after restart;
   under allow-unless-blocked, only `deny` blocks and hooks are deny-only.
6. **One surface table per installation**; the host path is canonical, translation is for
   the person's screen only.
7. **Host offline is a named mode the person declares**, not an inference.
8. **Two crash records** — one automatic and shallow, one deliberate and reasoned.
