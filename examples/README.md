# Example — Atlas Consulting

A **fictional and complete** instance of this repo's templates, to serve as a reference.
"Atlas Consulting" is an invented consultancy; the coordinator is called **Atlas** and has
three agents. All names, people, numbers, and paths here are **invented** and exist only to
illustrate how the patterns are instantiated.

## Contents

| File | What it illustrates |
|---|---|
| `atlas-consulting/ORCHESTRATOR.md` | Coordinator file instantiated from the template. |
| `atlas-consulting/routing-map.md` | Delegation map domain → agent. |
| `atlas-consulting/agents/market-analyst.md` | Market analysis agent (fictional persona). |
| `atlas-consulting/agents/proposal-editor.md` | Writing/editing agent (fictional persona). |
| `atlas-consulting/agents/knowledge-steward.md` | Knowledge curation agent (fictional persona). |
| `db/schema.example.sql` | Conceptual schema of the transactional store (traceability). |

## How to use

Read these files side by side with the `templates/` to see each `{{TOKEN}}` replaced with a
concrete value. Then create your own instance from the templates — **do not** copy Atlas
Consulting as if it were production.
