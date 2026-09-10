# 10 — Session lifecycle (opening and closing)

> **Scope.** The pattern for starting and ending a working session with a persistent
> assistant. Real script names, paths, and notification channels are outside this repo.

A coordinator with persistent memory has two moments that decide whether that memory is worth
anything: **how a session opens** and **how it closes**. Get them wrong and the system
accumulates files nobody reads and loses the one thing that does not survive on its own — what
was learned about working with this particular person.

## Three places, not one

| Where | What lives there | Read |
|---|---|---|
| **Memory index** | stable pointers to behaviour and lessons | every session, automatically |
| **Active shelf** | work in flight — what is open, what waits on a decision | every session, **explicitly** |
| **Project folders** | the detail: dossiers, measurements, runbooks | on demand |

⛔ **Keep work in flight out of the memory index.** They have opposite lifecycles: the index
is stable and loads every time, the shelf changes hourly. Mixing them means the index grows
without bound and the volatile state gets treated as doctrine.

⚠️ **The shelf has a size ceiling, and it is functional, not aesthetic.** Whatever watches it
for unexpected changes stops working above some size — so past that point the shelf is
unguarded, which is worse than it being long. Measure it at every close.

### The shelf has a grammar, and the grammar is what makes it work

A shelf that is only prose gets read by a person and ignored by every instrument. The
grammar is small — see [`templates/ACTIVE.template.md`](../templates/ACTIVE.template.md) for
the full table — and three rules carry it:

1. **The unit is the block** (a paragraph), never the line. An entry is a state symbol at the
   start of a paragraph plus everything until the next blank line, heading or symbol. Any
   verifier that matches the symbol on a line and looks for evidence on *that* line will
   miss the evidence on the second line of the same paragraph — and will report the whole
   shelf as "unverifiable" while looking healthy. That exact defect ran for weeks here before
   it was measured: 42 of 42 entries unverifiable, zero actionable, banner green.
2. **The symbol is an instruction to the opening, not decoration.** ⏳ is work owed; ⏰ names a
   clock (the date lives in the clock index, not here); 📋 is the user's decision; ⏸ is
   paused by the user; 🟢/✅ is closed and generates nothing. Section headings that carry a
   symbol are taxonomy and are excluded from the count.
3. **Every open block carries an anchor the world can check** — a memory link, an anchored
   artefact path, a clock or routine id. The sweep classifies by **discovery**: it goes and
   looks (does the file exist? did the clock close?) instead of trusting the block's own
   claim. Blocks with no anchor are a legitimate, named, small class — a question waiting on
   the user, a decision not yet taken. A block still marked open whose clock has already
   closed is *drift*, and it is the most common defect: the work got done and the symbol was
   not flipped in the same edit.

The reader that consumes this is the sweep in the opening: one line —
`sweep: N · a OK · b unanchored · c actionable` — and a loud `CRITERION BLIND` if it resolved
zero anchors on a non-empty shelf. Silence in the nominal state is the goal; a verifier that
never fires has stopped verifying.

## Opening

The pattern is **one gathering process, not many round trips**. Naively, session start is six
or seven separate checks — pending items, health, queue drain, snapshot, environment — each a
separate call. Wrapped into a single process returning one structured digest, the same
information costs two steps instead of seven.

What the opening does:

1. **Read the active shelf explicitly.** It does not arrive through the automatic memory load.
2. **Check the memory layers** — each tier reachable, each store answering. Report it as a
   **count**, `N/M layers OK`, not as reassurance: an opening that says "all good" without
   saying what it checked has not checked anything the user can rely on.
3. **Drain the daemon's queue** — the checks that ran while nobody was there.
4. **Diff the memory index against a snapshot.** If it changed without a recorded close, the
   previous session probably crashed: show the difference before doing anything else.
5. **Read what is cheap; never do what is expensive.** State that a background service writes
   periodically — consumption, budget, external health — and at start-up **read that file**.
   Do not open a browser, call an API, or run a scan to refresh it. The opening is the worst
   moment to do slow work: the person is waiting and has not yet said what they want.
6. **Report the routine and clock state — and, for a routine that proposes, its last
   conclusion, not merely its name.** Naming an instrument that has already produced a verdict
   reads as *not yet run*, and the verdict waits for an approval nobody knows to give
   (`docs/09-clocks-and-routines.md`). A pending item
   reading *"did this fire?"* should find its answer already in the digest.
7. **Report a banner** (below), and then stop.

### Reading a cached measurement honestly

Whenever the opening reports a number it did not measure itself, it reports **three** things:
the value, **its age**, and its source.

⛔ **And when the cached value predates the period it describes, show no number at all.** A
budget reading from before the weekly reset measures *last* week; displaying it would drive
this week's decisions on dead data. Say "no reading for this period" and decide by judgement.
**Absence of information is not a measurement, and must not be dressed as one.**

