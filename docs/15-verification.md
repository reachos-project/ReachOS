# 15 — Verification: probes that can fail

> **Scope.** How to measure, how to read a verifier, and how to tell a check that works from a
> check that only looks like one. The method is general; the checks, thresholds and
> instruments of any particular deployment are outside this repo.

Every other chapter in this repo leans on a verb it does not define: *verify*. A rule is
"verified by outcome", a return is "verified by execution", a control "is tested with two
probes". This chapter is what those words mean in practice — and, mostly, the ways each of
them fails while looking like it succeeded.

The common thread is one sentence: **a probe that cannot fail does not measure — it
describes.** Everything below is a way of making a probe able to fail, or of noticing that it
could not.

---

## 1. Designing a probe that can fail

A probe whose answer does not change with its input is not wrong, and it is not cached. It has
**no reach**, and what it returns looks exactly like a measurement.

The procedure, before using a new probe, before using an old one in a new context, and always
before writing *"absent"*, *"inert"*, *"blocked"* or *"does not work"*:

1. **Write down the expected result before running.** Otherwise any result can be fitted.
2. **Reach control (positive control).** In the same run, from the same place, the probe finds
   something **known to be present**. Without that, a negative does not mean absent — it may
   mean the probe never reached anything.
3. **Negative control.** A neighbouring case that **must** give the opposite result. If both
   give the same answer, the probe does not discriminate.
4. **Distinguishable reasons.** The ways the probe can fail must be told apart by their
   reason. A probe where everything reads as "failed" controls nothing.
5. **Measure in the real state.** The configuration actually in force — not the one from an
   earlier test, with a different switch in a different position.
6. **Do not execute what you are inspecting.** Asking a script for `--help` is not a safe
   probe: a script without an argument parser simply runs. Read it, parse it, or import it
   without calling its entry point.
7. **A correction to a probe inherits the probe's properties.** A self-test that proves the
   last error cannot recur says nothing about the next one. Check a few lines of the new
   version by hand before publishing numbers from it.

**Verification of the probe itself:** the reach control and the negative control give
**different** results in the same run. If they agree, the verdict is "not measured".

### Worked example: what an instruction file actually delivers

`docs/14-runtime-observed.md` § "Comments: free or not depends on where they sit" reports
whether HTML comments in always-loaded instruction files reach the model. The finding was
published wrong, then corrected; the probe that corrected it is a compact example of every
step above.

- **The question:** for each placement of a comment (own line, block, end of line, end of
  heading, mid-line), does the text inside it reach the model's context?
- **The hidden token:** a unique random token placed *inside* each comment. If the model can
  report it, the comment reached context.
- **The reach control:** a **visible** random token of the same shape, in the same file, outside
  any comment. If the visible token does not come back, the file never loaded — and the run
  says nothing about comments. Without this control, "no comment token came back" is
  indistinguishable from "the file was not there".
- **The negative control — against invention:** an **answer key**. The fresh session is asked
  to list every token of that shape it was given; any token it returns that is not in the key
  means the model is producing plausible tokens, and the run says nothing either.
- **Isolation:** a throwaway project, a fresh session, no tools — so the model cannot open the
  file and report what is on disk, which is a different path.
- **Declared absence:** the cells that were not tested are written as *"not tested"*, not left
  blank and not inferred from their neighbours.

⭐ **And the lesson that is not in the design.** A controlled probe run *before* the page was
first published had already shown own-line and block comments being removed. The published
text said the opposite. The two measurements were never reconciled — which is §6 below, one
level up: **two results that contradict each other are a finding, and the defect lives between
them.**

---

## 2. Before asserting a result

A measurement supports a decision only if it is about the **target**, taken in a **context
where the signal could move**, on the **right time base**, with the act that could have
contradicted it written next to it.

1. **Target.** Is the result about the thing in front of you, or about something similar — the
   staging copy, the other configuration, yesterday's version? A result about a neighbour is a
   **hypothesis** about the target. Re-measure.
2. **Context.** In this context, **could** the signal have moved? If a counter cannot change
   while the job it counts is idle, an unchanged reading taken while it is idle measures
   nothing. The
   result is "not measured".
3. **Predicate.** Does the predicate distinguish the outcomes that matter? "It changed" does
   not distinguish *unblocked* from *disappeared*.
4. **Time base.** Stores and logs are often in UTC; file timestamps and terminal output are
   often local time. Convert one side, and write the zone in the sentence. *A measured
   instance:* an export was declared to "fail silently" because its file was older than the
   events it should contain. Converted to one zone, the file was **newer**. A counter-check
   across every record found zero divergences — but the wrong claim had already entered a
   correction package.
