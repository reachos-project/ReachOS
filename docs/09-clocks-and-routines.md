# 09 — Clocks and routines (two different things)

> **Scope.** The pattern for time-driven work in a coordinated system. Real schedules,
> service names, and notification channels are outside this repo.

Anything that has to happen *later* falls into one of two categories, and conflating them is
the single most common source of silent failure in a long-running assistant.

| | **Clock** | **Routine** |
|---|---|---|
| Fires | **once**, on a date | **repeatedly**, on a cadence |
| Example | *"re-check this dependency on 30 September"* | *"review memory usage every 14 days"* |
| Done means | the question was answered — the clock is **retired** | this period's occurrence happened — the next one is due |
| Failure mode | passes unnoticed and nobody ever answers | drifts, or is reminded forever and never executed |

⛔ **A clock is not a routine with one occurrence, and a routine is not a clock that repeats.**
A clock carries a *question* and dies when answered. A routine carries a *practice* and never
dies. Storing them in the same structure forces one of them to lie about its state.

## Where this state lives

⛔ **Not in markdown prose.** The natural first implementation writes "⏰ check on 30/09" into
a notes file. It fails in three ways at once, all measured:

1. **It cannot be queried.** *"What is due this week?"* becomes a full-text search over prose,
   which finds the phrasings you thought of and misses the rest.
2. **It drifts from reality.** The same date ends up written in two files with two different
   values, and nothing detects the disagreement.
3. **It has no schema for "answered".** A clock that fired and was dealt with looks exactly
   like one that fired and was ignored.

⭐ **Put clocks and routines in the transactional store** (the same database that carries
tasks and deliverables — see `examples/db/schema.example.sql`), and let the notes file carry
a *pointer*, not the state. Prose is for the reasoning; the store is for the state.

⭐ **Two columns carry most of the weight.** A clock moves `armed → acked → retired`: `acked`
records that a human saw it fire, `retired` records that the question has an answer — collapse
them and "answered" becomes indistinguishable from "dismissed". A routine carries `armed_since`,
the date of its first successful fire, because a miss counted before that date is an alarm that
is wrong on day one. Both are in [`examples/db/schema.example.sql`](../examples/db/schema.example.sql).

⚠️ **A migration caveat, learned the expensive way:** when the dates already live in prose,
some of them have no date at all — they say "soon", "next quarter", "when X lands". Those
cannot be mechanically imported, and inventing a date for them is worse than leaving them out.
Import what is unambiguous, list the rest for a human, and **do not let the importer guess**.

## Reminded is not done

This is the failure that survives every dashboard.

If "last fired" is read from the **notification** record, it records that a reminder was
produced — not that anything happened. A routine can be reminded weekly for two months and
executed zero times, and the display stays green throughout.

Measured in one deployment: **10 of 18 routines had no record of completion at all**; one had
been enqueued six times and carried out none.

```
reminded_at   ← written by the scheduler, when it enqueues
completed_at  ← written by the session, when the work is actually done
```

⭐ **Declare, per routine, what constitutes completion** — the concrete logged action whose
presence proves it ran. Then make something *read* that declaration.

⚠️ **And check the reader exists.** In this deployment the per-routine "completion action"
field was already defined in configuration, and nothing ever read it — the startup code
loaded only the notification file. The gap was not a missing field; it was a **missing reader
for a field already shipped**. Before designing a mechanism, search for the one you may
already have.

## How far a routine may go on its own

Cadence answers *when*. It does not answer **who runs it, and how much it may do without
asking** — and that is a separate declaration each routine has to carry.

| Class | What it may do | What it hands back |
|---|---|---|
| **Measure-only** | runs unattended, start to finish | a record. It changes nothing, so nothing needs approving |
| **Propose-and-hold** | runs the survey unattended, **writes nothing** | a verdict per item, with the evidence, awaiting a go |
| **Ask-first** | does not run without a person present | nothing until asked |

⛔ **Classify by what the routine actually executes, not by its most dangerous step.** The
common error is to look at a routine that reads twenty things and writes one, see the write,
and put the whole thing behind a prompt. What that costs is the nineteen reads — they were
free, they were safe, and now they only happen when someone remembers to ask. Split it: the
survey runs on its own, the write waits.

