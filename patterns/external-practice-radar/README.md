# Pattern: External practice radar (scout → triage → digest → council → ledger)

> **Scope.** The pattern for watching the outside world for practices worth adopting, and for
> adopting them deliberately. Real sources, keyword lists, schedules, network configuration,
> and the domains of any particular user are outside this repo.

## Problem

An AI team that only reviews itself improves along the lines it already knows. The field it
works in moves weekly — new papers, new tooling, new failure reports from other teams — and
the practices worth adopting are almost never found by the team that needs them.

The obvious remedy, "read the news", fails in three predictable ways:

- **Volume.** Hundreds of items a day. Reading them is a job; skimming them is noise.
- **Adoption by enthusiasm.** Something reads well, gets adopted, and nobody later asks whether
  it worked — or remembers that it was adopted.
- **Silent degradation.** The collector breaks, returns half of what it should, and the digest
  that week is shorter. A short digest looks like a quiet week.

⚠️ The last one is the dangerous one. **An absence of a topic in a degraded harvest is not
information** — and nothing in a short list announces that it is degraded.

## Pattern

A funnel with five stages. The first three are automatic and cheap; the fourth is a person;
the fifth is a record.

```
 scout (daily, metadata only)
   │  hundreds of items → new candidates, deduplicated against a seen-index
   ▼
 triage (weekly, scored)
   │  candidates → a shortlist above a cut-off
   ▼
 digest (weekly, mechanical)
   │  shortlist → an agenda with the decision column left blank
   ▼
 council (weekly, a person)
   │  each item → adopt / test / reject / park
   ▼
 adoption ledger
      decision · reason · date · the task it opened · what was learned
```

### 1. Scout — cheap, metadata only, and honest about what it missed

The scout reads **metadata**: titles, abstracts, dates, categories, links. It does not read
full texts. It filters by a keyword list of adoption-relevant terms, deduplicates against a
seen-index, and writes the day's candidates to a dated file.

⛔ **The scout reports its own integrity on two lines, every run:**

| Line | Question | States |
|---|---|---|
| **Today's harvest** | did every source that should have answered, answer in full? | **complete** — N of N sources, zero losses · **floor** — K of N, with the cause per source (timeout, truncated body, parse failure) |
| **The series** | over the last window, is every day that should have a harvest covered? | **complete** · **floor** — which days are missing, which are partial · **indeterminate** — and why |

⭐ **"Floor" means the number is a lower bound.** The candidates exist; some others that should
be there are not. Everything downstream carries the mark: a digest built from floor batches
says so, and says which days.

⚠️ **A degraded harvest is a result, not a fault.** It does not make the run exit non-zero. A
scheduler that treats non-zero as "the routine is broken" would page someone for a partial
download; the degradation belongs in the summary and in the data, where the digest reads it.
Reserve a distinct exit status for **"I did not measure"** — a run that could not reach its
state at all — so that it is never confused with "measured, and nothing new".

⛔ **Negative control, before trusting it:** point the scout at a source that does not exist,
and confirm it reports **floor**. A collector that reports success with zero items on a dead
source cannot fail, and so does not measure.

⭐ **Deduplicate the same-day re-run.** A scout that runs twice on one day must merge, not
overwrite — in the deployment this comes from, a second run once overwrote the first and
dozens of candidates had to be recovered. The second run of the same day should produce zero
*new* candidates.

### 2. Triage — a score and a cut-off

Each candidate gets a relevance score from simple, inspectable features (keyword hits,
category, recency). Those above the cut-off form the shortlist.

⚠️ **The cut-off is a conclusion in disguise until its sensitivity is tested.** Move it within
a defensible range and see whether the shortlist changes materially. If it does, report the
shortlist as a function of the cut-off.

### 3. Digest — mechanical, with the decision left blank

The digest is **generated, not written**: no model, no summaries, no opinion. It is an agenda —
one line per shortlisted item, with its link, its score, its integrity marks, and **an empty
decision column**.

⭐ **Why mechanical:** a digest written by a model arrives with a framing — this matters, this
does not — and the person in the council inherits the framing instead of forming a judgement.
The digest's job is to make the decision possible, not to pre-make it.

The digest opens with an **integrity section**: how many batches in the window, how many were
floor, which days, and a plain warning that the absence of a topic in those days is
uninformative.

### 4. Council — the only stage with a person in it

Once a week, a person goes through the agenda with the coordinator. Each item gets one of four
decisions:

