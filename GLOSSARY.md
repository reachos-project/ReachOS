# Glossary

Terms used consistently throughout this repo.

| Term | Definition |
|---|---|
| **Coordinator (virtual CEO)** | The central agent that interprets requests, delegates, and synthesises. Does not perform operational work. |
| **Specialist agent** | A persona with its own domain (e.g., analyst, editor, curator). Receives delegations from the coordinator. |
| **Route** | The routing class of a request. There are 5 (see `docs/02-smart-routing.md`). |
| **Delegation** | Transfer of a task from the coordinator to an agent, logged for traceability. |
| **Hot / warm / cold memory** | Three persistence tiers: always-loaded / on-demand / semantic archive. |
| **Source of truth (SoT)** | The authoritative artefact. In the model described here, these are markdown files; indexes are derived. |
| **Vector index** | A semantic retrieval layer built on top of the SoT; never replaces it. |
| **ETL incremental** | The process that re-mines the SoT into the index in an idempotent way. |
| **Quality gate (QG)** | A blocking checklist run before delivering a deliverable. |
| **Deliverable** | The final artefact produced by an agent and handed to the user. |
| **Guardrail** | An automatic control that authorises or blocks an action before it occurs. |
| **Defence-in-depth** | The stacking of several independent guardrail layers. |
| **Tier-1 (critical paths)** | Configuration/identity files whose modification requires hardened protection. |
| **Heartbeat** | A periodic confined daemon that performs checks and escalates by cost. |
| **Egress-allowlist** | A closed list of network destinations that a confined worker is permitted to contact. |
| **Control-via-audit** | The philosophy of free + logged + reversible writes, rather than mandatory prior approval. |
| **Placeholder / token** | A `{{TOKEN}}` marker to be replaced with a concrete value when instantiating a template. |
