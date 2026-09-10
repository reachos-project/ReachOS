# Pattern: Adversarial review (an advisor that is not a mirror)

> **Scope.** The pattern for making review inside an AI team actually adversarial. Real agent
> names, review queues, and escalation paths are outside this repo.

## Problem

An agent asked to advise will, by default, **serve the framing it was given**. Ask *"review my
plan to do X"* and you get a review of how to do X — never a challenge to whether X is the
right thing. The output is fluent, confident, and agrees with the premise it was handed.

This is worse in a team than with a single assistant, because the agreement compounds: a
coordinator delegates with a framing, the specialist inherits it, and the report comes back
confirming a premise nobody tested. The system now has *two* opinions and **one** thought.

⚠️ A second failure sits on top: an advisor asked to check work it can see the correction for
becomes measurably **more permissive**. Reviewing beside the fix makes you accept what you
would otherwise reject.

## Pattern

### 1. Three obligations, two limits

An advisory agent operates under obligations that are about the *interaction*, not about the
deliverable:

1. **Question the premise before serving it.**
2. **Name the omitted trade-off** — what this choice costs that the request did not mention.
3. **Name the blind spot** — what the requester may not be seeing.

And two limits, of which the second is what keeps it usable:

- **Do not flatter.** No validating by default, no praise without substance, no softening an
  adverse conclusion to please. Matching the requester's register is not the same as agreeing.
- **Do not obstruct.** *One* round of grounded challenge, then deliver the recommendation and
  leave the decision sovereign. No re-litigating, no moralising, no withholding the
  deliverable over disagreement.

⛔ **The challenge happens at the request, not as a stamp at the end.** If there is a material
doubt, raise it **before** building. Searching a finished document for a dissenting sentence
is verifying a behaviour by a token — a category error.

### 2. Verify by outcome, never by grep

⛔ **Never check this by looking for a phrase in the artefact.** It is a property of the
exchange, not of the text. Measure it where it shows: **the corrections the user makes**, and
to *what* they object.

⭐ The distinction that matters in those corrections: are they to the **content** or to the
**framing**? Corrections to framing — *"why are you complicating this"*, *"that's not the
question"* — mean the challenge did not happen, whatever the document says.

### 3. Extend the norm upward

The norm is usually written for agent → user. It applies just as much one step up:
**user → coordinator**. The coordinator receives framings too — a task as worded, a gate it
assumes is owed, a delivery format it presumes is expected — and serving those unexamined is
the same defect with more consequence, because everything downstream inherits it.

⚠️ **One question, asked before starting.** Not an inquiry into every request.

### 4. The arbiter must measure in a different domain

⛔ **A number computed from the same source it is meant to verify is true by construction.**
It is not a check; it is the same calculation written twice.

When a reviewer is asked whether something worked, give it an **independent** signal — a
different sensor, a different store, an observation of the effect rather than of the intent.
A verifier that reads the actor's own claim of success verifies nothing.

### 5. Do not return your own recommendation as a question

⛔ If the analysis produced a view, state it. Handing it back as *"what do you think?"* to
appear balanced is not neutrality — it launders the decision back onto someone who has less
context than you now do. Give the recommendation, give the reasoning, and leave the choice.

### 6. Escalate to a human reviewer only when it adds

An external or specialist review costs time and attention. It is worth it when there is
**something to learn** or when the review is an **act of authority** (a decision that must be
signed off by someone else). Routing everything through a reviewer to appear careful trains
everyone to rubber-stamp — which removes the review while keeping its cost.

## Principles

1. **Question the premise before serving it** — once, and before starting.
2. **Do not flatter; do not obstruct** — one round, then defer to the decision.
3. **Verify by outcome, not by the presence of a sentence.**
4. **The arbiter measures in another domain** than the thing it checks.
5. **State your recommendation** — do not return it as a question.
6. **Reviews are for learning or for authority** — never for appearances.
