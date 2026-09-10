---
source: "delivery log, three incidents in 2026 (`projects/quality/`)"
created: "2026-05-11"
---

# Render the document before it leaves

**A document is not delivered until it has been rendered and looked at.**

## What is known, and how

- `[MEASURED]` three client decks shipped in 2026 with tables broken by the conversion step —
  delivery log, 2026-05-11.
- `[INFERRED]` the converter is the common factor, not the authoring tool — deduced from the three
  files sharing no template and one pipeline stage.

## Why it matters

The defect is invisible in the source format and obvious in the output, so nothing but opening the
rendered file catches it. It is a check, not a judgement.

## What would change this

A pipeline that renders and diffs automatically, with the diff surfaced before delivery.
