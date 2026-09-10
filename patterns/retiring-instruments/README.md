# Pattern: Retiring instruments (drain, mark, verify)

> **Scope.** The pattern for decommissioning a script, hook, routine, or check without
> leaving a trap behind. Real paths, service names, and deployment layout are outside this repo.

## Problem

An instrument that is switched off but **left where it was** does not become harmless. It
becomes a silent trap, because it still **reads as the instrument**.

The failure is not that the file wastes space. It is that reading it produces a **confident
wrong conclusion that looks like reading the source**. Nothing in the file warns you. Search
finds it. Your editor opens it at the line you asked for.

A measured instance: a health-check script was consulted to understand a guard's behaviour.
The copy on the source tree was the pre-migration version — the live one had moved to a
different location weeks earlier. The reading produced the conclusion that a fix had never
shipped. The opposite was true. The wrong conclusion was reported before it was caught.

⛔ **The reason a header comment does not save you is mechanical: a banner at the top does
not protect whoever enters in the middle.** In that case the file was reached by a search
with the path typed from memory, and read from line 566 onward. The first line was never
seen. That is how code is read with tools — nearly always.

## Pattern

Three defences at three different points of the same path: **take it off the path · warn on
the path · measure the path.** In strict order of preference.

### 1. Drain — preferred, and almost always possible

Remove the artefact from where people look. Archive it **outside the code tree**, with a
checksum manifest and a short note giving the **restore procedure** if it is still anyone's
safety net.

Before removing, enumerate the consumers — search the whole tree for the path, and name the
conditional ones explicitly (a rollback definition invoked only if someone reverts).

⚠️ **Archive the version WITHOUT the marker.** An archived file that says *"this is not the
copy that runs"* starts lying the day it is restored.

### 2. Mark — only what cannot be drained

When the artefact must stay (it is loaded by absolute path, it is the rollback target at a
fixed location, it shares a directory with live state), write a header that **does not
assert state** and that points to a verifier.

⛔ **A marker that asserts state lies on the first day the state changes.** Observed
sequence, on one file: the header said `DRAFT — NOT APPLIED` while it was live; it was
corrected to `LIVE in production`; a migration made it inert **the next day**. Two
generations, two lies. The third is avoided by not declaring state at all — point at the
thing that knows.

### 3. Verify — by discovery, not by declaration

A checker that compares what is **in force** against what is **in the tree**, and that finds
new cases by itself rather than reading a hand-maintained list. A declared list drifts from
the watched set; a derived one cannot.

⚠️ **It is only worth having if it is silent in the nominal state.** With two copies left
undrained, such a checker reports "2" forever — and an alarm that fires in the nominal state
gets ignored. **Draining is what gives the checker's silence its meaning.**

## Why this is a rule and not tidiness

The three defences are the same defence at different points of the reader's path:

```
 someone needs to know how X behaves
        │
        ├─ 1. DRAIN    — the stale copy is not there to be found
        │
        ├─ 2. MARK     — if it must be there, it refuses to state its own status
        │
        └─ 3. VERIFY   — something independently notices when a copy diverges
```

Cost is not storage. Cost is a wrong conclusion with the appearance of evidence.

## Principles

1. **Drain before marking** — the best warning is the file not being there.
2. **Enumerate consumers before removing** — including the ones invoked only on rollback.
3. **Never assert state in a marker** — point at the verifier that can answer.
4. **Archive without the marker** — it becomes false on restore.
5. **Verify by discovery** — a hand-written list of what to watch drifts from what is watched.
6. **A checker that never goes silent teaches everyone to ignore it.**
