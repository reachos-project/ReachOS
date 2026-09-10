# Contributing to this reference architecture

Thank you for your interest in contributing. This repository is a **reference architecture** —
it documents *patterns* that an organisation can study and reuse, with generic placeholders and
fictional examples. It is not production-ready software. The most useful contributions improve
the clarity, correctness, and coverage of the patterns, without ever bringing live configuration
from any real system.

## How to propose a pattern or improvement

1. **Open an issue** describing the pattern or improvement before writing much code — to align
   on scope and avoid duplication.
2. **Write from scratch (clean-room).** Describe the pattern from the *concept*. Never copy
   files, rules, or history from a real deployment — including your own.
3. **Use placeholders and fictional examples.** Use `{{UPPERCASE_IN_BRACES}}` tokens for
   parameterisable values; clearly invented entities (in the spirit of "Halcyon Consulting")
   for examples. See the existing `templates/` and `examples/` as a model.
4. **Open a pull request** with a description of what problem the pattern solves and how it
   can be adapted.

## Hygiene rules (mandatory)

These rules protect both this repository and your own deployment:

- **Never submit real identifiers.** No personal paths, hostnames, IPs, addresses,
  notification topics, tokens, keys, baseline hashes, or real people's names.
- **Never submit real detection rules** (sanitiser signatures, critical-path globs, or sandbox
  blocks from a production system). The *pattern* is shareable; the detection *signature* is
  not — publishing it aids evasion. See `patterns/defense-in-depth/`.
- **Non-executable skeletons.** Guardrail examples are illustrative and must not be runnable
  as-is against a real system (see `examples/guardrails/`).

## Automated check — anti-leak linter (CI)

Every contribution passes through an **anti-leak linter** in continuous integration. The linter
searches for real identifiers (personal paths, hostnames, tokens, internal names) and
unattributed overlaps with upstream projects.

- **Merge criterion: 0 BLOCK.** A contribution with any `BLOCK` result is not merged until
  corrected.
- `WARN` results (e.g., name overlap with an upstream) do not block, but require the overlap
  to be **conscious and attributed** (see `NOTICE`).

Run the linter locally before opening the PR and confirm the exit code is `0`. This is the
exact invocation CI uses (Python 3, standard library only, run from the repo root):

```
python3 tools/leak_linter.py --public --staging . --denylist tools/leak_linter_denylist.public.json --redact-matches
```

⚠️ Without `--public` the linter looks for the maintainers' private deny-list, which is not
distributed — it will exit 3 with "denylist not found". That is expected; use the line above.

## Contribution licensing

By submitting content to this repository, the contributor certifies that:

(a) they have the right to make the contribution, and
(b) they grant the project an irrevocable and perpetual licence to use, reproduce, and
    distribute the contribution under the terms of this repository (Apache-2.0 / CC-BY-4.0,
    as applicable).

This is an origin certification in the spirit of the *Developer Certificate of Origin* (DCO):
it does not require a formal contract, only the assurance that you have the right to contribute
and that the contribution falls under the repository's licences. See `LICENSE`, `LICENSE-docs`,
and `NOTICE`.

## Style

- Documentation in English; code, comments, and licence text in English.
- Clear structure, pattern-oriented: the *why*, the *form*, and the *principles*.
- No branding or references to real systems — the architecture conveys patterns, not
  installations.