⛔ **Never substitute a local estimate for the real reading** unless the estimate has been
validated against it. An approximation whose error is of unknown size decides worse than no
number, because it carries the same air of authority.

### The banner

The banner is the whole contract of the opening: everything the person needs in order to
decide what to do, and nothing that requires them to ask a follow-up question to be useful.
Environment, layer health, what is in flight, what the daemon found, what is due, what is
waiting for a decision.

⭐ **One rule about it is load-bearing, and it is not obvious: anything that has disabled a
channel the user relies on must appear at the top, verbatim, and must not be summarised.**

The reason is structural. If the alerting channel itself is what broke — the notifier is
throttled, the relay is stopped, the queue is not draining — then no alert can announce it.
The user would discover it by noticing, days later, that their phone stopped answering. **The
failure of a warning path cannot be announced through that path**, so it is announced here,
in the one place guaranteed to be read.

⛔ **Then stop.** The opening ends with the banner and waits. It does not start work, tidy
anything, or begin investigating a discrepancy it just surfaced. Volunteering work before the
person has spoken spends their context on your priorities.

⛔ **The opening surfaces; it does not investigate.** A pending item that says *"did this
routine fire?"* should have its answer in the digest, not trigger a research session before
the user has said a word. If something is unknown, say it is unknown and move on.

⛔ **Do not ask the environment questions the environment cannot answer honestly.** Detecting
which machine or terminal the user is on by inspecting session variables fails silently under
a persistent multiplexer — the values freeze at the moment the server started, and stay wrong
for days. Prefer a stated default plus a cheap correction ("assume A, the user says otherwise
when it matters") over an inference that is confidently stale.

## Closing

Closing is where the session's residue is converted into something the next session can use.
Run it when the user signals the end — and accept that it will sometimes be skipped.

1. **Gather once** — the same single-digest discipline as the opening.
2. **Audit the session's authorisation events.** Present them in a batch for the user to
   classify (wrong / intended / unsure), not one interruption at a time.
3. **Sweep the active shelf** — what closed, what is stale, what is now overdue.
4. **Diff the memory index** against the snapshot and let the user revert any line.
5. **Write the narrative log** (below).
6. **Write new memories**, by tier policy.
7. **Re-baseline the snapshot** and log the close.

⚠️ **The close must be invoked, so design for it being skipped.** If the user simply restarts,
the next opening's defensive diff still catches an altered index — no security is lost. What
is lost is the narrative log, and that is the part nothing else reconstructs.

## The narrative log — the part that is actually hard

Separate from the task record, keep a running log of **how the assistant and the person worked
together**: what was misunderstood, what correction the person made, what phrasing landed and
what did not.

⭐ **The test for what belongs here:** is this about *how I operate with this person*, or is it
domain knowledge?

- ✅ *"They correct framing more often than content — the fix is to question the framing before
  starting, not to check the output afterwards."*
- ❌ *"Regulation X has an eight-year validity."* — that is a fact; it belongs in memory.

This distinction is worth enforcing, because the second kind is easy to write and the first
kind is what actually changes behaviour.

Four fields per entry and no more — **date · what went wrong · the person's correction · what
generalises**. The third field is quoted, not paraphrased: their words are the evidence, and a
paraphrase is already the interpretation the log exists to check. See
[`examples/halcyon-consulting/narrative-log.md`](../examples/halcyon-consulting/narrative-log.md)
for three worked entries.

⭐ **A correction that can be fixed in a file should not be fixed in a habit.** If the entry
ends "so I will remember to…", it is unfinished: find the artefact — a routing row, a template
line, a rule — that makes the correction unnecessary.

### Watching for new vocabulary

A useful signal at close: **words the person used that the system has never seen before.**
New vocabulary is where the relationship is currently expanding — a new project, a new
concern, a new way of naming something that already existed.

⛔ **Give it a "nothing new" output, distinct from silence.** Measured failure: a derived
vocabulary check produced an empty section when it found nothing, which looks identical to the
check not running. It stopped running and two closes passed before anyone noticed — the same
way its declared predecessor had died months earlier, also unnoticed. A check that reports
nothing must still report *that it looked*.

## Anti-patterns

⛔ **Presenting audit items one at a time.** The user is closing the session; a queue of
individual confirmations guarantees the close gets abandoned halfway.
⛔ **Writing memories because the session went well.** Writing is free and unprompted, removal
is expensive — so the corpus fills with work logs disguised as lessons. Ask what generalises.
⛔ **Treating "the log said the write was authorised" as "the write happened."** See
`docs/08-control-via-audit.md`.

## Principles

1. **One gather, not many probes** — at both ends.
2. **Work in flight lives apart from stable memory.**
3. **Open by surfacing, not by investigating.**
4. **A skipped close must not cost safety** — only narrative.
5. **Log the working relationship, not just the work.**
6. **"Nothing found" is a result and must be printed.**
