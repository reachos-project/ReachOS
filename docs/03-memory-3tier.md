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
Mark it as active in a top-level index so that a resumed session reads it first.
Remove the mark when the iteration closes.
