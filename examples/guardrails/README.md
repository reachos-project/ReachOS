# Guardrail examples (skeletons)

> **Read this first.** These files are **illustrative skeletons**, not hooks ready to run.
> They exist to show the *shape* of a guardrail — the structure, the exit convention, the
> decision point. They do **not** contain the real detection rules of any system:
>
> - The sets of destructive verbs, the critical-path globs and the detection expressions are
>   represented by **tokens** (`{{...}}`, `<...>`) that **each installation fills in**.
> - The `.pseudo.*` files must **not run as they stand**. ⚠️ **The tokens are not what stops
>   them, and it is worth knowing which is which** — measured, not assumed:
>
>   | File | Parses? | What actually prevents execution |
>   |---|---|---|
>   | `content-inspection.pseudo.py` | no — `SyntaxError` | the `<<FILL: ...>>` tokens are invalid Python |
>   | `sql-readonly.pseudo.sh` | no — `bash -n` fails | the `<is_read_only ...>` angle token is invalid shell |
>   | `workspace-enforcement.pseudo.sh` | **yes — `bash -n` returns 0** | **only the `exit 3` guard** |
>
>   `{{TOKEN}}` is perfectly valid shell; `<angle>` tokens are not. So whether a skeleton
>   happens to be un-parseable depends on which token style its lines use — which is an
>   accident, not a control. ⛔ **The `exit 3` guard on the first executable line is the real
>   protection and is therefore load-bearing.** Remove it last, deliberately, and only once
>   every token is gone.
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
