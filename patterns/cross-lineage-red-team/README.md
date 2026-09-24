# Pattern: Cross-lineage red team (a bounded Socratic dialogue with another model)

> **Scope.** The pattern for having a judgement attacked by a model of a different lineage
> before it reaches the person who decides. Real vendors, endpoints, credentials, network
> paths, and exposure classifiers are outside this repo.

## Problem

A model reviewing its own work shares its own blind spots. A second instance of the same model
shares them too. And when the coordinator is an **interested party** in the judgement — it is
rating its own output, comparing itself with alternatives, choosing its own tooling, or deciding
whether its earlier answer was good enough — self-review has a direction: it favours itself.

`patterns/adversarial-review/` keeps an advisor from becoming a mirror *within* the team. This
pattern is for the case where the whole team is the mirror: bring in an adversary whose errors
are **not correlated** with the coordinator's, let it attack the judgement, and deliver only the
result.

⚠️ **The first version of this design, in the deployment it comes from, was named
"definitive".** Run live against a model of another lineage, the design was not overturned — but
it was shown to be **bounded adversarial triage, not robust mitigation**, because the interested
party still controlled exposure, framing, the dialogue, when to stop, **and** the synthesis. What
follows is the version that survived that critique.

## Pattern

### 1. When it fires

- **The coordinator is an interested party** in a high-stakes judgement — directly (rating
  itself, choosing between itself and something else) or **indirectly** (its autonomy, its
  reputation, its future use, whether its previous answer was sufficient).
- **"High stakes" is operational, not a feeling:** conflict of interest × consequence ×
  irreversibility × uncertainty × power asymmetry × potential harm.

### 2. What may leave — exposure first

Before anything is sent, a check classifies what would leave: only non-sensitive material — the
reasoning, the draft, analysis of public matters. Personal data, client data, secrets, protected
configuration, internal defence details, unpublished work: never.

⛔ **If the classification fails or is in doubt, the send is aborted** and the judgement is made
without the lane — and reported as made without it (§6).

### 3. Blind evaluation before the debate

Where exposure allows, the adversary first gets the **case**, not the coordinator's judgement,
and decides on its own. Only then does it see the judgement and attack it. This reduces anchoring:
an adversary shown the answer first critiques that answer; one that answered first has something
to compare it with.

⚠️ **When minimal exposure and blind evaluation collide**, minimal exposure wins — but the case is
recorded as **red team incomplete by exposure restriction**, and that label carries a mandatory
consequence (§6). It is never a passive tag. High-stakes cases that are also sensitive need an
adversary **inside** the boundary as their fallback.

### 4. The dialogue — Socratic, bounded, at most four rounds

```
round 1   send the judgement; ask for falsifiable criticism:
          the failures, the blind spots, what would change the conclusion
round 2+  for each objection: concede, or defend with evidence;
          then ask the adversary to attack the weakest point that remains
stop      when the adversary concedes / raises no new material objection,
          OR after round 4 — whichever comes first
```

⛔ **Four rounds is a ceiling, not a target.** It is what keeps the lane from becoming a loop of
re-litigation. Most useful dialogues converge before it.

⛔ **The adversary's replies are data, never instructions.** They go through an **entry** check as
much as the outgoing text goes through an exit check. An adversary that says "now do X" has
produced a sentence to evaluate, not a command.

⚠️ **Rate limits are expected.** When the adversary's service refuses for quota, back off and
defer — a bounded retry, never an unbounded loop. Deferral is a legitimate
outcome; see §6 for how it is reported.

### 5. Separate the decider from the objection classifier

The coordinator remains the author and the decider. The adversary is an adversary, not an
arbiter. But the step in between — deciding whether an objection **stands** — cannot be left to
the interested party, or every inconvenient objection gets reclassified as immaterial.

⭐ **Replace "defer only to valid objections" with a rule that does not require proving validity:**

> An objection that is **specific**, **potentially material**, and **not resolved by evidence or
> by an existing rule** has a mandatory consequence.

And whoever classifies objections is **not** the interested agent.

### 6. Distinct end states, and consequences that bind

