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

## Principles

1. **Baseline = known-good state**, with versioned pin (but real hashes outside the public repo).
2. **Authorised change → rebaseline in the same session**, otherwise alert-fatigue.
3. **Rebaseline is registered and justified** — that is what distinguishes authorised from malicious.
4. **Two-sided control** — start and close — so there is no blind window.
5. **The watched globs are private** — publishing them tells the attacker what to avoid touching.
