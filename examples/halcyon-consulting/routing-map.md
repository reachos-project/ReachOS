# Halcyon Consulting — Delegation map

<!-- Fictional instance. Domain → agent, with example requests. -->

| Request domain | Agent | Slug | Mode |
|---|---|---|---|
| Market sizing, competitive analysis, trends | Market Analyst | `market-analyst` | D |
| Client documents, proposals, reports, editing | Document Editor | `proposal-editor` | D |
| Knowledge curation, memory, freshness audit | Knowledge Curator | `knowledge-steward` | D |
| Pricing exceptions and client-relationship calls | Market Analyst | `market-analyst` | P |

**Mode** — `D`: permission already given at onboarding; Halcyon delegates without asking and
reports afterwards. `P`: only when the person asks, because the call is theirs to make.
The column answers *may I, without asking* — not *which agent*. Without it, Halcyon asks every
time, the person tires of confirming, and delegation quietly stops happening.

⚠️ Carve-out that survives a `D`, drawn by act: *running* anything that changes persistent
state on live systems (agents may prepare it, with the reversal; Halcyon runs it), the rules
themselves, Routes 1-2, and any request whose ground truth exists only in the current
conversation and is not yet in a file.

## Routing examples

| Request | Route | Destination |
|---|---|---|
| *"How many open tasks are there?"* | 1 — Direct | Halcyon responds |
| *"Fix the client name in the rules file."* | 2 — Micro-edit | Halcyon executes |
| *"Size the Iberian logistics market."* | 3 — Single-agent | `market-analyst` |
| *"Edit this client proposal."* | 3 — Single-agent | `proposal-editor` |
| *"Size market X **and** edit proposal Y."* | 5 — Parallel | `market-analyst` + `proposal-editor` |
| *"We need someone for financial modelling."* | 4 — Pipeline | New agent hiring |

## Fallback rules

1. Ambiguous domain → ask the user.
2. Non-existent agent → Route 4.
3. Vague request → ask for the desired outcome.
4. Agent error → retry with refined instructions; if it fails, escalate.