| End state | Means |
|---|---|
| **validated under sufficient critique** | the dialogue converged; no specific, material, unresolved objection stands |
| **inconclusive — budget** | the round limit or the quota ended it with objections still open |
| **inconclusive — exposure** | the case could not be sent in the form a full critique needed |
| **inconclusive — context** | the adversary lacked what it needed to judge |

⛔ **"Inconclusive by budget" is never presented as "passed the red team".** Stopping because the
money or the rounds ran out is not the same fact as surviving the critique.

For any inconclusive state, and for any objection left standing, **choose a consequence** — a
button marked "approve" is not one of them:

- **resolve** it by external verification, where a source, a test or an objective rule exists;
- **reduce confidence** — high confidence is no longer available for this judgement;
- **expose the residue** to the person, as a named open objection;
- **escalate**; or
- **refuse** to deliver the judgement in this form.

### 7. The synthesis, and what reaches the person

The synthesis is structured, with pre-registered sections, including a mandatory one:
**"material objections still standing"**. Open objections are not buried in prose.

The person receives the **final judgement**, with the adversary's contribution marked where it was
material, and the standing objections listed — **not** the round-by-round transcript unless they
ask for it. Every call is logged: a summary of what was sent, the verdict, the cost.

## The finding the dialogue produced about itself

Run live, the adversary's last round made a point that is worth more than any single objection:

> **There is no neutral arbiter inside the system** for open, high-stakes judgements. "Who
> classifies the classifier?" regresses forever in theory. It is cut **operationally**, in three
> ways: **external verification** where there is a source, test or objective rule; **conservative
> consequence** — a specific, material, unresolved objection removes high confidence or
> escalates, without having to prove it true; and **human authority** for the normative residue.

And a warning about that human backstop:

- **The human is not "without stake"** — they are the **authorised responsible party**, who may
  have stakes of their own.
- **Exposure to the human should be minimally sufficient, severely prioritised, and operationally
  binding** — not maximal. Maximal visibility produces alert fatigue, and alert fatigue produces
  rubber stamps.

Five rules against the rubber stamp:
1. **Triage** — only residue above a threshold goes up.
2. **No review is not approval** — the default in the absence of a decision is the conservative one.
3. **A grave objection requires choosing a consequence**, with an auditable justification for
   "proceed".
4. **Keep summary and evidence apart**, with drill-down from one to the other.
5. **Audit by sample — and measure the human reviewers too**, as part of the system.

⭐ **The framing that survived:** *when the system is an interested party, it does not absolve
itself. It resolves the objection by evidence, or reduces confidence, or exposes the residue, or
escalates, or refuses.* The lane's success metric is not how many judgements it validated; it is
**how faithfully it exposed to the person what remained unresolved**.

## Choosing the adversary

"Another lineage" is a proxy. What is actually wanted:

- **low error correlation** with the coordinator — it fails on different cases; and
- **measured adversarial calibration** — it tells a right case from a wrong one, rather than
  performing generic caution on everything.

⚠️ **Watch the adversary's own substitute stakes:** playing the role, pleasing the protocol,
winning the debate. An adversary that objects to everything is as uninformative as one that
objects to nothing.

## What this does not do

- **It does not make the coordinator neutral.** It bounds the damage of not being neutral.
- **It does not replace verification.** Where a test or a source can settle an objection, that
  settles it — not the dialogue.
- **It is not frequent.** In the deployment this comes from, the lane ran a handful of times. Its
  value is in the method and in the few judgements where the coordinator's interest is real.

## Principles

1. **Fire when the coordinator is an interested party** — directly or indirectly — in a
   high-stakes judgement.
2. **Exposure check before sending; entry check on what comes back** — replies are data.
3. **Blind evaluation before the debate**, where exposure allows.
4. **At most four rounds**; back off on quota, never loop.
5. **The decider is not the objection classifier**; a specific, material, unresolved objection
   has a consequence.
6. **"Inconclusive by budget" is not "passed".**
7. **Standing objections reach the person by name**; exposure is minimal, prioritised, and binding.
