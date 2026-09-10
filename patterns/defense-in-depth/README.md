# Pattern: Defence-in-depth for destructive actions

> **Scope and disclosure limit.** This document describes the **engineering** of a layered
> system that prevents a destructive action from reaching critical files. It describes the
> *form* — not the *signatures*. The concrete set of detection rules (verbs, path globs,
> regular expressions) is **deliberately omitted**: publishing detection signatures aids
> evasion. Kerckhoffs' principle applied in the reverse of the obvious — the *mechanism* is
> public, the *specific configuration* of each installation is private. All paths below are
> fictional (`/opt/halcyon/assistant/...`).

## Problem

An AI agent with shell access can, by mistake or injection, issue an operation that deletes or
overwrites a critical configuration file (the coordinator file, rules, hooks, state database).
A single control point is not enough — it fails or is bypassed. The response is to require the
action to traverse **independent layers**, each failing in a different way.

## The three layers

```
Proposed action
   │
   ▼
[C1] Authorisation matcher (tool threshold)          static allow / deny
   │ passed
   ▼
[C2] Content inspection (pre-execution)              deep examination
   │ passed
   ▼
[C3] Verifiable backup + source of truth             recoverable even if it passes
   │
   ▼
Execution
```

### C1 — Authorisation matcher, and its blind spot

The matcher evaluates `allow`/`deny` rules statically on the requested action. It is fast and
deterministic, but has a **structural blind spot** that is the central lesson of this pattern:

> The matcher only intercepts at the **coordinator → tool threshold**. A destructive command
> **embedded inside a script** that the coordinator sends for execution does **not** pass
> through the matcher again — it runs like any other binary on the system.

This is a generic property of any static threshold matcher, not a weakness of a specific
implementation. This is precisely why C2 and C3 exist: defence cannot rely solely on the
threshold.

### C2 — Content inspection (pre-execution)

A hook that receives the action **before** it occurs and examines it. Engineering requirements:

- **Robust command extraction.** Read the tool's structured input (e.g.: the command field in
  the JSON payload) with a real parser. **Never** with a fragile regex that breaks on the first
  escaped quote — a fragile extractor is a bypass waiting to happen.
- **Detection of destructive operations on critical paths**, including **indirect** references
  (the critical path as an argument to another command, or passed to a script).
- **Fail-safe / over-block:** if the input is malformed or the parser fails, **block** as a
  precaution rather than passing.
- **Exit convention:** `exit 0` = allow; `exit != 0` = block, with the reason written to the
  error channel for the model/operator to see.

```text
# PSEUDO-CODE — not executable; real signatures deliberately omitted.
input      := parse_tool_payload(stdin)          # structured parser, not fragile regex
command    := input.command
if parser_failed:
    deny("malformed payload — over-block as a precaution")   # fail-safe

# NOTE: DESTRUCTIVE_VERBS and CRITICAL_PATHS are sets defined by EACH installation
#       and are NOT distributed in this repo. See the disclosure note at the top.
if references_destructive_op(command, DESTRUCTIVE_VERBS) \
   and touches_any(command, CRITICAL_PATHS):
    deny("destructive operation on a critical path")
allow()
```

> **What is NOT here, and why.** The content of `DESTRUCTIVE_VERBS`, `CRITICAL_PATHS`, and
> the logic of `references_destructive_op` are the detector's signature. Distributing them
> would give an attacker the exact map of what to avoid. The pattern is shareable; the
> signature is not.

### C3 — Verifiable backup + reversibility

Before any operation capable of destroying critical configuration: create a **verifiable
backup** (archive + hash manifest), **confirm the backup's integrity**, and only then proceed.
Combined with a **markdown source of truth** and an **append-only history**, almost everything
is reversible.

## Two reinforcing controls that sit above the layers

### Pre-apply validation (assumptions dry-run)

Before applying a change to a critical file, run a dry-run that validates the change's
**assumptions** against the **current** state:

- does each item to REMOVE actually exist? (otherwise the change is stale)
- is each item to ADD absent? (otherwise it has already been applied)
- do the structural assumptions the change makes still hold?
- is the permission-rule syntax valid? ⚠️ **This one is a belief, not a measurement, and it is
  listed as a check precisely so it can be tested rather than assumed.** The fear is that a rule
  with invalid syntax is silently ignored and the defence goes inactive without warning. On one
  runtime we looked for evidence of that and **found none** — every apparent instance turned out
  to be our own documentation echoed back into context (`docs/14-runtime-observed.md`,
  §"What we could not establish"). Verify it on your host before relying on it, in either direction.

If there is **drift** between the assumed and the real: **HALT** and re-evaluate before
applying.

### Backup-before-risky (blocking precondition)

Operational rule: **no** script — one's own or delivered by a sub-agent — that contains a
destructive operation on a critical path runs without a complete and verified backup existing
first. A `syntax-check` (e.g.: `bash -n`) **does not** substitute semantic reading: it is
mandatory to **read** the script and look for destructive operations referenced, including
indirectly. If the script performs a destructive operation on a critical path, **return it to
the author for redesign** — do not execute.

## Why independent layers compose

If each layer fails **independently** with probability `p_i`, the probability of a destructive
action traversing all layers is approximately the **product** `∏ p_i` — orders of magnitude
smaller than any single layer. Independence is what matters: if two layers share the same
blind spot, they do not compose. Designing each layer to fail for a different reason is the
heart of this pattern.

⚠️ **The formula is doing qualitative work here, and it should be read that way.** No `p_i` is
estimated anywhere in this repo, and deliberately so: each layer's residual is exactly the kind of
record `docs/05-guardrails.md` says to keep in the house. So the product tells you the **shape** of
the argument — that independent layers multiply and correlated ones do not — and it is not a
quantitative claim about any deployment, including ours. Treat a stack of three layers with a
shared blind spot as **one** layer, whatever the arithmetic suggests.

## Principles

1. **Independent layers** — different blind spots.
2. **Fail-safe / over-block** — when in doubt, block.
3. **Robust extraction** — structured parser, never fragile regex.
4. **Never trust the self-reported identity** of a caller for security decisions.
5. **The pattern is public; the detection signature is not.**
6. **Verified backup before any destructive operation on a critical path.**
