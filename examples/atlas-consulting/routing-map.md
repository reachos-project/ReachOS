# Atlas Consulting — Delegation map

<!-- Fictional instance. Domain → agent, with example requests. -->

| Request domain | Agent | Slug |
|---|---|---|
| Market sizing, competitive analysis, trends | Market Analyst | `market-analyst` |
| Client documents, proposals, reports, editing | Document Editor | `proposal-editor` |
| Knowledge curation, memory, freshness audit | Knowledge Curator | `knowledge-steward` |

## Routing examples

| Request | Route | Destination |
|---|---|---|
| *"How many open tasks are there?"* | 1 — Direct | Atlas responds |
| *"Fix the client name in the rules file."* | 2 — Micro-edit | Atlas executes |
| *"Size the Iberian logistics market."* | 3 — Single-agent | `market-analyst` |
| *"Edit this client proposal."* | 3 — Single-agent | `proposal-editor` |
| *"Size market X **and** edit proposal Y."* | 5 — Parallel | `market-analyst` + `proposal-editor` |
| *"We need someone for financial modelling."* | 4 — Pipeline | New agent hiring |

## Fallback rules

1. Ambiguous domain → ask the user.
2. Non-existent agent → Route 4.
3. Vague request → ask for the desired outcome.
4. Agent error → retry with refined instructions; if it fails, escalate.
