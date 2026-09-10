<!--
  ACTIVE.md — the ACTIVE SHELF: work in flight, read explicitly at every session start.
  It does NOT go through the automatic memory load; the opening reads it on purpose.
  Companion: the memory index (stable pointers). Never put doctrine or lessons here —
  when an entry closes, its lesson moves to a memory and the entry becomes a one-line pointer.

  PRUNING RULE: what is CLOSED becomes a 1-2 line pointer as soon as the lesson lives in a
  memory. Compress by REMOVING DETAIL, never by rewriting claims. Fixing an internal
  contradiction is a SEPARATE act and is declared as such.

  SIZE CEILING: {{SHELF_MAX_KB}} KB. Above it, whatever watches this file for unexpected
  changes stops computing — the shelf becomes unguarded. Measure `wc -c` at every close;
  working target well below the ceiling. The growth rate per day is the signal, not the size.

  SENSITIVE DATA FORBIDDEN: no health/legal/financial personal data, no secrets, no tokens,
  no credentials. Every subagent can reach this file through its inline returns.
-->

# Work in flight — read FIRST

<!--
  ═══════════════════════════════════════════════════════════════════════════
  THE GRAMMAR — this is what makes the shelf work; without it the shelf is prose.

  1. UNIT = BLOCK. An entry is a paragraph: it starts with a state symbol and runs until a
     blank line, a heading, the next state symbol at line start, a table row, or `---`.
     Anything that reads the shelf reads BLOCKS, never lines. A verifier that matches the
     symbol on a line and looks for evidence on THAT line will miss the evidence sitting on
     the second line of the same paragraph — and will call the whole shelf "unverifiable".

  2. STATE SYMBOL — first character of the block. It is an INSTRUCTION to the opening:

     ⏳  in progress — work owed by the assistant. This is the task list.
     ⏰  has a MOMENT — verify or act at a given time/event. The moment itself lives in the
         clock index (see docs/09-clocks-and-routines.md), not in this prose; the block names the clock.
     📋  decision pending — the user's to make. Surface it; do not act.
     ⏸   paused by the user. Do not touch; do not re-litigate.
     🔴  open and important, no trigger yet. Read first.
     🟢 / ✅  CLOSED — pointer only. Generates no work; leaves at the next pruning.
     ⛔  hard constraint or "do NOT do this" — attaches to a block, is not a state.
     ⚠️  caveat/uncertainty — attaches to a block, is not a state.

     A `## ⏳ Section title` heading is TAXONOMY, not an entry. Verifiers exclude headings.

  3. EVERY OPEN BLOCK CARRIES AN ANCHOR the world can check — at least one of:
       [[memory-slug]]            (a memory that exists)
       `path/to/artefact`         (a file that exists; anchored path, not a bare basename)
       `clock-slug`               (clocks.slug in the store; state armed -> acked -> retired)
       `routine-id`               (routines.id in the store; armed_since set = it has fired once)
     Both tables are defined in examples/db/schema.example.sql. The slug lives here; the STATE
     lives there — a date written only in this prose is the failure docs/09 exists to prevent.
       #NNN                       (a task id — weak anchor: most tasks close the same day)
     Blocks without an anchor are legitimately UNVERIFIABLE: a question waiting on the user,
     a decision not yet taken, a judgement with no artefact. Name that class; keep it small.

  4. THE SYMBOL MUST TELL THE TRUTH. A block that still opens with ⏳/⏰ while its clock is
     already acked, or its artefact already drained, is CLOCK_DRIFT / DANGLING — the sweep
     will flag it. Closing the work and not flipping the symbol is the most common defect.
     When you close, flip the symbol on the SAME edit.

  5. WHAT THE OPENING DOES WITH IT (see docs/10-session-lifecycle.md): reads the shelf explicitly; the sweep
     classifies each block by DISCOVERY (does the anchor resolve? did the clock close?) and
     reports one line — `sweep: N · a OK · b unanchored · c actionable` — and shouts
     `CRITERION BLIND` if it resolved zero anchors in a non-empty shelf. Silence in the nominal
     state is the goal; a verifier that never fires has stopped verifying.
  ═══════════════════════════════════════════════════════════════════════════
-->

## ✅ {{DATE}} — closed (pointers; detail in the activity log)

🟢 **{{CLOSED_ITEM_TITLE}}** — {{one line: what closed, what it measured}}. Lesson →
[[{{memory-slug}}]].

## ⏳ {{DATE}} — {{OPEN_TOPIC}}

⏳ **{{OPEN_ITEM_TITLE}}** — {{what is owed, by whom}}. Artefact: `{{path/to/artefact}}`.
⚠️ {{caveat, if any — on its own line inside the same block}}.
⏰ **{{CLOCK_TITLE}}** — clock `{{clock-slug}}` ({{what fires and what to do when it does}}).
📋 **Pending decision:** {{the question, in one sentence, and the recommendation first}}.

## 🔴 {{OPEN_INCIDENT}}

🔴 {{what is broken, measured how, since when}}. First place to look: `{{path}}`.
⛔ {{what must NOT be done meanwhile}}.

---

## 📁 Closed — archive
📁 `{{path/to/ACTIVE_ARCHIVE.md}}` — pointers only, no clocks.
