# Glossary

Terms as used in this repo. Where a term carries a second sense somewhere, both are listed and
the collision is named — a glossary that promises consistency it does not have is worse than
one that maps the ambiguity.

| Term | Definition |
|---|---|
| **Coordinator (virtual CEO)** | The central agent that interprets requests, delegates, and synthesises. Does not perform operational work. |
| **Specialist agent** | A persona with its own domain (e.g., analyst, editor, curator). Receives delegations from the coordinator. |
| **Route** | The routing class of a request. There are 5 (see `docs/02-smart-routing.md`). |
| **Delegation** | Transfer of a task from the coordinator to an agent, logged for traceability. |
| **Delegation mode (`D` / `P`)** | Per-domain declaration of whether the coordinator may delegate without asking (`D`, permission already given) or only on explicit request (`P`). Answers *may I, without asking* — not *which agent*. |
| **Ground-truth carve-out** | The rule that a request is not delegated while its evidence exists only in the current conversation. A delegate cannot verify what it cannot open. |
| **Exclusion by act** | What stays with the coordinator even when delegation is pre-authorised is decided by the act, not the domain: *running* anything that changes persistent state or restarts a service on live infrastructure. Reading, designing and writing the exact command, with its reversal, are delegated. |
| **Hot / warm / cold memory** | Three persistence tiers: always-loaded / on-demand / semantic archive. |
| **Source of truth (SoT)** | The authoritative artefact, and it differs by kind: markdown files for knowledge and reasoning, the transactional store for state (clocks, routines, tasks, deliverables — `docs/09-clocks-and-routines.md`). Indexes are derived from either, and are authoritative for nothing. |
| **Vector index** | A semantic retrieval layer built on top of the SoT; never replaces it. |
| **ETL incremental** | The process that re-mines the SoT into the index in an idempotent way. |
| **Quality gate (QG)** | A blocking checklist run before delivering a deliverable. |
| **Deliverable** | The final artefact produced by an agent and handed to the user. |
| **Guardrail** | An automatic control that authorises or blocks an action before it occurs. |
| **Defence-in-depth** | The stacking of several independent guardrail layers. |
| **Tier-1 (critical paths)** | Configuration/identity files whose modification requires hardened protection. ⚠️ Not to be confused with the heartbeat's escalation levels, which this repo writes **L0/L1/L2** precisely to keep the two apart (`docs/06-heartbeat.md`). |
| **Heartbeat** | A periodic confined daemon that performs checks and escalates by cost. |
| **Egress-allowlist** | A closed list of network destinations that a confined worker is permitted to contact. |
| **Control-via-audit** | The philosophy of free + logged + reversible writes, rather than mandatory prior approval. |
| **Provenance (`source:`)** | The field recording *how* a note's claim is known — a command, a `file:line`, a URL with a date. Distinct from what the note says. |
| **Birth date (`created:`)** | The field recording when a note came into existence. Written once and never updated; a filesystem `mtime` cannot serve this purpose, since it means "last edited". |
| **Upper-bound date** | A date written as `≤YYYY-MM-DD`, recovered from a dated artefact containing the note. An honest partial answer where the exact date was never recorded. |
| **Claim tag** | An inline marker of how a statement is known: `[MEASURED]`, `[READ]`, `[REPORTED]`, `[INFERRED]`. Never used in a heading — position confers unearned authority. |
| **Draining (an instrument)** | Removing a decommissioned artefact from where people search, archiving it outside the code tree with a restore procedure. Preferred over annotating it in place. |
| **Reminded vs completed** | Two distinct facts about a scheduled routine: that a reminder was produced, and that the work happened. Recording only the first makes an unexecuted routine look healthy. |
| **Clock** | A one-shot, dated item carrying a question. It is retired once answered — unlike a routine, which recurs indefinitely. |
| **Routine** | A recurring practice with a cadence. Never "done" — only this period's occurrence is done. |
| **Active shelf** | The volatile record of work in flight, kept separate from the stable memory index because the two have opposite lifecycles. |
| **Narrative log** | The running record of *how* the assistant and the person work together — corrections, misunderstandings, what landed — as distinct from what was produced. |
| **Delegation standing** | The user's recorded answer to "for which domains may I bring in a specialist without asking?", captured at onboarding and expressed as the `D`/`P` mode. |
| **Autonomy boundary** | The rule that a change increasing what the system can do unattended is the user's to approve — including when the system believes a control is misfiring. |
| **First-run interview** | The onboarding conversation that produces the orchestrator brief and the initial roster from the user's actual work rather than a template. |
| **Capability server** | An external process the runtime connects to, exposing a namespaced set of tools (memory search, literature search, document fetch, browser, format conversion). Granted per **server**, not per tool. |
| **Source hierarchy** | The order in which an agent looks for an answer: own memory → own artefacts → authoritative domain sources → scientific literature → open web. Skipping a level answers from a worse source than was available. |
| **Delegation mandate** | The six things a delegation must carry: goal and done-criterion, where the ground truth lives, declared unknowns, source hierarchy, return format, out-of-scope line. |
| **Placeholder / token** | A `{{TOKEN}}` marker to be replaced with a concrete value when instantiating a template. |
| **Turn** | One bounded loop of the runtime: the user's input, every tool call the assistant makes in response, and the final answer. Not a request/response pair — it can run to many messages and many minutes. |
| **Compaction** | The runtime's reclamation of a full context window: history is replaced by a summary plus a short verbatim tail, and the ancestry link is cut. A rewrite, not a truncation. |
| **Prefix churn** | Editing anything near the top of the prompt — an instruction file, a tool listing — which invalidates the cached prefix and forces it to be paid for again. The dominant cost driver, ahead of conversation length. |
| **Anchor (shelf entry)** | The artefact an active-shelf entry points at — a file, a clock slug, a routine id — which the sweep resolves to decide whether the entry is still live. |
| **Sweep** | The pass that classifies shelf entries by discovery: does the anchor resolve, did the clock close. Distinct from reading the entry's prose. |
| **Two-sided diff** | The control on an auto-loaded surface: snapshot at session open, diff at session close, the person reverts any line they did not intend. |
| **Rebaseline** | Re-recording a tripwire's expected state after an authorised change, so the next check compares against what is now correct. Unbaselined authorised change and unauthorised change look identical. |
| **Pin** | A recorded hash or version an instrument is expected to match, written by the installing identity rather than the running one. |
| **Routine autonomy class** | How far a routine may act unattended: *measure-only* (runs and changes nothing), *propose-and-hold* (runs the survey, writes nothing, hands back a verdict), *ask-first* (does not run without a person). Classified by what it executes, not by its most dangerous step. |
