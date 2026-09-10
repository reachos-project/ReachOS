# Template — First-run interview

> **What this is.** The one thing to run the first time this architecture is instantiated.
> Without it the system has an orchestrator, a routing map, and no idea who is sitting in
> front of it — so every answer is generic and every delegation is a guess.

**Form:** conversational and branching. **One question at a time.** Reflect each answer back
before moving on. Show the artefacts being built **during** the interview, not at the end —
the person must see their own words becoming the system's configuration.

⛔ **Not a form.** Twenty questions in one block produces short answers and a profile made of
job titles.

---

## Step 0 — Preflight

Confirm the store is initialised, the memory index is reachable, and that this interview has
not already run. If it has, ask before overwriting — a re-run discards a profile that may have
been corrected by hand since.

## Step 1 — Identity

1. *"Who are you, and what do you call yourself professionally — the answer you'd give at a
   dinner with strangers?"*
2. *"Where do you work, and what does that place actually do?"*
3. *"How long have you been at it?"* — calibrates register, not seniority.

**Reflect back before continuing.** *"So you are {name}, {role} at {org}, {years} in."*

## Step 2 — How you got here

4. *"One sentence per chapter — education, first real job, the biggest turn."*
5. *"What did you almost become?"* — surfaces values that a CV hides.
6. *"What do people consistently misunderstand about your work?"* — calibrates how the system
   should explain **itself** to this person.

## Step 3 — The actual week

7. *"Walk me through a normal Tuesday, hour by hour."*
8. *"List everything taking up brain space right now — projects, commitments, courses,
   obligations. Don't curate."*
9. *"For each: what stage, who else is involved, what does success look like this year?"*

⭐ **Start creating memory spaces live, and name them out loud.** *"I'm creating separate
spaces for {A}, {B}, {C} — rename or add any of these."*

10. *"What did I miss? Side projects, obsessions, recurring obligations."*

## Step 4 — The pain (where this earns its keep)

11. *"What part of your week do you dread? The thing you'd pay to make disappear."*
12. *"What do you explain over and over?"*
13. *"What can't you do alone, but also can't justify hiring a person for?"*
14. *"If someone junior sat next to you ten hours a week, what would you give them?"*

**As these land, build a private list of agent candidates.** Do not show it yet.

## Step 5 — Standards and trust

15. *"Language: which, and if translation is needed, from what?"*
16. *"How do you want to be told you're wrong — blunt, structured, or discursive?"*
17. *"Three things that make you immediately distrust an AI's output."* — negative examples
    calibrate the guardrails better than positive ones.
18. *"Anything else about how you work? Quirks, constraints, dealbreakers."*

## Step 6 — Three questions most interviews skip

⭐ These two shape more day-to-day behaviour than everything above, and neither is obvious.

19. **Delegation standing.** *"For which of these areas should I bring in a specialist
    **without asking you first**, and for which do you want to be asked every time?"*

   Record the answer per domain as `D` (delegate by default) or `P` (only on request) in the
   routing map. Without this the system asks every time, the person tires of confirming, and
   delegation quietly stops happening — see `docs/02-smart-routing.md`.

20. **The autonomy boundary.** *"When I want to change one of my own safety rules — loosen a
    check, widen a permission — should I ever do that alone?"*

   The default answer, and the one worth explaining: **tightening alone, loosening never.**
   Anything that increases what the system can do without them is theirs to approve, even when
   the case looks obvious — including when the system believes a check is misfiring. See
   Rule 8 in `docs/01-orchestration.md`.

21. **Containment.** *"Two ways to install this. Which do you want?"*

   | | **A — open structure** | **B — sandboxed, with protected paths** |
   |---|---|---|
   | The assistant writes | anywhere the user account can | inside an allow-list; critical paths denied |
   | Network | unrestricted | through a filter, with a deny-list |
   | Critical files | ordinary files | declared set, hashed and watched |
   | Destructive operations | run | require a verified backup first |
   | Cost to you | none | real friction — see below |

   ⭐ **Recommend B, and say why in one sentence:** the authorisation layer only sees commands
   the assistant proposes, so a destructive command **inside a script** never passes through
   it. Only an OS-level sandbox catches that one. In deployments without it, the file carrying
   the system's own rules has been deleted by a script more than once.

   ⚠️ **And state the cost honestly, because it is real:** B means maintenance windows to edit
   protected files, re-hashing after every authorised change, and occasionally a legitimate
   action being denied. A person who is not told this discovers it as a series of small
   obstructions and switches the whole thing off. Someone who chose it with the cost in front
   of them tolerates it.

   **If B, install the accompanying instruments** — they are a set, and the set is what works:

   | Instrument | Does | Reference |
   |---|---|---|
   | Sandbox profile | filesystem allow-list with denies inside; filtered egress | `docs/12-os-sandbox.md` |
   | Critical-path set | the declared list of files whose change matters | `patterns/tripwire-baseline/` |
   | Tripwire + baseline | hashes the set, alerts on drift, with rebaseline discipline | `patterns/tripwire-baseline/` |
   | Backup-before-destructive | verified archive + manifest before any destructive step | `docs/01-orchestration.md` Rule 7 |
   | Out-of-band alert | tells the person when a channel they rely on has stopped | `patterns/reciprocal-watchdog/` |

   ⛔ **Do not install half of it.** A tripwire without rebaseline discipline produces false
   alerts until it is ignored; a sandbox without backups turns a denied action into lost work;
   an alert with no independent channel cannot report its own failure.

   ⚠️ **Derive the critical-path set from what is actually watched, never from a list typed by
   hand.** A hand-kept list drifts from reality and each divergence sends a false alarm.

## Step 7 — Show the artefacts

Write, **and display**, two things:

- **The orchestrator brief** — identity, register, active projects, working patterns,
  dealbreakers, delegation modes, autonomy boundary. This is read on every session; it is the
  single highest-leverage artefact in the system.
- **The person's entry in memory**, with provenance from day one: `source:` (this interview,
  with the date) and `created:`. Starting the corpus with dated, sourced entries costs nothing
  now and is unrecoverable later — see `patterns/provenance-and-dating/`.

Then ask: *"What's wrong here? Which sentence would you rewrite?"*

## Step 8 — Propose the first hires

From the pain points (11-14) and the projects (8-9), propose **three to five** agents. For
each: a real name, a one-line role, **why — quoting what the person actually said**, and what
it would own.

⛔ **No placeholder personas.** "Marketing Agent" is not a hire; it is a folder.

## Step 9 — One real result before they close the terminal

Propose **one concrete task** a new hire can do right now, drawn from something they mentioned.
The person should see the team produce something before the first session ends. An
architecture that is only explained does not get used.

## Step 10 — Persist and close

Record that the interview ran, regenerate whatever loads at session start, and tell them the
one command they need tomorrow.

---

## Anti-patterns

⛔ **All questions in one block.** ⛔ **Generic personas.** ⛔ **Skipping Step 7** — the person
must see what was inferred about them; inference shown is inference that can be corrected.
⛔ **Auto-hiring without confirmation.** ⛔ **Pushing on** when answers get short — ask whether
it is a bad time and offer to resume.
⛔ **Echoing stock phrasing back.** Use their words. A profile written in the assistant's
register describes nobody.

## If they stop halfway

Save the partial state, tell them how to resume, and do not re-ask what they already answered.
