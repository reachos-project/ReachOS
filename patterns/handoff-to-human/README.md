# Pattern: Handing an action back to the human

> **Scope.** What to do when the assistant cannot perform an action and a person must run it.
> Real paths, credentials, and terminal setups are outside this repo.

## Problem

Some actions are structurally outside the assistant's reach: they need an interactive login, a
credential it must never hold, a UI, elevated privileges, or a decision that is not its to
make. The work then crosses a boundary — from something the assistant *does* to something a
person **executes on its behalf**.

That crossing is where the failures cluster, and none of them are about the action itself:
- the person pastes a command that **breaks on the way in**;
- they run it and nobody records that it ran;
- they get eleven commands and run nine;
- the assistant, wanting to be helpful, makes the sequence long enough that following it is
  its own project.

⭐ **A handoff is a deliverable.** It has a reader, a failure mode, and a quality bar — and it
is usually written as an afterthought.

## Pattern

### One artefact, not a conversation

⛔ **Anything longer than a couple of short lines goes in a file the person opens and runs** —
not pasted into chat.

The reason is mechanical: a terminal wraps a long line, and a wrapped line pasted back in
carries **real newlines**. What arrives is not what was written, and the error it produces is
about syntax rather than about the actual problem. Roughly seventy characters is where this
starts biting; treat it as the ceiling for anything meant to be copied.

⚠️ **The same applies to explanatory text mixed into a command block.** Comment markers,
exclamation marks, backticks and quotes each mean something to a shell. Keep prose **outside**
the block, and let the block contain only what should execute.

### Write it as if it will be run once, at midnight, by someone tired

- **Idempotent.** Running it twice must be safe. The person will not be sure it worked.
- **Validates before acting.** Check that the thing to change is in the state assumed. If
  not, stop with a clear message rather than proceeding on a wrong premise.
- **Checks its own return codes.** A step that fails silently mid-script leaves the system in
  a state nobody described.
- **Backs up first**, verifiably, if anything is overwritten or removed.
- **Writes a log.** ⛔ This is the one that gets skipped, and it is the one that matters
  afterwards: without it, "did you run it?" has no answer but memory. The log is the artefact
  that lets the assistant pick the thread back up.
- **Says what it did** in its final lines, in plain language.

### Batch the crossings

⛔ **Do not hand over a sequence of separate scripts to be run one at a time.** Each crossing
costs the person a context switch, and by the third they are approving without reading —
which is worse than not asking at all.

⭐ **Group the crossings that belong to the same decision into one artefact**, and make it
report at the end. If two changes are co-dependent, they cross together or the intermediate
state is one nobody designed.

### Tell them what it costs, before they start

State up front: how long, what it touches, whether it is reversible, and what happens if they
stop halfway. Someone who knows a step takes twenty minutes will not abandon it at minute
fifteen.

### When the handoff is a protected change

The hardest handoff is a script that changes something protected — configuration, rules, the
guards themselves — and runs in the person's own terminal. There, **none of the assistant's
controls run**, and none of its rules are read. So what the assistant controls is not the run;
it is the **delivery**. Three things travel with the script, and the person decides on them:

1. **The checksum of the script as delivered**, so that what runs is what was checked.
2. **The checker's output, verbatim** — the state by its full name and every list it printed.
   Not a summary: a list the assistant summarised is no longer the list the person decides on.
3. **Where the backup is, the result of verifying it, and the command to repeat that
   verification.** A backup obligation cannot be verified from the script, since the backup is
   not an input to any check of the script. From the delivery, it can.

⛔ **What does not travel with it is an opinion that it "can run".** If the check disclosed
destructive operations, the decision is the person's; if it came back clean, the check was
lexical and says nothing about behaviour.

⚠️ **Name what the delivery does not catch, instead of implying that it does.** A guard that
can never fire — a status captured after a pipe, a condition that is always false — survives
all three items above. The only act that catches it is a **complete reading** of the script by
the assistant before delivery, and that reading is not delegated to a pattern search. The
specifics for protected applies are in `patterns/apply-preflight/` § "What travels with the
script to the person".

## The other direction: know what you can actually do

⛔ **The mirror-image failure is handing over work that did not need handing over.**

Before declaring something out of reach, check. "Let me confirm whether I can" and "I can't"
are different sentences, and the second one, said wrongly, quietly moves work onto the person
who delegated it precisely to avoid that.

⭐ **Keep a written record of what the assistant can and cannot do** — capabilities, and the
limits actually measured rather than assumed. Consult it before declining. An unverified
"can't" is a claim about the world, and claims about the world get checked
(`docs/01-orchestration.md`, question 0).

⚠️ **A denied attempt is information, not a verdict.** It may be the sandbox, a missing
capability, or the wrong path — each with a different remedy, and only one of them is "a human
must do this".

## Principles

1. **A handoff is a deliverable** — it has a reader and a quality bar.
2. **Long instructions live in a file**, never in a message to be pasted.
3. **Prose outside the command block**, always.
4. **Idempotent, validating, self-logging** — written for one tired run.
5. **Batch the crossings** that belong to one decision.
6. **Check before declaring something out of reach** — "can't" is a claim.
7. **A protected change travels with its checksum, the checker's verbatim output, and a
   verifiable backup** — never with an opinion that it can run.
