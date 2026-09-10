# 03 — 3-tier memory

The team shares a persistent memory across three tiers. The guiding principle is
**markdown-as-source-of-truth**: markdown files are authoritative; any index
(vector, database) is a **derived** layer that never supersedes them.

## The three tiers

| Tier | Description | Access |
|---|---|---|
| **Hot** | User profile, preferences, rules. Loaded in **every** session. | Markdown file read at startup. |
| **Warm** | Project decisions, learned patterns, hiring history. | Markdown, queryable on-demand by read, grep, or semantic search. |
| **Cold** | Semantic historical archive + temporal knowledge graph. | Via the derived index's search/graph tools. |

## Source of truth and derived index

```
   User edits markdown
            │
            ▼
   Incremental ETL re-mines   (idempotent, by content hash)
            │
            ▼
   Vector index + graph       ← derived layer (retrieval, never SoT)
```

- The user edits **markdown**. An incremental ETL process re-mines and realigns the index.
- The ETL is **idempotent**: the same content produces the same identifier (hash), so
  re-running does not create duplicates.
- The index serves **semantic recall**; for verbatim recall (an ID, a rare term) use
  deterministic search (grep) against the SoT.

## Provenance: how a note says what it knows

A note that asserts something without saying **how it is known** decays into folklore: it
is read, believed, and repeated long after the thing it describes stopped being true.
Two fields carry that weight, and they answer different questions.

| Field | Answers | Written |
|---|---|---|
| `source:` | *how do I know this?* | once, at creation — a command, a `file:line`, a URL + date, a query and its result |
| `created:` | *since when does this note exist?* | once, and **never touched again** |

⛔ **File modification time is not a creation date.** `mtime` means "last edited", so a note
that has been revised ten times has lost its birth date entirely — and it lost it long before
anyone noticed, because nothing ever displayed the difference. If the birth date matters, it
needs a field of its own; there is nowhere else for it to live.

### Claim tags, inline

Weight-bearing statements carry how they are known, in-line:
`[MEASURED]` (with the command and the date) · `[READ]` (with the document and the date) ·
`[REPORTED]` (with who said it) · `[INFERRED]` (with what it was deduced from).

⛔ **`[INFERRED]` must never be a title or an index line.** Whoever opens a file in the
middle reads the heading, and an index loads in every session: an inference placed in a
heading becomes a fact **by position**, without anyone deciding it. The same applies to
naming a note after the *mistake* it describes — read alone, the heading instructs the
reader to repeat it. A title states what one **does**.

### Recovering dates that were never recorded

When notes predate the convention, the date is often still derivable — not from the notes,
but from **anything dated that contains them**: periodic backups, snapshots, an activity log.
A snapshot from a given date containing the note proves the note existed by then. That is an
**upper bound**, not an exact date, and it is written as one:

```yaml
created: "≤2026-05-02"   # reconstructed from a dated snapshot — UPPER BOUND
```

⚠️ **Then teach the readers about the qualifier.** A counter written as "match `created:`
followed by a literal date" reports every one of these as *missing the field* — measured
here: 312 false negatives out of 379 claimed. Match the **field**; validate the value as a
separate question. Otherwise the notes that declared their uncertainty honestly are counted
as the ones with no provenance at all.

## Write authority and after-the-fact audit

Not every tier carries the same risk, so not every write needs the same ceremony.

- **The body of a note** is retrieved on demand. A wrong one misleads whoever opens it.
- **The index line** loads in *every* session. A wrong one changes behaviour silently.

Put the control where the risk is. Bodies may be written freely; what protects the index is
not a gate before the write but **a two-sided diff** — compare against a snapshot at session
start and at session close, so any line that appeared without a recorded write is surfaced
and can be reverted. Free to write, cheap to audit, always reversible.

⚠️ **An authorisation record is not proof that the write happened.** The hook decides and
logs *before* the file is touched; if the write then fails (permissions, an immutable flag,
a sandbox denial) the log still shows it as allowed. To know whether a note exists, look at
the file — never at the audit trail alone.

### The index is a file with a grammar and a ceiling

The hot tier is not "a file with the important things in it" — it is an **index of pointers**,
and the distinction is what keeps it loadable. One line per entry: a symbol, a link, and an
explanation short enough to read at a glance. The substance lives in the linked file and is
read only when something needs it. See [`templates/MEMORY-INDEX.template.md`](../templates/MEMORY-INDEX.template.md)
for the grammar and [`examples/halcyon-consulting/memory/hot.md`](../examples/halcyon-consulting/memory/hot.md)
for it instantiated.

⚠️ **It has a size ceiling, and the ceiling is functional.** Past the host's limit for an
auto-loaded file the excess is dropped on the next load — silently, and from the end. A
truncated index is indistinguishable from a short one, so the ceiling is measured at every
close rather than discovered by a rule going missing.

⛔ **Prune by removing detail, never by removing pointers** — and never on the grounds that
nobody has opened one. A pointer costs a line; the entry it names costs nothing until it is
followed. An unread pointer is not an unused pointer: its job is to be there on the day the
question comes up.

## Flow rules

- **Promote warm → hot:** edit the hot file when a memory becomes needed in every session.
- **Demote hot → warm:** remove the reference from the hot file; the warm file stays intact.
- **Decay:** not automatic — the user validates in periodic reviews. Stale files remain
  mined in the index and continue to be retrievable.

## When to use each retrieval mechanism

| Situation | Mechanism |
|---|---|
| File known by name/path | Direct read. |
| Verbatim term, concrete ID, rare jargon | Deterministic search (grep) against the SoT. |
| Semantic/conceptual cross-corpus question | Vector search (derived index). |
| Fact about a person/project/relationship | Knowledge graph query. |
| Operational state (tasks, deliverables) | Transactional database (not the semantic index). |

> *Hard rule:* never manually write into the index information that exists in a markdown file.
> The flow is always: edit markdown → ETL re-mines → index realigns. Manual writes
> introduce *drift*.

## Failure-resilient multi-turn work

For long iterations with a risk of interruption (in-the-field debugging, very long sessions),
maintain an **iteration log** with the current state, what failed, what worked, and pending items.
Mark it as active on the **active shelf** (`templates/ACTIVE.template.md`) — not in the memory
index — so that a resumed session reads it first. Remove the mark when the iteration closes.
The shelf is where work in flight lives; the index is for stable pointers (`docs/10`).
