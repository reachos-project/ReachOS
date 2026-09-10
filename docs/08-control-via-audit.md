# 08 — Control via audit

A data governance principle that runs through the whole system: prefer **free, auditable,
and reversible writes** over **mandatory prior approval**. Approval on every write creates
friction and, in practice, leads people to bypass or stall the flow. Audit maintains control
without blocking work.

## The trade-off

| Approach | Cost | Residual risk |
|---|---|---|
| **Gating** (approve before each write) | High friction; constantly interrupts the flow. | Low — but only if people do not bypass the gate. |
| **Audit** (free write + log + review) | Low friction. | Contained by detect-and-revert within a bounded latency. |

The choice depends on **where the real risk lies**. The practical rule: place the hard gate
where an action is **irreversible**, and use audit where the action is **reversible**.

## Where to apply each

- **Hard gate (prior block):** irreversible operations — deleting/overwriting critical
  configuration, exposing secrets. Here the cost of error is catastrophic and blocking is justified.
- **Audit (free write + ex-post review):** the majority of content writes —
  memories, notes, logs. A wrong entry is always reversible because the source of truth is
  markdown and an append-only history exists.

## Audit pattern

```
Write  ──►  Log in the audit queue (actual content, not just a summary)
                     │
                     ▼
        Cross-reference with the activity history
                     │  (heuristic: anomalies — secrets, URLs, injection)
                     ▼
        Only anomalies are surfaced to the human
                     │
                     ▼
        On-demand review + trivial revert (SoT in markdown)
```

- Writing stays **free** — the queue is not a gate.
- The queue stores the **actual content** to enable faithful review, not just a summary.
- At session startup, only the **count** and **anomalies** are shown — not a per-session
  review screen.
- Full audit is **on-demand**. Complete reversibility comes from the markdown source of truth
  + activity history.

## Defence-in-depth for the audit itself

Cross-reference two sources: events logged in the history **versus** items in the queue. A
write event with no corresponding queue item signals a failed log — the audit audits itself.

⛔ **But note what the history actually records.** The authorisation hook decides and logs
**before** the write is attempted. If the write then fails — a permission, an immutable flag,
a sandbox denial — the event still reads as allowed. Measured here: entries recorded as
authorised writes for which no file exists.

⛔ **And the harder question this model does not answer on its own: who audits the auditor?**
Everything here — the close, the sweep, the queue, the quality gate — is executed by the same
assistant whose writes it is checking. That is a self-control, and this repo is otherwise strict
about not accepting those: `patterns/tripwire-baseline/` insists the pin be written by the
installing identity and not the running one, and `patterns/adversarial-review/` requires the
arbiter to measure in another domain. **Neither principle is applied to the self-controls above,
and the gap is real.** What makes it tolerable is not the audit — it is that every write is
**reversible** and the record is **outside the assistant's own reasoning**, so a person can
reconstruct what happened without trusting the account of it. If you need more than that for a
given class of write, the answer is a second identity, not a stricter checklist.

⭐ **The audit reads authorisations, not writes.** To know whether something was actually
written, look at the artefact. An audit trail answers *what was permitted*; only the
filesystem answers *what happened*. Any regime built on "free writes plus ex-post review"
depends on that distinction being understood, or the review inspects a record of intentions.

## Caution with sensitive data

If the audit queue duplicates content in plaintext, then **no sensitive content** (special
personal data, secrets, re-identification keys) may live in the audited memories —
that data belongs in dedicated stores, never in a free-text memory.

## Principle

> Control is not the same as blocking. Free + auditable + reversible writes give more real
> control than an approval queue that people learn to bypass — provided the hard gate protects
> what is genuinely irreversible.
