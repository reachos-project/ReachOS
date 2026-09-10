# 12 — The OS sandbox (the layer below the rules)

> **Scope.** How an operating-system sandbox sits underneath the authorisation rules described
> in `docs/05-guardrails.md`, and the properties that surprise people. Real profiles, allowed
> hosts, and denied paths are outside this repo.

## Why this is a separate layer

`docs/05-guardrails.md` describes controls the assistant's runtime applies to **actions it is asked to
take**. This document is about the layer underneath: a sandbox enforced by the **operating
system**, which does not care what the runtime intended.

The distinction matters because the two fail differently. A rule can be bypassed by phrasing
a command differently. A kernel-enforced filesystem denial cannot — it does not read the
command, it refuses the syscall.

⭐ **Both are needed, and neither substitutes for the other.** The rule layer is expressive and
lexical; the sandbox is dumb and absolute.

## The shape of a profile

Two independent dimensions:

| | Typical shape | Note |
|---|---|---|
| **Filesystem** | reads: broad, with a **deny-list** of sensitive trees · writes: an **allow-list** of a few directories, with denies carved inside them | writes are the dangerous direction |
| **Network** | egress through a filtering proxy, with a **deny-list** of hosts, or an allow-list for confined workers | see `patterns/worker-confinement/` |

⛔ **Write allow-lists need deny-lists inside them.** "May write in this project directory"
almost always means "except the configuration, the hooks, and the credentials that also live
there". Nesting a deny inside an allow is the normal case, not an exception.

## Five properties that surprise people

**1. Deny wins, and it is inherited.** A denial on an ancestor directory beats an allow on a
descendant. To open a hole, you narrow the parent's deny — you do not add a broader allow
underneath it.

**2. Some changes are hot; others need a restart.** Read-denials may take effect immediately
while write-allowances need the process restarted, or the reverse. ⛔ **Never assume a policy
change is live because the file was saved.** Test the behaviour: attempt one thing that should
now be denied and one that should now be allowed. A configuration that was edited but not
loaded is indistinguishable from one that does not work.

**3. Removing a permission is not the same as forbidding it.** Under a permissive default,
deleting an entry from an allow-list does not block anything — it just stops explicitly
allowing it, and the permissive default takes over. **To block, write a deny.**

**4. The sandbox and the rule engine intercept at different points.** The rule engine sees the
command the assistant proposed. The sandbox sees every syscall, including from **inside
scripts**. This is why a destructive command embedded in a script escapes the rule layer
entirely — and why the sandbox is the only layer that catches it.

**5. A denied probe can make a gate fail open.** If a check needs to read something the
sandbox forbids, the check errors — and an error is not a denial. Any guard that consults a
resource must decide explicitly what an *unreadable* answer means, and the safe default is to
treat it as a failure to verify, never as a pass.

## What the sandbox does not give you

⛔ **It does not stop the assistant from being wrong.** It bounds the blast radius of
mistakes; it does not improve judgement.

⛔ **It does not protect against what it was configured to allow.** The interesting question is
never "is there a sandbox?" but "what is inside the allow-list, and who last checked?".

⛔ **File immutability flags are friction, not a barrier.** Marking critical files immutable is
useful — it converts an accidental overwrite into an error. But the command that clears the
flag runs from inside the same context as everything else. Treat such a flag as a speed bump
that produces a log entry, never as a control. ⚠️ And it has a failure mode of its own: an
application whose write fails because of a flag it does not know about often reports success
anyway, so the change silently does not happen.

⛔ **An immutable *directory* blocks creating files, not modifying existing ones** — the
opposite of most people's intuition, and a real source of half-applied changes.

## Testing a profile

⭐ **Every change to a sandbox profile ships with two probes: one that must be denied, and one
that must be allowed.**

A positive-only test proves nothing — a profile that allows everything passes it. A
negative-only test is passed by a profile that denies everything, including the work. Both, or
the change is unverified.

⚠️ **Run the probes as the constrained identity, not as yourself.** A test executed with more
privilege than the thing being tested measures the tester.

## Principles

1. **The sandbox is dumb and absolute**; the rule layer is expressive and lexical. Keep both.
2. **Deny wins and is inherited** — narrow the parent, do not widen the child.
3. **Removing an allow does not deny** — write the deny.
4. **Verify by behaviour after a restart**, never by the file having been saved.
5. **A denied probe is not a pass** — decide explicitly what unreadable means.
6. **Immutability flags are friction with a log**, not a barrier.
7. **Two probes per change** — one denied, one allowed, run as the constrained identity.
