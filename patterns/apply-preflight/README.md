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
    findings += check_content_travels(text)       # 6
    if any(f.blocking for f in findings): deny(findings)   # no override path
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
| 6 | **The content travels in the apply** — new content for a protected file is produced by the script itself (an edit anchored on the installed file that aborts if the anchor is missing, or content generated inline), never copied whole from a sibling file in a working folder | a full working copy is a **second claim to be the instrument**: it reads like the instrument, an instruction can point at it, and it is left behind after the apply — where the next reader mistakes it for what runs |

Anything the gate cannot resolve it names as **a note, not a pass**: a target computed at
run time, a path under a symlink, a variable it could not follow. The person decides.

⚠️ **Read the command line in segments, not up to the first operator.** A copy followed by
`&&`, `||` or a pipe is the same copy. A reader that stops at the first operator misses the
forms applies use most (`cp a b || fail "..."`); a reader that truncates there loses the copy
that comes *after* the operator (`mkdir -p d && cp a d/`). Split on the operators and check
every segment — and keep one fixture for each variant, because each variant is where the
blindness comes back.

### A BLOCK goes back to the design or to the person — the agent never stamps it

**There is no override.** When the gate blocks, one of two things happens: the script is
**redesigned** until it complies, or the case goes to **the person**, who decides with the
findings in front of them. The agent that wrote the script does not get to wave it through,
whatever it has concluded about the finding.

The reason is the same as the autonomy boundary in `docs/01` (Rule 8): *"this BLOCK is a false
positive"* is the author's judgement about the author's own work, formed with the assumptions
that produced both the script and the belief that it is fine. It is also rarely worth what it
costs: an override buys the author's convenience, not a capability the person was missing. A
false positive is **measured, written down where the rule
lives, and brought to the person**; the rule is not bent on the spot.

⛔ **The lesson that made this a rule, and it is the uncomfortable one.** An earlier version of
this pattern allowed an override, declared in the script with a reason, logged, and counted
weekly — with the argument that a growing count would reveal bad rules or bad discipline.
Later, overrides started arriving with an **independent verification** attached: a second
agent had read that exact script and confirmed the finding was lexical. That looked like the
safe form of an override. It was not. **An override with independent verification is still
an override — and it was the verification that normalised it.** Each verified override made the
next one easier to justify; the count grew, and counting it stopped nothing. A second reader
reduces the chance that one override is wrong. It does nothing about the fact that the
exception has become the path.

⚠️ **If your gate still accepts an override marker, the rule above is doctrine and the code
disagrees with it.** Close the code, not the doctrine: make the gate refuse the marker, keep the
refusal logged, and rotate any marker that has ever appeared in a transcript, a log or a
working file — a secret that has been written down in those places is no longer one.

### A verdict that discloses, and what it does not absolve

It helps to have a separate, read-only instrument that, given an apply script, lists **the
destructive operations it finds, the protected paths it names, and where the two meet** — and
that takes its definition of "destructive" from the same source the command filter uses, so
the two can never disagree about what the word means. It returns one of four states, and the
output is read, never just the return code:

| State | Meaning |
|---|---|
| **conforming** | no destructive operation on a protected path |
| **destructive, declared** | there is one, and the script declares, in code rather than in comments, the obligations that go with it: flags measured before and restored after, the targets pinned by checksum with a HALT on drift, a backup as a precondition |
| **violation** | a destructive operation on a protected path, not declared |
| **unreadable** | the instrument could not parse it — which is **not** conforming |

⛔ **"Destructive, declared" is disclosure, not absolution, and not an attestation.** The check
is lexical: it sees the *forms* in the code, not that they work — so declarations must count
only outside comments, and even then they are forms. A check of this kind protects the
**existence** of a protected file, not its integrity: any design that asks "is a regular,
non-empty file left behind?" will read an overwrite as an edit. The backup obligation is
structurally unverifiable from the script — the backup is not an input to the instrument. In
that state, the decision is **the person's**, taken on the full printed lists.

⛔ **Nothing here catches an inert guard.** In one apply that ran, five of six return-code
guards were inert — a status captured after a pipe, an `if` that could never fire — while the
instrument reported the obligations as declared. The only act that catches this is **reading
the whole script**, which is why that reading is never delegated to a pattern match.

### What travels with the script to the person

A protected apply usually runs in the person's own terminal, where no hook runs and none of
this document is read. So the gate does not *authorise* the run; it shapes the **delivery**.
With the script go:

1. the **checksum of the script as delivered**, so what runs is what was checked;
2. the verdict instrument's **output, verbatim** — the state and the full lists, not a summary
   of them; a list someone summarised is no longer the list the person decides on;
3. **where the backup is and the result of verifying it**, with the command to repeat that
   verification. This is the only point at which the backup obligation — unverifiable from
   the script — becomes verifiable.

⛔ **What does not go with it is an opinion that it "can run".** In the declared state the
decision is theirs; in the conforming state the check was lexical and says nothing about
behaviour. See `patterns/handoff-to-human/` for the general form.

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
- It does not replace the reviewer. The contract exists so a reviewer can read a handful of
  declarations instead of three hundred lines — not so nobody reads.
- It does not see scripts invoked *by* scripts. Nesting is a bypass; the contract asks for a
  flat apply.

## Principles

1. **A script is not trusted because it was allowed** — the command filter saw the name.
2. **Declare targets and flags at the top, measured now** — a reviewer reads declarations.
3. **Dry-run with HALT before any write** — nothing touched is the good outcome.
4. **Atomic writes, byte-copy backups, restore-not-apply flags.**
5. **No override** — a BLOCK goes back to the design or to the person; a verified override is
   still an override.
6. **The content travels in the apply** — never a full working copy of a protected file.
7. **Disclose, do not absolve** — a verdict instrument informs the person's decision; it never
   replaces reading the whole script.
