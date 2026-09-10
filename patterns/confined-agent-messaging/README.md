# confined-agent-messaging

A validated **pattern** for giving a confined autonomous agent a two-way text channel
to its human operator over a consumer messaging service — without weakening the sandbox.

## What this is

A single design note: [`confined-agent-messaging.md`](./confined-agent-messaging.md).
It documents the problem, the OS-automation-consent finding that shapes the whole design,
the two-job architecture, the provenance envelope, the echo trap on a shared account, the
operational lessons learned running it, and an honest frontier of what was not verified.

## What this is **not**

- **Not an installable implementation.** There is no code. The design was validated on
  one machine and one OS version; it is not a product tested for third parties.
- **Not a security guarantee for your setup.** The pattern's safety argument rests on a
  separation of capability that you would have to re-establish, and verify, in your own
  environment.

If you build from this, the design note's *Frontier* section lists what you must close
before relying on such a channel.

## Why prose and not code

Sanitising a working implementation to publish it produces an artefact that is no longer
the thing that was validated, and that someone might install believing otherwise. A
reference implementation, if it ever exists, is a separate effort: written clean, with
its own tests and its own security review — not an export of a private setup.

## Related patterns

- [`../worker-confinement/`](../worker-confinement/) — confining the agent itself, which is
  what makes the capability separation described here meaningful.
- [`../reciprocal-watchdog/`](../reciprocal-watchdog/) — the two halves of a channel watching
  each other, so that a silent receiver is detected rather than assumed healthy.

## Licence

Documentation: [CC-BY-4.0](../../LICENSE-docs), as with the rest of `patterns/`.
