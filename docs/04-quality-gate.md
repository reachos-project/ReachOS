# 04 — Quality gate

Before any deliverable goes out to the user or to third parties, a blocking checklist runs.
The idea is simple: **if it does not pass, it does not ship**. The result is logged to
enable quality metrics over time.

## When to run

- **Mandatory** before any delivery to the user, stakeholders, or external destinations.
- **Mandatory** for *quality-sensitive* deliverables (visual, for third parties, for publication).
- **Optional** for internal drafts and private notes.

## Structural checklist (blocking)

Each failing item blocks delivery:

1. **Naming** — follows the naming convention and is in the right place; name is unique (no collision).
2. **Metadata** — frontmatter/properties filled in (title, date, author).
3. **No adjacent duplication** — no paragraph is identical to the next (a common conversion artefact).
4. **Image flow** — each image has a unique caption and a coherent position (not immediately after an empty heading).
5. **Annotation conventions** — coordinator annotations are marked with their source; never confusable with the author's voice.
6. **Language and style** — consistent language, correct spelling, appropriate tone, expected typography.
7. **Cross-references** — internal links point to files that exist; paths work.
8. **Tables and boxes** — well formatted; consistent column count; lists without orphaned items.
9. **No LLM markers** — no separators or formulaic phrases typical of automated generation.

## Content checklist (warning, non-blocking)

10. **Density** — no empty sections or sections containing only *TODO*; no unresolved placeholders.
11. **Actionability** — follow-up actions have an owner and a deadline; open questions are marked.
12. **Style consistency** — aligned with the style guide applicable to the register (formal, technical, etc.).

## Score and decision

The two axes decide differently, and conflating them is what makes a gate unusable:

- **Structural (X / 9) is all-or-nothing.** Any failed item is a **blocker**. The number is for
  the record; the decision is `blockers == 0` or not. "8 out of 9" does not ship.
- **Content (Y / 3) is the number that decides.** These are warnings, and the count of them is
  the difference between shipping and looking again.
- **The total (Z = X + Y, out of 12) is reporting convenience only.** Never decide from it —
  with zero blockers X is always 9, so Z is just `9 + Y` wearing a bigger denominator.

```
Decision — the FIRST branch that matches wins, and they do not overlap:

  1. blockers > 0                            → FIX FIRST
  2. quality-sensitive  and  Z < 11          → FIX FIRST, then human visual review
  3. Z < 10                                  → REVIEW
  4. otherwise                               → SHIP
```

- Base rule: **zero blockers, and at least one content item passing** — which is what
  "minimum 10/12" means once the arithmetic is written out.
- For *quality-sensitive* deliverables (visual, third-party, publication): **minimum 11/12**,
  i.e. at most one content warning, plus human visual review.
- Maximum 2 correction rounds before escalating to the user.

Record `structural_score`, `content_score` and `blockers` separately in the store — a single
total cannot express "12/12 with one blocker", which is the case the gate exists to catch. See
[`examples/db/schema.example.sql`](../examples/db/schema.example.sql) and an instantiated gate
at [`examples/halcyon-consulting/skills/quality-gate/SKILL.md`](../examples/halcyon-consulting/skills/quality-gate/SKILL.md).

## Logging and metrics

After running the checklist, log the result (structural score, content score, number of
iterations, tags). This feeds a quality KPI. A useful signal: **divergence** between a clean
gate result (12/12 total, zero blockers) and the user's subjective satisfaction (e.g., 6/10) indicates a
systemic failure that the checklist does not capture — a trigger to refine the gate itself.

## Language verification (example)

A language gate can be automated. Example for a language with mandatory accentuation:
count accented characters in a long document; a result close to zero in a text that
should have them is a linguistic *fail*. Adapt to your target language.
