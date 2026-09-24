# Pattern: Domain manuals (refer by manual and section name)

> **Scope.** The pattern for keeping references between documents true as the documents
> move, and for giving each domain one place that has a duty to be right. Real manuals, their
> sections, and the paths they hold are outside this repo.

## Problem

A growing system accumulates notes, runbooks, rules, scripts and configuration that point at
each other. Each pointer is written as a path, or as a section number, because that is the most
precise thing to hand at the moment of writing. Then things move.

- **Paths rot.** A file is renamed, drained, moved to another folder. Every document that
  named it now points at nothing — and nothing about the pointer looks broken until someone
  follows it.
- **Section numbers rot faster, and silently.** A section is inserted above; every `§7.2` in
  the corpus now points at the *wrong* section, which exists and reads plausibly. In the
  deployment this comes from, a section number written into thirteen places had to be
  rewritten in all thirteen.
- **Pointers hide in data, not just in code.** Search the repository and you find the paths in
  scripts and prose. You do not find the ones sitting in a **free-text field** of an external
  system's configuration — a job definition, a dashboard, a rule in another tool. In one
  deployment, a batch of live definitions in such a system carried a file path in a description
  field — data, not code, where no search of the repository reaches. Draining the file without
  correcting them would have left dead pointers inside a system nobody greps.
- **Many notes, no door.** A domain with forty notes about it has forty partial truths, some
  superseded. A reader who opens the wrong one first acts on it.

## Pattern

### 1. Every domain has a manual, and only the manual holds the paths

> One artefact refers to another as **`<domain manual> § <section name>`**. The manual is the
> only place with a **duty to be right**, and it — and only it — holds the real path, the
> script, and the reason.

From that follows the prohibition: **no other artefact writes paths** — not in prose, not in
code, **not in data**. Code resolves its own neighbours relative to itself, never by an absolute
path to a sibling.

⚠️ **The positive form is the rule; the prohibition alone makes things worse.** Forbid paths
without offering somewhere to point, and the references simply disappear — which is worse than
a stale pointer, since a stale pointer at least says what to look for.

**Two obligations, without which this cannot be applied:**
- **every domain has a manual**, even a short one; and
- **the manual takes in what the pointer carried.** If a document used to say "see
  `tools/x.py` line 40 for why the limit is 30", the manual's section must now say why the limit
  is 30. Otherwise the reference points at a place that does not answer — the same defect in
  different clothes.

### 2. Anchor by section *name*, never by number

Sections get renumbered; names are chosen to survive. A reference by name survives insertion,
deletion, and reordering. A reference by number survives none of them, and fails by pointing at
a **different, real** section — the worst kind of failure, because it reads fine.

⭐ The same applies to the manual's own internal links, and to this repo: its documents refer to
each other by file and by section name.

### 3. The manual is a door, not the evidence

The manual **summarises what decides**, and points to the notes that hold the evidence. The notes
remain the evidence; the manual is the one place to enter the domain.

> **Usage rule, written at the top of each manual:** before acting in this domain — before a
> measurement, a change, a claim that something is absent — **the first act is to open this
> manual**, before any probe or hypothesis.

⭐ **Why "open before acting" matters more than "the manual is complete":** the recurring failure
is not a missing note. It is knowing that the note exists and running the procedure from memory
instead of opening it.

### 4. The SOP format

Each operative section follows the same shape, so a reader landing on any section knows where
to look:

| Part | Contains |
|---|---|
| **Objective** | what this procedure achieves, in one or two sentences |
| **When to use (trigger)** | the concrete moment — a symptom, an act about to happen |
| **Procedure** | numbered steps; each step links to the note holding its evidence |
| **Verification** | how to know the procedure worked — ideally a control that would fail if it had not |
| **Reference case** | one real, dated instance where this went wrong, told briefly |
| **What does NOT resolve it** | the remedies that were tried and failed — so they are not tried again |
| **Links** | other sections by name, and the underlying notes |

And at the top of the manual, before the sections, four navigation tables:

| Table | Answers |
|---|---|
| **Signals** | which signals may be used to decide, and which may not (`docs/15-verification.md` has a generic version) |
| **Symptom → first act** | *"I am about to do X"* → *"do this first"* → *"section"* |
| **What was tried and does not work** | the list that stops the same remedy being proposed again |
| **What is open** | the known gaps, stated, so nobody presents them as solved |

⭐ **The "Reference case" and "What does NOT resolve it" parts are the ones that pay.** Procedures
can be reconstructed; the memory of what failed, and how, cannot.

### 5. A root index and satellites

One **root manual** indexes the others. Each domain manual is a **satellite**: it declares its
position under the root and the domains it covers.

⚠️ **A term shared between domains has one owner.** "Backup" may appear in half a dozen manuals;
one of them owns the definition for each sense, and the others cite it by name. Two manuals that
each define the same term will, eventually, define it differently.

⭐ **Route by manual.** Where the coordinator routes work by domain (`docs/02-smart-routing.md`),
a column naming the domain's manual lets every delegation carry the door to that domain in its
mandate — the "where the ground truth lives" item, answered once.

### 6. When a domain has too many notes

A domain that has accumulated many notes is the signal to compile a manual — not to write
another note. The compilation keeps the notes, replaces their many entry points with one, and
removes from the always-loaded index the individual pointers the manual now covers.

## What this does not do

- **It does not make the manual correct.** It concentrates the duty to be correct in one place,
  where it can be checked. A wrong manual is wrong everywhere at once — which is also why it is
  found faster.
- **It does not remove the need to re-measure.** A manual records what decides and why; it does
  not freeze the world it describes.
- **It does not reach pointers it does not know about.** Enumerate the external stores (tool
  configurations, scheduled job definitions, dashboards) before draining anything a path points
  at.

## Principles

1. **Refer by manual and section name** — never by path, never by number.
2. **No paths outside the manual** — not in prose, not in code, not in data.
3. **The positive form is the rule** — every domain has a manual, and the manual answers what
   the pointer carried.
4. **The manual is the door; the notes are the evidence.**
5. **Open the manual before acting** in its domain.
6. **One shape for every section**, and never skip "reference case" and "what does not resolve
   it".
7. **A shared term has one owning manual.**
