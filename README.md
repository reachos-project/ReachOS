# ReaCH — Reference Architecture for Coordinated Hives

**ReaCH** (*Reference Architecture for Coordinated Hives*) is a **reference architecture**
for orchestrating a team of specialised AI agents under a central coordinator (a "virtual CEO").
It documents the patterns that an organisation can study and reuse: request routing, quality
control, persistent memory, security guardrails, and confined automation.

> **Notice.** This is a *reference architecture*, not production-ready software. All names,
> companies, agents, paths, and numbers are **fictional and illustrative**. Adapt the templates
> to your context before use.

---

## What it is

The core pattern is simple: a **coordinator** interprets the user's request, **delegates** to
the appropriate specialist agent, **synthesises** the result, and delivers it. The coordinator
never does the operational work — it orchestrates.

```
User → Coordinator → Specialist agent → Coordinator → User
```

Five pattern families sit on top of this skeleton:

1. **Orchestration** — governance rules for the coordinator (delegation, chain of command, traceability).
2. **Smart routing** — classifying each request into one of 5 routes.
3. **3-tier memory** — hot / warm / cold, with markdown as the source of truth and a derived vector index.
4. **Quality gate** — a blocking checklist before any delivery.
5. **Guardrails + confined automation** — defence-in-depth, a heartbeat daemon, workers with an egress-allowlist.

---

## Mental map

- **Routes** (`docs/02-smart-routing.md`): Direct · Micro-edit · Single-agent · Pipeline · Parallel.
- **Memory** (`docs/03-memory-3tier.md`): hot (every session) · warm (on-demand) · cold (semantic archive).
- **Guardrails** (`docs/05-guardrails.md`): 3 layers — matcher → content inspection → backups.

---

## Repo structure

| Folder | Contents |
|---|---|
| `docs/` | The "why" and "how" of each pattern, in prose. |
| `templates/` | Parameterisable skeletons with `{{TOKEN}}` placeholders. |
| `examples/` | A complete fictional instance ("Atlas Consulting"), an example schema, and guardrail skeletons. |
| `patterns/` | Deep engineering of the security patterns (defence-in-depth, heartbeat, confined worker, tripwire/baseline, reciprocal watchdog). |
| `NOTICE` | Upstream lineage attribution (see Acknowledgments below). |

## How to use the templates

Each template uses `{{UPPERCASE_IN_BRACES}}` tokens. Replace them with your own values:

| Token | Meaning | Example |
|---|---|---|
| `{{PROJECT_ROOT}}` | Project root | `/opt/atlas/assistant` |
| `{{ORCHESTRATOR_NAME}}` | Coordinator name | `Atlas` |
| `{{OWNER_HANDLE}}` | Human user | `owner` |
| `{{AGENT_SLUG}}` | An agent's slug | `market-analyst` |
| `{{NOTIFY_CHANNEL}}` | Alert channel | `<your-notify-url>` |
| `{{DB_PATH}}` | State database | `./state/assistant.db` |

## What this repo does NOT contain

By design, the following are **excluded**: any secrets or credentials, real internal personas,
personal paths or hostnames, the real topology of security controls (detection rules,
baselines), and user data. The repo conveys **patterns**, not live configurations.

## Acknowledgments / Lineage

This architecture did not emerge from nothing — it descends, with credit and gratitude, from two
upstream projects. It is a **clean-room rewrite** (patterns re-expressed from concept, with
generic placeholders and fictional examples), not a copy of either.

- **[freskhu/genesis](https://github.com/freskhu/genesis)** (Apache-2.0) — the **functional
  structure** of this project descends from `genesis`: the virtual-CEO coordinator model,
  delegation to specialist agents, smart routing, the quality gate, the skills/hooks layout,
  and the traceability store schema conventions. The author shared the structure with our team
  privately, before the repository was published. Where we reproduce upstream names or schema
  nomenclature, it is **conscious and attributed**.

- **[MemPalace/mempalace](https://github.com/MemPalace/mempalace)** (MIT) — the **3-tier
  memory system** and its taxonomy (the semantic "palace" and the vocabulary of wings / rooms /
  halls / drawers, mining and traversal, the diary, and the bitemporal knowledge graph) inherit
  concepts from `mempalace`, which was the original engine for our memory layer before an
  internal successor was built. MIT is compatible with Apache-2.0.

Formal attribution detail is in the [`NOTICE`](NOTICE) file. Both licences are permissive and
mutually compatible; credit is given here visibly and generously, out of obligation
(Apache-2.0) and out of acknowledgment.

## Licences

This repository uses a dual licence:

- **Code, templates, and skeletons** (`templates/`, `examples/`):
  [Apache License 2.0](LICENSE)
- **Documentation** (`docs/`, `patterns/`, `README.md`, `GLOSSARY.md`, `CONTRIBUTING.md`):
  [CC-BY-4.0](LICENSE-docs)

The [`NOTICE`](NOTICE) file identifies the upstreams that gave rise to this architecture and
declares the clean-room nature of this repository.
