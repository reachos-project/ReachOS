# Example — Halcyon Consulting

A **fictional and complete** instance of this repo's templates, to serve as a reference.
"Halcyon Consulting" is an invented consultancy; the coordinator is called **Halcyon** and has
three agents. All names, people, numbers, and paths here are **invented** and exist only to
illustrate how the patterns are instantiated.

## Contents

| File | What it illustrates |
|---|---|
| `halcyon-consulting/ORCHESTRATOR.md` | Coordinator file instantiated from the template. |
| `halcyon-consulting/routing-map.md` | Delegation map domain → agent. |
| `halcyon-consulting/ACTIVE.md` | The active shelf instantiated: one closed section, one open topic with anchor/clock/decision, one incident, one paused item — the grammar of `templates/ACTIVE.template.md` in use. |
| `halcyon-consulting/memory/hot.md` | The memory index instantiated: pointers only, one line each, with the bodies beside it. |
| `halcyon-consulting/memory/*.md` | The bodies those pointers name — each an instance of `templates/memory-note.template.md`, with `source:` and `created:`. |
| `halcyon-consulting/agents/market-analyst.md` | Market analysis agent (fictional persona) — **the reference instance**. |
| `halcyon-consulting/agents/proposal-editor.md` | Writing/editing agent (fictional persona). |
| `halcyon-consulting/agents/knowledge-steward.md` | Knowledge curation agent (fictional persona). |
| `halcyon-consulting/rules/autonomy-boundary.md` | Rule 8 instantiated from `templates/rules/rule.template.md`. |
| `halcyon-consulting/skills/quality-gate/SKILL.md` | The quality gate instantiated from `templates/skills/skill.template/`. |
| `halcyon-consulting/narrative-log.md` | The working-relationship log — corrections, not deliverables. |
| `halcyon-consulting/projects/` | Stubs, so that every anchor on the shelf resolves to a real file. |
| `db/schema.example.sql` | Conceptual schema of the transactional store (traceability). |

⚠️ **The three agents are not equivalent, deliberately.** `market-analyst` is the **reference
instance**: it carries every doctrinal section of `templates/agents/agent.template.md` — the
source hierarchy, the advisory conduct with its confidence block, and the inline-return rule.
`proposal-editor` and `knowledge-steward` are **reduced**: identity, mission, expertise and
constraints only. Read `market-analyst` to see what a full instantiation looks like; read the
other two to see how short a working agent file can be once the doctrine is settled elsewhere.

## How to use

Read these files side by side with the `templates/` to see each `{{TOKEN}}` replaced with a
concrete value. Then create your own instance from the templates — **do not** copy Halcyon
Consulting as if it were production.
