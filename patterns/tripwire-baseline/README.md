# Pattern: Tripwire + baseline with rebaseline discipline

> **Scope.** Engineering of an integrity tripwire over critical files. The concrete set of
> watched files (the globs) and the real hashes are **not** part of the repo — they reveal the
> trust-system topology. Fictional paths.

## Objective

Detecting **unauthorised changes** to critical files (coordinator config, rules, hooks, sandbox
profiles) between the moment they are known-good and now.

## Mechanism

1. **Baseline:** compute a **hash manifest** of the critical files in a known-good state, and
   save it (pin).
2. **Tripwire:** periodically (and at session start) **re-compute** the hashes and compare with
   the pin. Any divergence → **alert**.

```text
# PSEUDO-CODE — the watched globs are installation configuration, not part of this repo.
pin  := load_manifest(BASELINE_PIN)        # { path: hash } from a known-good state
now  := hash_all(WATCHED_GLOBS)            # WATCHED_GLOBS is NOT distributed
drift := diff(pin, now)
if drift:
    alert("integrity: files changed vs baseline", drift)
```

## What the baseline actually is

A single JSON document, small enough to read and diff by hand:

```json
{
  "algo": "sha256",
  "generated_at": "2026-09-07T04:00:00Z",
  "entries": {
    "<watched-file-1>": "<hex digest>",
    "<watched-file-2>": "<hex digest>"
  }
}
```

Three fields and no more. `algo` is written down because a pin whose hash function is implied
cannot be verified by anything but the tool that wrote it. `generated_at` is what turns "the
pin disagrees" into "the pin disagrees and was last written before the change" — without it,
drift and staleness are the same observation. `entries` is a flat path → digest map, so a diff
names the file rather than a line offset.

⚠️ **The paths in `entries` are installation configuration.** Publishing the watched set tells
an attacker exactly which files are unwatched, so the map ships empty and is populated locally.

## Where the pin lives

⛔ **Not inside the tree it watches.** A pin that a compromise can rewrite is a pin that
certifies the compromise. Three properties, and all three are required:

| Property | Why |
|---|---|
| **Outside the watched tree** | otherwise an attacker who edits a watched file also edits its expected hash, and the check passes |
| **Restrictive permissions** — readable by the verifier, writable only by the account that rebaselines | the write path is the attack; the read path is not |
| **Written by the installing account, not the running one** | the daemon that verifies must not be able to rewrite what it verifies |

⭐ **A missing pin is a verification failure, never a pass.** The check that cannot read its
baseline has not found the files unchanged — it has found nothing, and the safe reading of
nothing is "unverified".

## Responding to an alert

Four signals, and the first question is different for each. Asking the wrong one first is how
a real drift gets rebaselined away.

| Signal | First question | Action |
|---|---|---|
| Drift, with a rebaseline recorded for it | *is the recorded reason the change I see?* | nothing — this is the system working |
| Drift, with no rebaseline | *who wrote this, and when* | **freeze and escalate**; do not rebaseline to make the alert stop |
| Pin absent or unreadable | *why can the verifier not read it?* | treat as a **failed verification**; never report PASS |
| Immutability flag changed, no drift | — | invisible to the tripwire; only an attribute scan finds it (below) |

⛔ **The fourth row is the one that matters most and fires least.** A content hash cannot see a
flag change, so this signal never arrives on its own — it only exists if something separately
inventories file attributes. Without that scan, the row is a description of a blind spot.

## The hard part: rebaseline discipline

The tripwire is only useful if **legitimate** changes are handled in a disciplined way.
Otherwise, every authorised change fires an alert, the operator gets used to ignoring alerts
(**alert-fatigue**), and the tripwire loses value precisely when it is needed.

Rule: **an authorised change to a watched file must trigger a rebaseline in the same session.**
The flow:

```
Authorised change to a watched file
        │
        ▼
Re-compute that file's hash  ──►  update the pin (rebaseline)  ──►  record who/when/why
        │
        ▼
The tripwire is "green" again for that file
```

- An **authorised change without rebaseline** = recurring false alert → signal erosion.
- An **unauthorised change** = drift without a corresponding rebaseline → true alert.

The distinction between the two cases is precisely the existence (or not) of a rebaseline
**registered and justified** for that change.

## Two-sided control (snapshot vs live)

To catch both the forgotten legitimate change and the malicious one, compare the **live** state
against a **snapshot** at two moments: at **session start** (catches changes made while no one
was watching, e.g.: a process that died mid-way) and at **close** (catches changes made during
the session and re-baselines the snapshot). If start finds drift without a prior close that
justifies it, that is the crash-path — bring it to the human's attention before anything else.

## Immutability flags interact with this, badly

Where watched files also carry a filesystem immutability flag, editing one is a **four-step
dance**, and the order is not optional:

```
1. measure the CURRENT flag state   ← on the file AND on its directory
2. clear the flag, edit, close
3. restore the state measured in (1)   ← not "apply the flag": restore what was there
4. rebaseline, in the same window
```

⛔ **Step 3 is where this goes wrong.** Writing the procedure as "reapply the flag" instead of
"restore the prior state" sets the flag on things that never had it — and the mistake is
silent, because a flag change alters no content and therefore no hash. Write step 1 as a
recorded measurement, not as an assumption about what the state "should" be.

⛔ **The tripwire almost certainly does not watch the flag.** A typical implementation records
existence, size, timestamp and hash — not the file's attributes. So clearing an immutability
flag and leaving it cleared is **invisible to the tripwire**: the content check still passes.
If the flag is part of the posture, it needs its own inventory scan.

⚠️ **Measure the directory too, not just the file.** An immutable *directory* blocks file
creation while permitting modification of existing files — the opposite of the usual
intuition, and a reliable source of a rename or atomic-replace failing halfway.

⚠️ **Reinstalling a component typically clears these flags.** Anything that replaces files —
package installs, deployment scripts — silently resets the posture, and the reset is not
visible in any content hash.

## Principles

1. **Baseline = known-good state**, with versioned pin (but real hashes outside the public repo).
2. **Authorised change → rebaseline in the same session**, otherwise alert-fatigue.
3. **Rebaseline is registered and justified** — that is what distinguishes authorised from malicious.
4. **Two-sided control** — start and close — so there is no blind window.
5. **The watched globs are private** — publishing them tells the attacker what to avoid touching.
6. **The pin lives outside what it watches**, written by a different account than the one that verifies.
7. **An unreadable pin is a failed verification**, never a pass.
