# ReachOS — a Reference Architecture for Coordinated Hives

**ReachOS** (*Reference Architecture for Coordinated Hives*) is a **reference architecture**
for orchestrating a team of specialised AI agents under a central coordinator (a "virtual CEO").
It documents the patterns that an organisation can study and reuse: request routing, quality
control, persistent memory, security guardrails, and confined automation.

> **Notice.** This is a *reference architecture*, not production-ready software. Names, companies,
> agents, personas, and paths are **fictional and illustrative**. Adapt the templates to your
> context before use.
>
> ⭐ **Numbers are different, and deliberately so.** Any figure introduced as a **measurement**
> — *"measured in one deployment"*, *"measured here"*, and the like — is **real**: it comes from a
> single deployment, and carries whatever scope that sentence states. Figures inside examples and
> templates are illustrative like everything else around them. When the two could be confused,
> the measurement says so and the illustration does not.
>
> **The largest of these** is [`docs/14-runtime-observed.md`](docs/14-runtime-observed.md), an
> independent field report on the observed behaviour of **Claude Code**
> (Anthropic PBC), the runtime this architecture was developed and exercised on. Each figure is
> bounded by date, by version range, and by the single operator, platform, and configuration it
> came from, and speaks as of that chapter's publication date. That chapter is field notes, not
> illustration: **not a vendor statement, not authorised or endorsed by Anthropic PBC, and not
> generalisable beyond what it states it measured.**

---

## What it is

The core pattern is simple: a **coordinator** interprets the user's request, **delegates** to
the appropriate specialist agent, **synthesises** the result, and delivers it. The coordinator
never does the operational work — it orchestrates.

```
User → Coordinator → Specialist agent → Coordinator → User
```

**Start here, in this order:**

1. [`docs/13-runtime-requirements.md`](docs/13-runtime-requirements.md) — the six things the
   host must provide, and the order of instantiation. Read it before copying any template:
   it is what decides whether your stack can host this at all.
2. [`templates/onboarding-interview.md`](templates/onboarding-interview.md) — the first-run
   interview. Without it the system has a routing map and no idea who it works for.

Ten pattern families sit on top of this skeleton:

1. **Orchestration** — governance rules for the coordinator (delegation, chain of command, traceability).
2. **Smart routing** — classifying each request into one of 5 routes, and declaring per domain whether delegation needs to be asked for at all.
3. **3-tier memory** — hot / warm / cold, with markdown as the source of truth and a derived vector index.
4. **Quality gate** — a blocking checklist before any delivery.
5. **Guardrails + confined automation** — defence-in-depth, a heartbeat daemon, workers with an egress-allowlist, and a two-way operator channel that does not weaken the sandbox.
6. **Provenance and dating** — how a note records what it knows, how it knows it, and since when; and how to recover dates that were never written down.
7. **Retiring instruments** — what to do with a script, hook, or routine that is no longer in force, so that it stops being read as if it were.
8. **Time** — clocks (fire once, then die) versus routines (recur), why their state belongs in a store rather than in prose, and why "reminded" is not "done".
9. **Session lifecycle and review culture** — how a session opens and closes, what gets logged about the working relationship, and how to keep an advisor from becoming a mirror.
10. **Host substrate** — persistent sessions that survive disconnection, the OS sandbox beneath the rule layer, and scheduled background jobs: the machine-level realities that decide whether any of the above holds.

---

## Mental map

- **Hive** (the name): one coordinator, many specialists, one shared memory — a *hive* in the
  sense of coordinated division of labour, not of swarm autonomy. Every agent answers to the
  coordinator; none acts on its own initiative.
