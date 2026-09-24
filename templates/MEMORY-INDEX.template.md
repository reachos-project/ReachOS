<!-- DELETE THIS COMMENT BLOCK WHEN YOU INSTANTIATE.
     On the host observed in `docs/14-runtime-observed.md`, a comment block on its own lines did
     not reach the model, but a comment trailing a line of text did — and your host may differ.
     Do not rely on either: in this template the comment is most of the file. Keep it while you
     fill the template in; remove it before the file starts loading.

  MEMORY INDEX — the hot tier. This file loads AUTOMATICALLY in every session (runtime
  capability 1, docs/13-runtime-requirements.md). Companion: {{PROJECT_ROOT}}/ACTIVE.md, built
  from templates/ACTIVE.template.md, which is read explicitly and holds work in flight.
  Never mix the two: they have opposite lifecycles.

  WHAT LIVES HERE: pointers only. One line each. The body of every entry lives in its own
  file under {{WARM_MEMORY_DIR}}/ and is read on demand.

  SIZE CEILING: {{INDEX_MAX_KB}} KB. It is functional, not aesthetic — past the host's limit
  for an auto-loaded file, the excess is dropped on the next load, silently and from the end.
  A truncated index looks exactly like a short one. Measure `wc -c` at every close.

  PRUNING: compress by REMOVING DETAIL from the explanation, never by removing pointers.
  A pointer costs one line; the entry it names costs nothing until something opens it.
  ⛔ Never prune by "nobody read this one" — an unread pointer is not an unused pointer.

  GRAMMAR — one pointer per line, exactly three parts:
      <symbol> · [Title]({{note_file}}.md) — explanation, ≤{{INDEX_EXPLANATION_MAX_CHARS}} chars
  Symbols: ⛔ never do this · ⚠️ blocking in practice · ⭐ operating rule worth the line.
  ⛔ No [INFERRED] claim in a title or on this page: position confers authority (docs/03).

  WATCHED: this file is the subject of the two-sided diff (docs/10 — opening and close).
  A line that appears here without a recorded write is surfaced at the next opening and
  reverted. That is the control; there is no gate before the write.
-->

# {{ORCHESTRATOR_NAME}} — memory index

> ⏳ Work in flight lives in `{{PROJECT_ROOT}}/ACTIVE.md`, not here.

## ⛔ Never do this

⛔ · [{{ANTIPATTERN_TITLE}}]({{antipattern_file}}.md) — {{what it destroys, and the cheaper alternative}}.

## ⚠️ Blocking in practice

⚠️ · [{{BLOCKER_TITLE}}]({{blocker_file}}.md) — {{what fails, measured how}}.

## ⭐ How we work

⭐ · [{{PRACTICE_TITLE}}]({{practice_file}}.md) — {{the rule, in one clause}}.

## Anchors

- [{{PERSON_PROFILE_TITLE}}]({{person_file}}.md) — who the system works for.
- [{{PROJECT_TITLE}}]({{project_file}}.md) — {{one line of state}}.
