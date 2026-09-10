# Pattern: Apply preflight — a gate that reads the apply script before it runs

> **Scope.** How a change to protected configuration (rules, hooks, scripts, settings) gets
> applied by a script *without* the script being trusted. Paths and watched globs are
> installation configuration and are not in this repo.

## Objective

Every non-trivial change to protected files ends up as a script: back up, unlock, write,
re-lock, re-baseline. The script is written by the assistant (or a subagent) minutes before it
runs, and it runs with the person's privileges. **The gate exists because the layer that
inspects shell commands sees the *invocation* of the script, not the commands inside it** —
`bash apply.sh` looks harmless to a command filter, whatever `apply.sh` contains.

## Mechanism

The gate is a hook on the command boundary that fires when the command is *running a script*
(`bash x.sh`, `python3 x.py`). It opens the file and checks a **contract the script has to
declare about itself**, then blocks or lets through. Detect-and-block, no repair.

```
# PSEUDO-CODE — hook on the command boundary
if command runs a script file:
    text = read(script)
    findings = []
    findings += check_declared_targets(text)      # 1
    findings += check_flags_declared(text)        # 2
    findings += check_dry_run_gate(text)          # 3
    findings += check_destructive_verbs(text)     # 4
    findings += check_privilege(text)             # 5
    if any(f.blocking for f in findings): deny(findings)
    else: allow_with_notes(findings)              # notes are logged, not hidden
```

### The contract (what a script must say about itself)

| # | The script declares | Why it is checked, not trusted |
|---|---|---|
| 1 | **Targets** — every protected path it will write, listed literally near the top | a reviewer must see the set without reading code; targets computed inside functions are invisible |
| 2 | **Flags** — which of those paths (and *directories*) it will unlock, with the state **measured at run time**, not copied from last week | immutability flags change with every hardening; an inherited list is wrong within days |
| 3 | **A dry-run that can HALT** before any write, and a `--apply` that is a separate switch | a HALT in dry-run means nothing was touched — that is the instrument working |
| 4 | **No destructive verbs on protected paths** (`rm`, `mv`, overwrite-copy, `find -delete`, redirection-to-file, truncation) — writes are atomic (`temp + rename`) and backups are byte copies, never metadata copies | metadata copies propagate immutability flags onto the backup, and the *retry* fails in a place nobody looks |
| 5 | **No privilege escalation inside the script** — the one privileged step (the re-baseline) is a separate command the person runs | a script that escalates has no upper bound on what a bug can do |

Anything the gate cannot resolve it names as **a note, not a pass**: a target computed at
run time, a path under a symlink, a variable it could not follow. The person decides.

### An escape hatch, and its price

Some scripts legitimately violate a rule (a launcher that runs privileged by design, a
one-off migration). The script may declare `# {{OVERRIDE_MARKER}}: <rule> — <reason>` and the
gate lets it through **and logs the override**. ⚠️ The marker string is **chosen per
installation** and lives only in the gate's own source — a marker fixed by a public document
would be a known escape hatch in every reader's build, which is a defect, not a feature. Overrides are counted by a weekly sweep;
a growing count is the signal that the rules are wrong or the discipline is.

## The shape of a compliant apply (seven steps, stop at the first failure)

```
0  preflight     — targets exist, flags measured now, "N targets, M immutable"
1  backup        — byte copies + checksum manifest; verify the manifest before continuing
2  snapshot      — record the current flag state, to restore *what was*, not what you assume
3  dry-run       — apply to copies, run the new file's self-test, HALT on any failure
4  unlock        — clear immutability on targets AND on the directories the temp files land in
5  apply         — atomic writes, modes preserved; emit the list of paths written
6  re-lock       — restore step-2 state exactly (a trap runs this even on Ctrl-C)
   then, by the person: re-baseline the tripwire against the list from step 5
```

⭐ **Step 6 restores, it does not apply.** A file that was never immutable must not come out
immutable "for safety" — that is how a memory directory got locked for an hour without anyone
noticing. Restore what step 2 recorded, and count the files it *skipped* as the proof.

⭐ **The list from step 5 feeds the re-baseline.** The tripwire's rebaseline should refuse if
pending changes exceed what the apply declared — otherwise the stamp depends on someone
reading a list, which is the failure mode this whole pattern exists to close.

## What the gate does NOT do

- It does not make the script correct. A dry-run that passes on copies can still fail on the
  real target for a reason the copy did not have (a directory flag, a symlink). The **failure
  model** for locked directories has five distinct points — creation blocked, replace blocked,
  metadata copy propagates the flag, orphan temp file, re-lock must run on failure — and
  fixing the one you just hit uncovers the next. Enumerate the model before the first line.
- It does not replace the reviewer. The contract exists so a reviewer can read five
  declarations instead of three hundred lines — not so nobody reads.
- It does not see scripts invoked *by* scripts. Nesting is a bypass; the contract asks for a
  flat apply.

## Principles

1. **A script is not trusted because it was allowed** — the command filter saw the name.
2. **Declare targets and flags at the top, measured now** — a reviewer reads declarations.
3. **Dry-run with HALT before any write** — nothing touched is the good outcome.
4. **Atomic writes, byte-copy backups, restore-not-apply flags.**
5. **Overrides are logged and counted** — an escape hatch nobody counts is a hole.
