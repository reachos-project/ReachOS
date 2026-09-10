---
source: "{{HOW_THIS_IS_KNOWN}}"     # a command, a file:line, a URL + date, a query + its result
created: "{{YYYY-MM-DD}}"           # written once, NEVER updated — mtime means "last edited"
---

<!--
  Memory note template — the BODY of one index entry. The pointer to this file lives in
  MEMORY-INDEX.template.md; this file carries the substance and is read on demand.

  Filename prefix declares the type and decides how much ceremony the write needs:
    reference_   stable knowledge, provenance-validated on the creation path
    feedback_    a preference or a correction from the person
    project_     the state of a piece of work
    workflow_    a procedure
    watch_       something external to keep an eye on

  ⛔ A reconstructed date is written as an UPPER BOUND and says so:
       created: "≤2026-05-02"   # reconstructed from a dated snapshot — UPPER BOUND
     Any counter over this field must match the FIELD and validate the value separately,
     or every honestly-qualified note is reported as having no provenance at all.
-->

# {{NOTE_TITLE}}

<!-- ⛔ The title states what one DOES. Never the name of the mistake, never an inference:
     whoever opens a file in the middle reads the heading, and position confers authority. -->

**{{The claim, in one sentence.}}**

## What is known, and how

- `[MEASURED]` {{the finding}} — {{the command or `file:line`}}, {{date}}.
- `[READ]` {{the finding}} — {{the document or URL}}, {{date}}.
- `[REPORTED]` {{the finding}} — {{who said it}}.
- `[INFERRED]` {{the finding}} — deduced from {{what}}.

<!-- ⭐ Promotion from [REPORTED] to [READ] needs corroboration independent of the source,
     and the reason for promoting is written here. A delegate's own report stays [REPORTED],
     however confident it sounds. -->

## Why it matters

{{What breaks if this is forgotten, and what to do instead.}}

## What would change this

{{The observation or event that would make the note wrong. If nothing could, say so.}}