⭐ **The class is a property of the current scope, not a permanent label.** A routine that is
widened from reading to also removing has changed class, whatever its configuration still
says. Whoever widens it re-declares it in the same act — and the declaration belongs where the
routine is defined, not in a commit message nobody re-reads.

⛔ **The taxonomy is worth publishing; your instance of it is not.** Which of your routines sit in
which class is a map of when your system acts without a witness — an internal document, for the
same reason `docs/05-guardrails.md` gives for keeping your residual analysis in the house.

## The middle class needs a reader — or it silently becomes a queue

⛔ **This is the failure one level up from "reminded is not done", and it is harder to see.**
There, the routine never ran. Here **the routine runs perfectly**, produces exactly the verdict
it was designed to produce, writes it to the activity record — and nothing happens, because
nothing puts it in front of the person whose approval it is waiting for.

The startup surface shows the routine's **name** in a list of things needing attention. It does
not show **what the routine concluded**. So the reader sees a name, reads it as *"this has not
run yet"*, and either ignores it or — worse — redoes the work by hand.

Measured in one deployment: a reconciliation routine of this class had produced a verdict in
**14 of its last 20 runs**. None had been acted on. The backlog it was designed to prevent had
been accumulating for days, in plain sight, on a display that reported the routine as merely
"due".

⭐ **The fix is not more autonomy. It is a channel.** Carry the routine's **last conclusion**,
with its date, onto whatever surface the person actually reads. One line. The approval that was
never asked for gets asked, and the queue drains in seconds instead of accumulating.

⚠️ **That line is written by a routine and read by a human on an auto-loaded surface — treat it as
untrusted input on a trusted channel.** If any input to the routine is attacker-influenceable, its
conclusion becomes a delivery path into every subsequent session's context. The same two-sided
diff that guards the memory index (`docs/10-session-lifecycle.md`) applies here, for the same
reason: a surface that loads itself into context needs someone able to see what changed on it.

⚠️ **Resist the obvious alternative.** Promoting the routine to measure-only so it stops
needing a go is the change that *increases* what the system does unattended — and the argument
for it will be that the routine's judgement is better than the operator's. It may well be. That
is not what decides it; see `docs/01-orchestration.md` on which direction of change is the
person's to approve.

⛔ **And the symmetric error is real too:** asking for approval on a routine that was armed
precisely so it would not need any turns automation back into a waiting list. If it needed a
go every time, it should not have been armed. **Both errors come from the same missing
question — how far may this one go on its own — asked once, when the routine is written.**

## Parking something is a scheduling act

⛔ **"Later" is not a plan.** Deferring work without a **named trigger** is deferring it in
silence, and silence is indistinguishable from abandonment.

A parked item states what will bring it back: a date, a named recurring review, or an
explicit request. *"When I get to it"* is not a trigger; *"the 11 September memory review, or
when the user asks"* is.

## Anti-patterns

⛔ **A "missed" count that includes periods before the routine existed.** It produces an alarm
that is wrong on day one, which teaches everyone to ignore it. Only count misses inside the
window in which the routine had already proved it could fire.

⛔ **A durable schedule that fires per session.** If a recurring job is registered per
conversation rather than per system, N open sessions produce N executions of the same work.
Register the schedule once, at system level; let sessions *consume* it, not re-arm it.

⛔ **A clock whose reopening condition is satisfied by its own test.** *"Re-check when the
service responds"* — the check itself makes it respond. State the condition in a variable the
test does not touch.

⛔ **A surface that names the instrument instead of reporting its conclusion.** A list of
routines "needing attention" is a list of names. Names are read as *work not yet done*, so a
routine that already did the work and produced a verdict is indistinguishable from one that
never ran. Carry the conclusion, not the label.

## Principles

1. **Clocks die; routines don't** — different lifecycles, different storage.
2. **State in the store, reasoning in the prose** — never a date living only in a sentence.
3. **Record completion separately from reminder** — or an unexecuted routine looks healthy.
4. **Every deferral carries a named trigger.**
5. **Never invent a date** for something whose date was never known.
6. **Every routine declares how far it may go alone** — and is classified by what it executes,
   not by its most dangerous step.
7. **A routine that proposes needs somewhere its proposal is read.** Otherwise it runs
   flawlessly, concludes correctly, and changes nothing.