| Decision | Means | Produces |
|---|---|---|
| **adopt** | take it into how the system works | a task, with an owner and a way to know it worked |
| **test** | try it in a bounded pilot first | a pilot task with a stop criterion |
| **reject** | not for us, and why | a ledger line — so it is not re-proposed next month |
| **park** | not now | a ledger line **with the trigger that would reopen it** |

⛔ **Adoption is a human decision, and the funnel is built around keeping it one.** Automating
the first three stages is what makes the fourth affordable; automating the fourth removes the
point. A system that adopts practices on its own is also one whose judgement erodes without
anyone noticing.

⭐ **Expect most items to be parked.** In the deployment this comes from, about half of all
council decisions were "park", and adoptions were a small minority. That is the funnel working,
not failing.

### 5. The adoption ledger

One line per decision: the item, the decision, the reason, the date, the task it opened, and —
later — what was learned. The ledger is what answers *"did we already look at this?"*, and it
is the first place question 0 of `docs/01-orchestration.md` searches when a practice is
proposed from anywhere else.

## Verifying published code — only for pilot candidates

Before an item goes to the council as a candidate for a **pilot**, somebody must establish
whether its code is published. Not for every digest item — only for the few that may be run.

A ladder, stopping at the first hit:

1. **The paper's landing page and full text.**
2. **The paper's "code availability" section** (or "data and code", "resources").
3. **Affiliation → the lab's site → its code-hosting organisation → enumerate the
   repositories.**
4. **A search scoped to that organisation or user.**

⛔ **Never search free text for the project's name.** A project name is not an identifier; an
organisation is. In the deployment this comes from, a free-text search landed on a
**homonym**, and a paper whose code *was* published was labelled as unverified.

Three exclusive labels, and one forbidden:

| Label | When | Must carry |
|---|---|---|
| **code published** | one of the four rungs hit | URL · **licence** · date of last push · traction (stars, forks, issues) |
| **announced but not located** | the paper says it exists; all four rungs missed | where it is announced, and which rung failed |
| **not mentioned** | the paper does not claim code exists | — |

⛔ **"Not verified" is forbidden.** It merges *"we looked and there is none"* with *"we did not
look"*, and the two decide differently.

⭐ **The licence is decision-relevant, not metadata.** Code with no licence cannot be run in a
pilot by a team that respects licences; a "code published" label without the licence does not
enable the decision the label exists for.

## Silence is the nominal state

Each stage is a **no-op when the stage before it produced nothing**: triage runs only if there
are scout batches newer than the last digest; the digest is produced only if at least one
shortlisted candidate is not yet in a digest. A quiet week produces **nothing**, not an empty
digest.

⭐ This is what makes the funnel's output meaningful. A digest that always arrives trains the
person to open it without reading. A digest that arrives only when there is material — with its
integrity section saying how complete that material is — is read.

⚠️ **Silence only means "nothing new" if the chain has shown it can speak.** The negative
control on the scout, and a run where a known new item does travel through to a digest, are
what earn the silence its meaning.

## Governance

- **Every new source is a decision.** If the scout runs confined (`docs/07-worker-confinement.md`),
  adding a source widens its egress allowlist. Give the scout an allowlist of its own: a list
  shared with other confined jobs widens all of them at once, and the job with the most autonomy
  inherits hosts its task never needed. Either way it is an envelope change, and it is the
  person's.
- **Check a new source domain before trusting it** — the same scrutiny as any URL recommended to
  the person.
- **Prune the sources periodically.** A source that never contributes to a shortlist is cost
  without signal.
- **Primary sources for anything that will be cited.** The radar finds; it does not ground.
- **Harvested metadata is untrusted input.** Anyone can publish a title or an abstract. At
  every stage that reads it — including the council, where a model sits beside the person — it
  is data, never instruction.

## Principles

1. **Cheap stages are automatic; the adoption decision is a person's.**
2. **The scout reports its integrity on two lines** — today's harvest and the series — and
   "floor" travels downstream.
3. **A degraded harvest is a result, not a fault**; "did not measure" has its own status.
4. **The digest is mechanical** — an agenda with the decision blank, not a summary with a view.
5. **Four decisions, and "park" carries its reopening trigger.**
6. **Verify published code by ladder**, never by free-text name; "not verified" is forbidden;
   the licence decides.
7. **Silence is the nominal state** — once the chain has shown it can speak.
