# Pattern: Decision questions in a recommendation mandate

> **Scope.** The block a coordinator injects into every delegation that must produce a
> recommendation someone will decide on, and the gate that checks the return. Real agent
> names, review queues, and the checker's implementation are outside this repo.

## Problem

A specialist asked for a recommendation will give one. It will be fluent, structured, and
confident — and three things are usually missing from it:

- **It does not know whether the question was already answered.** The system may have
  measured, decided, or refuted the same thing a month ago. The delegate, starting fresh,
  re-derives it, and the re-derivation silently replaces the earlier conclusion.
- **It does not check its own measurement.** A number arrives with no indication of whether
  the probe that produced it could have returned the other answer.
- **It does not say where it stops.** A recommendation with no stated boundary grows: the
  delegate that was asked about one control proposes three.

`docs/01-orchestration.md` § "The decision questions" states the questions for the
coordinator. This pattern is the other half: **the same questions, carried into the mandate
of whoever writes the recommendation**, and a gate on what comes back.

⚠️ **A rule that exists in one place binds only whoever reads that place.** In the deployment
this comes from, one of the sub-rules below existed word for word in the delegation block —
binding every specialist — and not in the coordinator's own rules. The reverse gap is just as
easy to leave open. Check who each copy binds.

## Pattern

### 1. Only for mandates that produce a recommendation

⛔ **Not for research, drafting, content analysis, or execution.** Only for a delegation whose
output is a *recommendation that supports a decision*.

The reason is measured, not stylistic. Applied to everything, the block gets **filled in**
rather than answered. In one deployment, a sample of written outputs that carried the block's
label was read against its method: **6 of 21** used the label without the method — headings
present, questions answered with prose that answered nothing. A block that is everywhere
teaches everyone to complete it.

### 2. The block, injected verbatim

The coordinator pastes it into the mandate unchanged. Paraphrasing it per delegation is how
the criteria drift.

```markdown
### Decision questions — REQUIRED in this recommendation

Answer all six BEFORE recommending. Each has an answer criterion:

- **0. Has this already been decided? Where is the earlier conclusion, and what has changed
  since?**
  RUN both searches — one semantic search over the system's memory, one verbatim search for
  the exact name — and CITE what they returned, including when they return nothing.
  A declared emptiness is a result; a presumed one is a guess.
- **1. What is the actual risk?** Name the failure mode, and say whether it has instances or
  is latent.
- **2. What self-control already exists?** List the layers — or write "none".
- **3. What does this cost ordinary, harmless activity?** The cost in the COMMON case, not
  the bad one.
- **4. What measurement supports this — and did you finish it?** A command, or `file:line`.
  A command that was DENIED is not a measurement: run it another way, or state that you did
  not measure.
  **And how do you know your measurement is right?** If the result were the wrong one, would
  the output you are citing show it? A probe that cannot fail does not measure — it
  describes.
- **5. Who watches that this stays alive?** Name the observer, and say whether what it runs
  on is itself watched. A clause with no witness is a note, not a control.

Two more parts are required:
- **A verification block at the top:** what you measured, and at least ONE verdict on a claim
  of YOUR OWN — `FALSE` / `REFUTED` / `CONFIRMED`. Without it, it is a reading list, not a
  verification.
- **"What I do NOT propose":** it may not be empty. It is the brake on scope creep.

Do not invent measurements to fill this in. "Not measured, and why" is a valid answer; a
fabricated measurement is not, and is the defect this block exists to catch.
```

### 3. The verification block — a verdict on your own claim

The top of the return lists what was measured and how. That alone is a reading list. The part
that makes it a verification is **at least one verdict on a claim the author made** — and the
most useful verdict is `REFUTED`:

```markdown
| What was measured | How | Result |
|---|---|---|
| ... | command or file:line | ... |

Verdicts:
- REFUTED — "X is absent". It is present, in an older form, at <location>.
- CONFIRMED — "Y is missing". A verbatim search for <term> returned nothing, and the same
  search found <known-present term> in the same pass.
- REFUTED, and the probe was mine — the first count returned the same value for every term,
  so it could not fail. Discarded and replaced by <method>.
```

⭐ **The last line is the one worth training for.** An author who reports that their own first
probe could not fail has shown that they checked it. An author who never reports one has
either been lucky every time or never checked.

### 4. "What I do NOT propose" — never empty

A recommendation's value is partly in its boundary. The section lists the adjacent changes
the author saw and **chose not to recommend**, with the reason: out of scope, someone else's
decision, not measured, irreversible. An empty section means the boundary was never drawn.

### 5. The gate is question 0, and it belongs to the coordinator

When the return comes back, the coordinator checks it before relaying it. Of the six
questions, **question 0 is the gate** — the only one that blocks.

⭐ **Why that one:** in the deployment this comes from, question 0 was the only item that
separated recommendations from non-recommendations perfectly — every document that was not a
recommendation lacked an executed, cited search; the other questions appeared, in some form,
in ordinary analyses too. The others inform the report; they do not block it.

The check is simple: is there a search, was it **run** (a query and what it returned, not a
sentence saying "I checked"), and is the result **cited** — including an empty result?

⛔ **The gate is the coordinator's, not the delegate's.** A failed return is not refused and
sent back as a punishment. It is **not relayed to the person without saying that it failed
the gate.** The person may still want it; they should know what they are holding.

⚠️ **A checker for this is a heuristic, and it can be written in an afternoon** — look for a
section for question 0, and inside it for the evidence of a query and its result. It will
have false positives and false negatives. Measure both on a sample of real returns before
trusting it, and keep the check on the one question it is good at.

## What the block does not do

- **It does not make a recommendation correct.** It makes the reasoning inspectable, and
  exposes the places where it was skipped.
- **It does not replace verification by execution.** The coordinator still runs the script,
  opens the file, checks the number against the source (`docs/02-smart-routing.md` § "The
  delegation mandate").
- **It does not prevent fabrication.** Nothing stops "searched, found nothing" being written
  without a search. The difference is that a query with a result can be re-run by the reader;
  "I checked" cannot.

## Principles

1. **Only for recommendations** — applied to everything, it gets filled in rather than
   answered.
2. **Inject it verbatim** — paraphrase per delegation is how criteria drift.
3. **Question 0 is executed, and its result cited, even when empty.**
4. **At least one verdict on the author's own claim** — the verification block is not a
   reading list.
5. **"What I do NOT propose" is never empty.**
6. **The gate is the coordinator's**, sits on question 0, and a failed return is relayed as
   failed — not hidden, not refused.
7. **Check who each copy of a rule binds** — the coordinator and its delegates read different
   files.
