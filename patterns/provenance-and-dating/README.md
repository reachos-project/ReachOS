# Pattern: Provenance and dating (how a note says what it knows)

> **Scope.** The pattern for making a body of written notes auditable over time. Real note
> content, internal identifiers, and store paths are outside this repo.

## Problem

A long-lived corpus of notes — decisions, learned patterns, operating rules — degrades in a
specific and predictable way: statements survive their own evidence. A note asserts that a
control is in place, that a threshold is 30, that a service is unreachable. Months later the
statement is read, believed, and acted upon, and nothing in the file says **how it was
known** or **when**. The reader cannot tell a measurement from a guess, or last week's fact
from last quarter's.

Two failure modes follow, and they compound:

- **An inference hardens into a fact.** Something deduced once is restated without its
  hedge, then cited, then treated as established.
- **A stale claim outlives its subject.** The control was removed, the endpoint changed, the
  routine was disarmed — and the note still says otherwise, with no date to make the reader
  suspicious.

## Pattern

Every weight-bearing statement carries **how it is known**; every note carries **when it was
born**. Two frontmatter fields, answering different questions, plus inline tags.

```yaml
source:   "how do I know this"      # a command, a file:line, a URL + date, a query + result
created:  "2026-05-02"              # written once, never touched again
```

| Field | Answers | Lifetime |
|---|---|---|
| `source:` | *how do I know this?* | written at creation |
| `created:` | *since when does this note exist?* | written once, **never updated** |
| `mtime` (filesystem) | *when was this last edited?* | answers neither of the above |

⛔ **Modification time is not a birth date.** A note revised ten times lost its creation date
at the first revision — and lost it invisibly, because nothing displays the difference. If
the birth date matters, it needs a field. There is nowhere else for it to live.

### Inline claim tags

`[MEASURED]` — with the command or `file:line`, **and the date**
`[READ]` — with the document or URL, **and the date**
`[REPORTED]` — with **who** said it
`[INFERRED]` — with **what** it was deduced from

⛔ **`[INFERRED]` must never be a heading or an index line.** Whoever opens a file in the
middle reads the heading; an index loads in every session. An inference placed in a heading
becomes a fact **by position**, without anyone deciding it.

⭐ The same rule bites when naming a note after the **mistake** it describes. *"Classify once
and don't revisit"* is a perfectly good label for a defect — and, read alone in a list of
titles, it instructs the reader to commit it. **A title states what one does.**

⭐ **Promotion from `[REPORTED]` to `[READ]` requires corroboration independent of the
source**, and the reason for promoting is written down. A delegate's report on its own stays
`[REPORTED]`, however confident it sounds.

## Recovering dates that were never recorded

When a corpus predates the convention, the dates are usually **not** lost — they are simply
not in the notes. They are in anything **dated that contains the notes**: periodic backups,
snapshots, an activity log, a version-control history. A dated artefact from a given day
that contains the note proves the note existed by then.

That is an **upper bound**, not an exact date, and it must be written as one:

```yaml
created: "≤2026-05-02"   # reconstructed from a dated snapshot — UPPER BOUND
```

⚠️ **Two traps, both measured in practice:**

**1. The excluded source.** Backups and snapshots are correctly dismissed as evidence of
*where information came from* — a backup proves the note was there, not its origin. When the
question changes to *when did this exist*, the very same artefacts become the best available
evidence. An exclusion is valid only for the question that motivated it; when the question
changes, reopen the drawer. Here, a corpus declared "undateable — the information no longer
exists anywhere" turned out to be dateable for **82 %** of cases, from artefacts already on
disk.

**2. The counter that cannot read the qualifier.** A check written as *"match `created:`
followed by a literal date"* reports every `≤`-bounded note as **missing the field**.
Measured here: 312 false negatives, reported as a 42 % gap in a corpus whose real gap was
7 %. The notes that declared their uncertainty honestly were counted as the ones with no
provenance at all.

⭐ **Match the field; validate the value as a separate question.** Merging the two makes the
qualified value disappear inside "absent" — and the effect is perverse: it penalises exactly
the epistemic honesty the convention was introduced to produce.

## What makes the convention stick

⛔ **Discipline alone does not produce compliance; validation does.** In this corpus the
`source:` field reached **75 %** on the one note type whose creation path validated it, and
**4 %** on the types where it was merely expected. The inline claim tags, which nothing
validates anywhere, sit at **19 %** among notes written after the convention was adopted.

If a provenance field matters, put a check on the path that creates the note. A counter that
reports and never blocks measures adoption; it does not cause it.

## Principles

1. **Every weight-bearing claim carries how it is known** — measured, read, reported, inferred.
2. **A birth date needs its own field** — `mtime` means "last edited" and always will.
3. **An upper bound is a real answer** — `≤date` beats both an invented date and a blank.
4. **Never put an inference, or the name of a mistake, in a heading** — position confers authority.
5. **Readers must know the corpus's qualifiers** — or they will count honesty as absence.
6. **Validate on the creation path** — what is only expected is not done.