- **Routes** (`docs/02-smart-routing.md`): Direct · Micro-edit · Single-agent · Pipeline · Parallel.
- **Runtime** (`docs/13-runtime-requirements.md`): six host capabilities; interception and confinement are different layers.
- **Runtime, observed** (`docs/14-runtime-observed.md`): field notes on how one host actually behaves — comments in loaded files are not free, an absent tool looks like a blocked one, and history is not reliably append-only.
- **Memory** (`docs/03-memory-3tier.md`): hot (every session) · warm (on-demand) · cold (semantic archive).
- **Memory index** (`templates/MEMORY-INDEX.template.md`): pointers only, one line each, with a ceiling — the shelf's stable twin.
- **Guardrails** (`docs/05-guardrails.md`): 3 layers — matcher → content inspection → backups.
- **Provenance** (`patterns/provenance-and-dating/`): `source:` answers *how do I know this*; `created:` answers *since when*; `mtime` answers neither.
- **Retirement** (`patterns/retiring-instruments/`): drain first, mark only what cannot be drained, verify by discovery.
- **Time** (`docs/09-clocks-and-routines.md`): a clock dies when answered; a routine never dies. Both live in the store, not in prose.
- **Sessions** (`docs/10-session-lifecycle.md`): one gather at each end; work-in-flight lives apart from stable memory.
- **Review** (`patterns/adversarial-review/`): question the premise once, before starting — and never verify it by grepping the document.
- **Delegation mandate** (`docs/02-smart-routing.md`): goal · where the ground truth lives · declared unknowns · source hierarchy · return format · out-of-scope line.
- **Source hierarchy** (`templates/agents/agent.template.md`): own memory → own artefacts → authoritative domain sources → scientific literature → open web. Never let the last answer for the middle two.
- **Execution host** (`docs/11-persistent-sessions.md`): one execution host, many presentation surfaces — and environment variables a persistent server froze days ago.
- **Handing back** (`patterns/handoff-to-human/`): what an agent owes the person when it stops —
  the state, the reason, and the one next action.
- **Sandbox** (`docs/12-os-sandbox.md`): deny wins and is inherited; removing an allow does not deny; two probes per change, one denied and one allowed.
- **Daemons** (`patterns/scheduled-daemons/`): the payload that runs is not the file you are reading.

---

## Repo structure

| Folder | Contents |
|---|---|
| `docs/` | The "why" and "how" of each pattern, in prose. |
| `templates/` | Parameterisable skeletons with `{{TOKEN}}` placeholders. |
| `examples/` | A complete fictional instance ("Halcyon Consulting"), an example schema, and guardrail skeletons. |
| `patterns/` | Deep engineering of each pattern: defence-in-depth, heartbeat, confined worker, tripwire/baseline, apply preflight, reciprocal watchdog, confined agent messaging, provenance and dating, retiring instruments, adversarial review, handoff to human, remote autonomous sessions, scheduled daemons. |
| `NOTICE` | Upstream lineage attribution (see Acknowledgments below). |

## How to use the templates

Each template uses `{{UPPERCASE_IN_BRACES}}` tokens. Replace them with your own values:

| Token | Meaning | Example |
|---|---|---|
| `{{PROJECT_ROOT}}` | Project root | `/opt/halcyon/assistant` |
| `{{ORCHESTRATOR_NAME}}` | Coordinator name | `Halcyon` |
| `{{OWNER_HANDLE}}` | Human user | `owner` |
| `{{AGENT_SLUG}}` | An agent's slug | `market-analyst` |
| `{{NOTIFY_CHANNEL}}` | Alert channel | `<your-notify-url>` |
| `{{SHELF_MAX_KB}}` | Size ceiling of the active shelf (`templates/ACTIVE.template.md`), above which its change-watcher stops computing | `64` |
| `{{INDEX_MAX_KB}}` | Size ceiling of the memory index (`templates/MEMORY-INDEX.template.md`); past the host's limit for an auto-loaded file the excess is dropped silently | `24` |
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

## Trademarks

Claude, Claude Code, and Anthropic are trademarks of Anthropic PBC, used in this repository
solely to identify the product observed in
[`docs/14-runtime-observed.md`](docs/14-runtime-observed.md). This project is not affiliated with,
authorised by, endorsed by, or sponsored by Anthropic PBC. All other trademarks are the property
of their respective owners. See [`NOTICE`](NOTICE).

## Licences

This repository uses a dual licence:

- **Code, templates, and skeletons** (`templates/`, `examples/`):
  [Apache License 2.0](LICENSE)
- **Documentation** (`docs/`, `patterns/`, `README.md`, `GLOSSARY.md`, `CONTRIBUTING.md`):
  [CC-BY-4.0](LICENSE-docs)

The [`NOTICE`](NOTICE) file identifies the upstreams that gave rise to this architecture and
declares the clean-room nature of this repository.