5. **State.** Was the count taken in the middle of a transition? Then it does not compare with
   the count from before.
6. **Read the signal before fitting the story.** Spend one command looking at the raw signal
   before placing it inside the hypothesis you already have.
7. **An empty search is not absence.** It needs enumeration and reading — and a reach control
   (§1).
8. **Close the cheap doubt.** If settling it costs a few minutes of tooling, settle it instead
   of declaring it.

**When the result supports someone's decision**, the sentence that carries it states the act
that could have contradicted it, and what that act returned — a counter-check, a negative
control, or a declared absence (`docs/01-orchestration.md` § "The decision questions", the
second sub-rule of question 4). *"I verified"* is not one of the three.

---

## 3. Reading a verifier's verdict

Take from a verifier the verdict it actually issued — no more, no less.

1. **Read the output, not the return code.** A return code may not carry the verdict: a checker
   can report a discrepancy in its output and still exit zero. `if checker; then echo clean` is
   a test of the exit path, not of the system.
2. **Read the whole envelope** — standard output **and** standard error, the output log **and**
   the error log. Choosing in advance which one to keep is choosing what will be missing.
   *A measured instance:* a background job was declared stopped because its output log had
   stopped growing. Its error log, in the same directory, kept growing for most of a day.
3. **States in full.** *Unreadable* is not *conforming*. *Partial coverage* is not *zero
   defects*. A verifier that issues a verdict about something it did not read has to say so.
4. **Inert guards.** A return code captured after a pipe; an `if` that can never fire; a check
   whose failure branch is unreachable. Only a **complete reading** of the code catches these,
   and that reading is not delegated to a pattern search.
5. **The surface shows the whole value.** A reader that expects a bare number counts a value
   written as `≤ 2026-05-02` or `~40` as missing. Qualifiers are information, not noise.

**Verification:** inject a known-bad case and watch the **output** change. If the return code
changes and the output does not, or the reverse, the reading criterion is in the wrong place.

---

## 4. Verifying behaviour, not the presence of a token

The proof that the **mechanism acts** — not that the text declaring it exists.

1. **Separate the two layers.** Layer A: the declaration you write (a config field, a list
   entry, a matcher). Layer B: the mechanism recognises it, the dispatcher routes it, the
   executor accepts it. Count something as done only on layer B.
2. **Ask the mechanism.** A controlled denial using the real name, a run of the executor, a
   read of the *processed* state — not a read of the source file. ⭐ Both layers are needed,
   and neither is redundant: a matcher can be present (A passes) while the handler behind it
   never dispatches that name (B fails), and the reverse.
3. **Re-verify by behaviour.** "Does the system do X?", not "does the file contain X?". A text
   search that confirms a claim sends it out with more credit than it had.
4. **A proof predicate demands the act or the body, never the name.** `if "<duty>" in text`
   opens to anything that merely *mentions* the duty — including a note saying it was not done.
5. **Lexical verification** returns "none of the forms my lexicon knows". Before using it as
   proof, ask which forms the lexicon **does not** know in this codebase — another language in
   the same file, another way to overwrite a file, another spelling of the same act.

**Verification:** the same test, applied to a fixture that **has** the defect, fails it.

---

## 5. Auditing a verifier by its silences

The false negatives of a verifier live, by definition, in the list of things that **pass**. No
amount of analysis of what it rejected will reveal them.

1. **Run the verifier over the historical population**, and list what passes.
2. **Cross that list with what actually failed** — incidents, logs, errors someone saw in a
   terminal. Each intersection is a demonstrated false negative.
3. **Baseline × configuration matrix.** For each real version of the watched object, does the
   verifier report a difference from its baseline? Several different versions with zero
   reports means it is blind — whatever its green history says.
4. **Ask what it read.** A verdict about content it never parsed becomes "partial coverage".
5. **In review, ask the behaviour, not the inventory.** "Is it installed and hashed?" proves it
   has not changed. "Fire something it should catch" proves it bites.

**Verification:** the matrix must contain at least one cell where you **know**, by another
route, that a change happened. If the verifier reports it, it can fail; if not, it is blind in
that class.

⚠️ **The mirror-image rule:** a verifier that is never silent in the nominal state gets
ignored. So a verifier is audited from both sides — it must **speak** when there is a change,
and it must be **silent** when there is none (`patterns/retiring-instruments/`: draining is
what gives the silence its meaning).

---

## 6. When two correct controls contradict each other

Two controls, each right on its own, give opposite verdicts on the same act — an apply stuck
between two guards, a check that requires what another forbids. The defect is not in either of
them. **It lives between them**, and it shows only in an act that crosses both.

