---
name: quality-gate
description: "Blocking checklist run on a deliverable before it leaves Halcyon. Nine structural items (any failure blocks) and three content items (warnings). Logs the result for quality metrics."
user-invocable: true
allowed-tools: ["Read", "Bash", "Grep"]
disallowed-tools: ["Write", "Edit"]
model: a lightweight model — this is a checklist, not a judgement call
---

<!-- FICTIONAL instance of templates/skills/skill.template/SKILL.md, for Halcyon Consulting. -->

# Quality gate

## When to run

- **Mandatory** before anything reaches a client, a prospect, or a public channel.
- **Mandatory** for any deliverable flagged quality-sensitive (decks, one-pagers, the website).
- **Optional** for internal drafts and working notes.

## Input

- **Argument 1:** path to the deliverable.
- **Argument 2 (optional):** `--quality-sensitive`, raising the bar from 10/12 to 11/12.

## Procedure

1. **Read the file whole.** A gate run on a summary measures the summary.
2. **Score the nine structural items** (`docs/04-quality-gate.md`). Each failure is a
   **blocker** — record the item number, not just the count.
3. **Score the three content items.** These are warnings and never block on their own.
4. **Render it** if the output format is not plain text — a broken table is invisible in the
   source and obvious in the render. See [[feedback_render_before_delivery]].
5. **Check every figure carries a source and a date** ([[reference_number_provenance_rule]]);
   an unsourced number fails **content check 3 (coherence)**, and is raised as a blocker by house
   rule rather than by the structural list — none of the nine structural items covers provenance.
6. **Apply the decision ladder** — first branch that matches wins, per `docs/04`.

## Output

```
=== quality-gate: <path> ===
Structural: 9/9   blockers: 0
Content:    2/3   warning: item 11 — two follow-ups have no owner
Total:      11/12
Decision:   SHIP
```

## Logging

Write `structural_score`, `content_score`, `blockers`, `revision_rounds` and `tags` to
`deliverables` in the store (`examples/db/schema.example.sql`). Recording only the total loses
the case the gate exists for: a full structural score with one blocker still in it.

## Notes

⛔ **Two correction rounds, then escalate.** A third round means the brief was wrong, not the
draft — take it back to the person rather than polishing.
⚠️ **Watch the divergence signal.** A deliverable that scores 12/12 and leaves the client
lukewarm is not a scoring error; it is the checklist failing to measure something. Log it and
revise the gate, not the score.
