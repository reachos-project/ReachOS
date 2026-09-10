# tools/ — the anti-leak linter

Two shipped artefacts and one test. All of it is Python 3 standard library only.

| File | What it is |
|---|---|
| `leak_linter.py` | The linter. Scans a staging tree for secret patterns (BLOCK), upstream-name and taxonomy overlaps (WARN), and never-ship artefacts (BLOCK). |
| `leak_linter_denylist.public.json` | The public rule set. Generic secret detectors only — no real identifiers, which is why it is safe to commit. |
| `test_leak_linter_tripwire.py` | Regression test for the assert-absent tripwire. |

## The CI invocation

Exactly this, from the repo root. `--public` fails closed if any loaded rule category falls
outside `{secret, secret-baseline}`; `--redact-matches` keeps matched values out of public
job logs.

```
python3 tools/leak_linter.py --public --staging . --denylist tools/leak_linter_denylist.public.json --redact-matches
```

**Merge criterion: `BLOCK = 0`.** `WARN` never changes the exit code, but each one has to be a
*conscious* overlap — see `NOTICE`.

## Two scans, and they are not the same scan

⛔ **`ignore_paths` excludes a prefix from content scanning only.** `tools/` is on that list,
because the deny-list enumerates upstream names and therefore matches itself: every one of
those WARNs described the deny-list, not the repo.

⭐ **The assert-absent tripwire walks the tree separately and is deliberately not filtered.** An
ignored prefix must never become somewhere a never-ship file can hide — and `tools/` is exactly
where such a file would land by accident, since that is where its sibling belongs. This is the
one property worth a test rather than a comment.

## Test result

Planting the three never-ship deny-list basenames inside `tools/` — the ignored prefix — and
running the CI invocation over the copy:

```
decoys planted : 3 in tools/ (excluded from content scanning)
decoys BLOCKed : 3  ['leak_linter_denylist.json', 'leak_linter_denylist.private.json', 'leak_linter_denylist_internal.json']
exit code      : 2 (2 = FAIL/blocked, as required)
RESULT         : PASS
```

⚠️ **Read it with its control.** 3 of 3 blocked *with* the decoys present; the same invocation
over the clean tree returns `BLOCK=0`. A test that only ever reports "blocked" would pass on a
linter that blocks everything — the pair is the evidence, not the line.

The test copies the tree to a temporary directory and removes it afterwards; it never writes
into the repo.