1. **Give both the same fixture.** Test them together, not each against its own examples. In
   one deployment, seven such pairs surfaced within a single day; the remedy that followed was
   a battery that feeds every control the same fixtures.
2. **Enumerate the whole model before touching anything** — the flags, the exception hierarchy,
   the permission layers. Fixing the symptom in front uncovers the next.
3. **Fix the block, not the occurrences.** When a search returns the places to correct, count
   them, and check **which** are wrong — the neighbour of the one you fixed is usually wrong in
   the same way.
4. **A hard rule cannot guard both floors.** A rule that forbids both *losing* a protected file
   and *changing* it forbids maintenance. Decide which floor the rule protects, and let the
   other be protected by something else.
5. **A derived artefact with no installer drifts silently** — and its "derived" label makes it
   more trusted than a hand-written one.

**Verification:** after the fix, the shared fixture passes both controls, **and** the defective
case that motivated each one is still refused by that control.

---

## 7. Validating a fix, or a test

1. **An "obvious" fix gets an A/B before adoption.**
2. **When the baseline already passes, change surgically** rather than redefining globally.
3. **Does the test still test?** Does it point at code that exists? Does it run more than once?
4. **A new version of something already reviewed:** lay the old version's assertions against
   the current criteria; any inversion blocks.
5. **Static review is not execution** for operations that change state.

**Verification:** the test, applied to the code **before** the fix, fails; applied after, it
passes. A test that passes on both did not test the fix.

---

## What each signal can — and cannot — be used for

| Signal | Supports | Does **not** support |
|---|---|---|
| a verifier's return code | nothing, without reading its output | a verdict |
| a verifier's empty output | the nominal state, **if** it has shown it can fail | "all is well", from a verifier never exercised |
| a long green streak on an object that changes | nothing, until the silence matrix (§5) | "nothing changed" |
| a text search confirming a claim | that the text exists | that the system behaves that way |
| an unchanged hash | that it did not change | that it bites |
| a passing self-test | that the last error does not recur | the next error |
| a written declaration (field, list entry, matcher) | intent | that the mechanism recognises it |
| an empty search or listing | absence, **only** with a reach control in the same run | absence, without one |
| a lexical "conforming" | absence of the **forms** the lexicon knows | absence of the **effect** |
| a store timestamp against a file timestamp | order, **after** converting the zone | order, directly |
| a count taken during a transition | describing the transition | comparing with the count before |
| a single reading of a live value | deciding, **if** the value was shown to move | computing with it, without that proof |
| a delegate's report | `[REPORTED]` | `[READ]` or `[MEASURED]`, without independent corroboration |

## What has been tried, and does not work

- **More discipline** ("whoever creates X declares it in Y"). The failure being fixed *was* a
  discipline failure. Derive or discover instead (`docs/05-guardrails.md` § "Controls decay,
  and they do it quietly").
- **A self-test that proves the error that just happened.** It passes on every version of a
  probe that keeps being wrong in new ways.
- **Re-verifying with a text search.** The claim leaves with more credit than it came in with.
- **Writing the criterion before looking — alone.** Necessary, not sufficient: it does not ask
  whether the signal could have moved.
- **Widening a detector without measuring its noise.** Count, before widening, the new denials,
  how many are true, and which legitimate tools would stop running.
- **A reminder where a structural remedy was available.** That is deferring the remedy and
  calling it a control.

⚠️ **Nothing in this chapter has a mechanical trigger.** These are behaviours, and they are
verified by outcome: count the corrections that fall in the class *"a measurement or verdict
was misread"* (`patterns/adversarial-review/` § "Verify by outcome, never by grep"). If the
count does not fall, redesign rather than reinforce.

## Principles

1. **A probe that cannot fail does not measure — it describes.**
2. **Every negative carries a reach control; every probe carries a negative control.**
3. **A result holds for the target measured, in a context where the signal could move.**
4. **Read the output, the whole envelope, and the state by its full name.**
5. **Verify the mechanism, not the declaration.**
6. **Audit a verifier by its silences** — it must speak on change and be silent otherwise.
7. **Two correct controls that disagree are a finding**; give them the same fixture.
8. **A fix is validated by a test that fails before it and passes after it.**

## See also

- `docs/01-orchestration.md` § "The decision questions" — the sub-rules of question 4.
- `docs/05-guardrails.md` — two probes per guardrail, one denied and one allowed.
- `docs/14-runtime-observed.md` § "Checking these yourself" — the same method applied to a
  runtime's own transcripts.
- `patterns/decision-questions/` — the verification block that carries these results into a
  recommendation.
