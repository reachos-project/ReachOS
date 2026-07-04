# Guardrail examples (skeletons)

> **Read this first.** These files are **illustrative skeletons**, not hooks ready to run.
> They exist to show the *shape* of a guardrail — the structure, the exit convention, the
> decision point. They do **not** contain the real detection rules of any system:
>
> - The sets of destructive verbs, the critical-path globs and the detection expressions are
>   represented by **tokens** (`{{...}}`, `<...>`) that **each installation fills in**.
> - The `.pseudo.*` files are **not executable as they stand** — the tokens deliberately break
>   any attempt at direct execution. This is intentional: a security example should not be
>   runnable blindly against a real system.
>
> See `patterns/defense-in-depth/` for why the concrete signatures stay private (evasion)
> while the pattern stays public (Kerckhoffs).

## Files

| File | Layer | What it illustrates |
|---|---|---|
| `workspace-enforcement.pseudo.sh` | C1/C2 | An agent writes only inside its workspace; writes outside → deny. |
| `content-inspection.pseudo.py` | C2 | Pre-execution content inspection with robust extraction and fail-safe behaviour. |
| `sql-readonly.pseudo.sh` | C2 | Database read-only by default; only reads pass. |

## Exit convention (common to all)

- `exit 0` → **allow** the action.
- `exit != 0` → **block**, with the reason written to the error channel (stderr).
- When in doubt (malformed input, parser failure) → **block** (fail-safe / over-block).
