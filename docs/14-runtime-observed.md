# 14 — What the runtime actually does (observed, not documented)

> **Scope.** `docs/13` says what a host must *provide*. This page says how one such host actually
> *behaves* — the mechanics you only meet by operating a fleet for months, and which a competent
> builder will usually assume the other way round.

> **What this chapter observes, and on what terms.**
>
> The runtime described here is **Claude Code**, a command-line agent runtime published by
> **Anthropic PBC**. The architecture in this repository was developed and exercised while
> operating it. This chapter is an **independent field report by one operator**. It is not a
> vendor statement, it is not authorised, endorsed, sponsored by, or affiliated with Anthropic
> PBC, and nothing in it is a warranty, a specification, or a commitment by anyone.
>
> **How it was obtained, and what was left out.** Every observation below comes from reading the
> session transcripts the product writes to the operator's own disk during ordinary licensed use.
> Nothing was obtained by decompiling, disassembling, or otherwise reducing the software to
> human-readable form, by inspecting its packaged code, by intercepting network traffic, or by
> circumventing any technical measure. Material that appeared to document internal
> permission-rule syntax was **deliberately excluded**, because its origin was the product's
> packaged code rather than its observed behaviour — see §"What we could not establish".
>
> **What the claims cover, and what they do not.** Observations span **July–September 2026**
> across roughly seventy weekly builds, on **one operating system, one configuration, one
> operator**. Each figure states what it rests on: where a number is a product constant it is
> given as such; where it is a property of how hard one operator pushed the thing, it is marked,
> and those magnitudes do not transfer — only their shape. **Nothing here is generalised beyond
> what was measured. No claim is made about behaviour outside those bounds, on other platforms,
> or after those dates.**
>
> ⚠️ **Everything here speaks as of this chapter's publication date, and no later.** The product
> ships weekly and changes without notice. Nothing on this page is updated as it evolves unless
> the page itself is republished — so treat any statement as describing the runtime *then*, not
> the runtime you are running now.
>
> ⛔ **Anything below that matters to your design should be re-measured on your own host before
> you depend on it.** §"Checking these yourself" says how.
>
> **Corrections.** If any statement here is inaccurate, please open an issue: it will be corrected
> or withdrawn. Accuracy is the whole purpose of this chapter, and it is asserted for no other.
>
> **Published: 2026-09-10.** Every "as of publication" in this chapter means that date.
> **Corrected: 2026-09-24** — finding 1 was wrong as published; see §"Corrections".
>
> *Claude, Claude Code, and Anthropic are trademarks of Anthropic PBC, used here solely to
> identify the product observed. No affiliation, authorisation, endorsement, partnership, or
> sponsorship is claimed or implied.*

---

## The five that contradict what you would assume

If you read nothing else:

| # | The assumption | What is actually true |
|---|---|---|
| 1 | An HTML comment in an always-loaded instruction file is either always stripped or never | **It depends on where it sits.** A comment on its own line, or a multi-line comment block, did not reach context. A comment that **shares its line with text** — at the end, in a heading, or mid-line — did, every session, paid for *(corrected 2026-09-24; see §"Corrections")* |
| 2 | A long conversation is what costs you | Almost the entire input is cache reads. **Prefix churn** is the cost driver — editing one character near the top of the prompt is far more expensive than a thousand turns at the bottom |
| 3 | A probe that comes back "blocked" tested your guard | It may have tested nothing. **An absent tool fails before any permission layer runs**, and the message looks like a refusal |
| 4 | Compaction summarises; history is still roughly there | Compaction **rewrites** history. The ancestry chain is deliberately cut, and ~97% of context is discarded |
| 5 | Conversation history is append-only | It is not. A safety refusal can **retract messages already in the conversation** |

---

## The turn, and the shape of a session

**A turn is a bounded multi-message loop, and it is long.** Not a request/response pair: one
observed turn ran to 179 messages. In one operator's corpus the median turn was well over a
minute and the 99th percentile above twenty *(workload-dependent — do not treat as a constant)*.

⛔ **What this breaks:** anything you build that assumes per-turn latency of seconds. Watchdogs,
lock TTLs, "did it hang?" heuristics and progress indicators are all wrong by roughly two orders
of magnitude if you size them from intuition.

**Auto-compaction fires against the ceiling, not with a margin.** It lets the window fill
essentially to the top, then discards on the order of **97%** of context and takes **minutes** of
wall clock to do it. It arrives at the worst possible moment — when you are already at the limit.

**And it is a rewrite, not a truncation.** A synthetic message is inserted announcing the
continuation; a boundary record carries the metadata; **the parent link on that boundary is
null** and the real ancestry moves elsewhere. A short list of recent messages survives verbatim
*alongside* the summary. Everything else is gone from context, though it remains on disk.

⛔ **Two traps here.** Walking the parent chain to reconstruct a session silently hands you only
the tail — the chain is cut by design. And "it kept roughly everything, summarised" is wrong: it
kept a summary **plus a specific short list**, and nothing else.

**The session-start hook fires on compaction.** The hook carries a source discriminator, and one
of its values means *"this is a compaction, not a process start"*. That invocation is your only
re-injection point at the moment the context was gutted without the process ever restarting.

⭐ **This is the single most useful hook fact in this document.** State restoration built only
for process start will not run when it is most needed.

**Input typed during a turn is queued, and can be dropped.** Queue operations are recorded as
first-class events — enqueue, dequeue, and *remove*. A meaningful fraction of queued items were
removed rather than delivered. Typing during a long turn does not steer it; it lands at the next
boundary, if it lands at all.

**The model is told its remaining budget every turn.** A token-budget reminder is injected into
context reliably. You do not need to build budget-signalling scaffolding — it is already there,
and the model can be instructed to act on it.

---

## Files that load every session

### Comments: free or not depends on where they sit

⚠️ **This section was wrong as first published, and has been rewritten** — see §"Corrections"
for what it said and why it changed.

**Whether an HTML comment reaches context depends on its placement: a comment on its own lines
does not; a comment that shares its line with text does.** Three sources, stated separately
because they are not equally strong:

- **Controlled probe, before publication** (*probe 1*): a throwaway project whose instruction
  files hid a unique token inside each comment, next to a **visible control token in the same
  file** — so a missing comment could not be confused with a file that never loaded. It covered
  own-line comments in both files and a block in the rules file. Every visible token came back;
  no comment token did.
- **Controlled probe, isolated project, 2026-09-24** (*probe 2*): the same design, extended to
  every placement in the table, in both files, run in a fresh session with no tools. Both
  visible control tokens came back, and no token outside the answer key was returned — so the
  files loaded and the answer was not invented.
- **Observation of a live session** (*observation*): in a working deployment, a short comment at
  the end of a heading line in a loaded rules file was present in the model's context, while
  own-line comments and comment blocks in files loaded in the same session were absent and the
  text around them was present. Not designed as a test — but it is what exposed the error.

| Placement | Always-loaded project instruction file | Always-loaded rules file | Always-loaded memory index |
|---|---|---|---|
| Comment on its own line | **did not reach context** (probes 1 and 2, observation) | **did not reach context** (probes 1 and 2) | not tested |
| Multi-line comment block | **did not reach context** (probe 2) | **did not reach context** (probes 1 and 2, observation) | **did not reach context** (observation) |
| Comment at the end of a line of text | **reached context** (probe 2) | **reached context** (probe 2) | not tested |
| Comment at the end of a heading | **reached context** (probe 2) | **reached context** (probe 2, observation) | not tested |
| Comment in the middle of a line, text on both sides | **reached context** (probe 2) | **reached context** (probe 2) | not tested |

⚠️ **This is about files the runtime loads by itself at session start.** A file the model opens
with a read tool is returned as it is on disk, comments included — a different path, and
nothing in this table applies to it.

⛔ **The trap is the last three rows.** Parking rationale, history and notes-to-self in a
comment on its own lines is, as observed, free: it is removed before the file reaches the
model. A comment that shares its line with text is not — at the end of a sentence, at the end
of a heading, or in the middle of a line, it arrives with the line, every session, and you pay
for it. Two comments that look the same in an editor behave differently depending on whether
text shares their line.

⭐ So the practical rule is placement, not abstinence: **a comment on its own line, or in a
block, does not reach the model; a comment that shares its line with text does.** Archaeology
goes in a block on its own lines; nothing you do not want the model to read goes on a line
with text. The memory-index cells marked "not tested" are exactly that, and all of this is one
host, one configuration — **re-measure on your own host** before relying on it
(§"Checking these yourself").

### The always-loaded index has a hard cap, and the runtime warns you before it

The host imposes a **read limit on the order of 25 KB** on the memory index that loads each
session, and content past the cap is **not loaded**. Approaching it, the runtime injects a
warning naming both the current size and a target — the target being roughly **70%** of the cap,
with the instruction to keep one line per entry and move detail into topic files.

⚠️ **Do not dismiss that warning as noise.** It is the mechanism telling you that content is
about to stop being loaded, and it names the number that no documentation surfaces as
prominently. `templates/MEMORY-INDEX.template.md` is written to that shape for this reason.

### File reads are capped — and the failure is sometimes *partial*, not an error

Two distinct behaviours. A **hard failure** when a single read exceeds the token cap, delivered
as an errored result telling you to page. And a **soft one**: the content arrives with a banner
saying this is a partial view, naming the lines shown against the total, and telling the reader
in as many words not to answer from that page alone.

⛔ **The soft form is the dangerous one.** A model that reads a long file and answers confidently
may have seen the first two-thirds. The warning exists, but it lives *inside the tool result* —
not in the answer, and not anywhere the person reading the answer will see it. Any conclusion
drawn from "I read the file" needs to survive the question **which part of it?**

---

## Hooks: where they bite, and where they are mute

**stdout reaches the model; stderr on success does not.** Measured across pre-tool hook
executions: hooks exiting zero having written **only to stderr** put nothing into the model's
context *(positive control: within each session where that came back empty, the same extraction
did recover rendered stdout payloads from other hooks — so the query had reach, and the negative
is a property of the branch)*. Hooks exiting zero **with stdout** overwhelmingly did.

⚠️ Evidenced for one hook event (pre-tool, on shell invocations). The mechanism is likely
general; the measurement is not, and this page does not claim more than it measured.

⛔ **Consequence:** a hook that warns on stderr and returns success has warned *nobody*. The
agent proceeds without ever seeing it. If you want the model to know, write to **stdout** —
or block.

**Exit codes, by observation:**

| Exit | What happens | What the agent hears |
|---|---|---|
| `0` + stdout | proceeds | your message, in context *(in nearly all observed cases; the residual was not explained)* |
| `0` + stderr only | proceeds | **nothing** |
| non-zero *blocking* | tool call fails | an error naming your hook and its output |
| non-zero *non-blocking* | **work proceeds** | **nothing at all** — stdout was not rendered in any observed case |

⛔ **The non-blocking failure path is worse than useless as a warning channel.** It reads, from
the outside, like a hook that "failed loudly". The agent hears silence and carries on.

**The blocking message echoes your hook's configured command line to the model** — including
variables that were never expanded. Hook internals are not opaque. **Treat your hook's
invocation path as published text.**

**Hooks sit on the critical path.** Typical execution is sub-second, but one observed execution
was cancelled after roughly **ten minutes**, having stalled the session for that entire time.

⛔ **Never put network I/O or lock-waiting in a hook** unless you have set a timeout you can
afford to lose entirely — and find out what your host's default is, because a hung hook will
spend all of it.

**There is an interception point *before* the model sees the user's message.** A prompt-submit
hook can refuse, and the refusal is recorded with an explicit flag preventing continuation.

⭐ **This is the earliest boundary there is, and the only one that can stop content from entering
context at all.** Guards placed exclusively at the tool boundary have already let the content in.

**End-of-turn hooks are a veto point, not a notification.** The turn-end summary carries per-hook
timings, collected errors, added context, and a flag that can **prevent the turn from ending**.

---

## Permissions: the observability hole

⛔ **Permission denials are visible. Permission *decisions* are not.**

A denial surfaces as an errored tool result naming the tool. Refusal by a person and refusal by a
hook are likewise visible. So the boundary is not silent.

What no record anywhere contains is **which rule decided**. No rule value, no decision reason,
and — the part that matters most — **no allow event at all**. You can see that something was
refused. You cannot see *why*, and you can never see what was **permitted**.

This is a **declared absence with a positive control**: the same search does find the three kinds
of refusal, so the search works; the decision record does not exist.

⭐ **The gap is one of attribution, not of visibility** — which is the more useful shape, because
it names precisely what you must instrument yourself: **the mapping from a decision back to the
rule that made it.** Nothing else is missing.

⚠️ **And refusal is not a quiet boundary.** The denial message echoes **the full command string**
back into the model's context. Whatever a command carries on its argument line — a path, a flag,
a query string — enters context *because* it was refused. Anything you would not want in context
should not be on a command line you expect to be denied.

⭐ **What follows for design:** you cannot audit permission behaviour from transcripts after the
fact. If you need that evidence, you must generate it yourself — and **the only boundaries that
write to the transcript are the hooks**. That is a strong reason to route decisions you will want
to defend later through a hook that logs, rather than through configuration that does not.

**A human refusal is a message, not an exception.** It arrives as an ordinary tool result
instructing the model to stop and wait. Whether the loop actually stops is a matter of
**instruction-following, not control flow** — which is worth knowing before you rely on a person's
"no" to halt an agent mid-sequence.

⛔ **This section is a property of the runtime, not a description of anyone's security posture.**
Where *your own* evidence is thin is an internal document, and assembling one from pages like
this is exactly what `docs/05-guardrails.md` tells you to keep in the house: a written map of
what your controls do not reach is more useful to an attacker than to you. Read this to know
what the substrate does and does not record. Do not publish the resulting gap analysis of your
own deployment.

---

## Sub-agents

⛔ **Declaring a tool for a sub-agent does not create it — and the failure looks like a security
block.** The error says the tool is not available and suggests an alternative. The call **never
reaches any permission layer**.

⭐ **This is the most expensive misreading available to anyone testing guardrails.** A probe that
returns "blocked" may have tested nothing whatsoever: the tool was absent, so the guard you were
validating never ran. **Any negative security result must first prove the tool existed.**
See `patterns/adversarial-review/` — this is the concrete mechanism behind "prove the probe can
see the thing it is looking for".

**Delegate transcripts contain no system records.** Sub-agent sessions are written separately,
and their streams carry only conversation — none of the system-level events (compaction
boundaries, model changes, turn timing) that main sessions carry. **You cannot diagnose a
delegate's stall from the delegate's own log**; the events that would explain it are not written
there.

**Only the final message crosses back.** The parent receives status, resolved model, duration,
token totals, tool-use counts and a per-tool breakdown — plus the delegate's final content.
Nothing intermediate.

- Design the **return message as the entire deliverable**. A delegate's reasoning does not inform
  the parent.
- But note the flip side: **you are handed real per-delegation telemetry**, which is the cheapest
  available basis for answering "is delegation actually paying for itself?"

**Progress from a background delegate is a sentence, not output.** Polling for partial results
gets you a compressed summary and a file path.

**Model and background execution are per-delegation parameters**, and the result reports the
model that was actually resolved — which is not always the one requested.

---

## Tool loading

**Most tools are advertised by name without their schemas, and must be loaded on demand.** The
runtime says so explicitly and provides a selection mechanism; registry changes then arrive as
typed deltas that distinguish, among others, tools added, removed, and still pending.

⭐ **If you are optimising context, this is the largest lever the runtime already gives you** —
names are cheap, schemas are not, and schemas are only loaded when selected. It is easy to miss
precisely because it works silently.

**Servers can still be pending when the session starts.** Absence of a capability at the first
turn is not absence of the capability — the registry populates asynchronously.

**An operating mode can withdraw first-class tools and name the substitute in the error.** The
message does not merely refuse; it prescribes an alternative. **Do not write agent definitions
that assume a fixed tool surface** — the surface is mode-dependent.

**An oversized tool result is spilled to a file, not discarded.** The error names the path.
Re-running the expensive call is wasted work; page through what is already on disk.

---

## Sandbox

⛔ **A sandbox denial does not fail the command. It annotates it.** Blocked egress appears as a
violations block appended to stderr, while the tool result itself is **marked as not an error**.
The command's own exit status decides the verdict.

⭐ **This is the quiet one.** A script that phones home, is blocked, and continues will report
success. Anything built on "the command succeeded" inherits the hole. **To know that a part of
the work did not happen, you have to parse the annotation** — the exit code will not tell you.

---

## The model can change under you

**Mid-session, without the conversation noticing.** A system record announces a switch to a
different model under load, naming both. Cascading switches were observed **under half a second
apart** in a single session.

**And a safety refusal retries on a different model and *may* retract messages already in the
conversation** — when it does, the record carries the list of retracted message ids. It did not
in every observed case.

⛔ **Two consequences.** Any evaluation assuming a fixed model across a session is measuring a
**mixture**, and a quality drop may have nothing to do with your prompt. And any external mirror
of the conversation you maintain **can silently diverge from what the model actually sees**,
because history is not append-only.

---

## What you actually pay for

**Essentially the entire input is cache reads** — in one corpus the median share of input tokens
served from cache was above 99%, with cache reads exceeding cache writes by roughly fifty to one
*(workload-dependent; the ratio is not a product constant, the shape is)*.

⛔ **This inverts the obvious optimisation.** Trimming the tail of a conversation saves almost
nothing. **Editing anything near the top of the prompt — an instruction file, a tool listing, a
system-level block — invalidates the prefix and forces it to be written again at write prices.**

⭐ **The cost of a one-character change to a session-loaded instruction file is the whole
prefix, for that session.** This is the economic argument behind everything in §"Files that load
every session", and it is invisible unless you look at the usage fields on each call.

**Two cache lifetimes run simultaneously** — a long tier and a short one, split visibly per call.
Modelling the cache as a single TTL will mislead you: durable prefix material and volatile
material are placed differently.

---

## Checking these yourself

None of this requires special access. The runtime writes a structured transcript per session; it
is a **system of record, not a chat log** — in one corpus roughly half of all records were
machinery rather than conversation *(workload-dependent — the ratio moves with which host
features an operator actually uses; the shape is the point, not the number)*, including full
system-prompt snapshots, per-message file
backup snapshots and deltas (which is how *"this file changed since you read it"* is detected),
and permission-mode changes as first-class events.

⛔ **A limit worth stating, precisely because the method makes it reachable.** Those transcripts
also carry material that belongs to the vendor rather than to you — verbatim system prompts among
it. Establishing that such records *exist* is observation of behaviour. Republishing their
*contents* is not, and is outside both this method and this page: treat vendor-authored text
sitting in your own transcripts as the vendor's, and leave it where it landed. Nothing of that
kind is reproduced here, and nothing of that kind belongs in what you publish either.

To reproduce the method:

0. **Stay on the observation side of the line.** Everything below reads files the product writes
   to your own disk during ordinary licensed use. None of it involves decompiling or disassembling
   the software, inspecting its packaged code, intercepting its network traffic, or defeating any
   technical measure — and none of it needs to. If a question can only be answered by one of
   those, it is out of scope for this method and for this page.
1. **Find your transcript directory** and treat one file as the unit.
2. **Tally record types and subtypes** before reading anything. The schema tells you what
   mechanisms exist; prose does not.
3. **Stratify by product version before concluding anything from an absence.** A field that does
   not exist in older records makes every older record look negative. This control killed one of
   our findings outright — see below.
4. **Run a positive control on every negative result.** If you claim a record does not exist,
   prove in the same pass that your search finds the records that *do*.
5. **Distinguish runtime-emitted strings from your own text echoed back.** The text of your
   instruction files comes back into context, so a grep across transcripts will find *your own
   documentation* and it will look like evidence. This is the single easiest way to fool
   yourself here.
6. **To test what an instruction file delivers, hide a unique token and plant a control.** Put
   a random token inside the construct you are testing (a comment, a block, a trailing tag) and
   a visible random token in the same file; ask a fresh session, with no tools, to list every
   token of that shape it was given. The visible token must come back, or the file never loaded
   and the run says nothing. A token that comes back and is not in your key means the answer is
   invented, and the run says nothing either.

---

## What we could not establish

Stated because a gap named is worth more than a gap implied:

- **The permission matcher.** Which command shapes defeat static analysis, and which rule syntax
  is silently ignored — widely believed, and we found **no runtime-emitted evidence for any of
  it**. Every apparent hit was an operator's own documentation echoed back into context. The
  belief may well be correct; we cannot support it from observation, so this page does not.
- **Why tools are withdrawn** in each case. The mechanism is evidenced; the cause is not.
- **Whether the compaction thresholds hold at other context sizes.** All observations came from
  a single window size.
- **Exactly what "rendered into context" means** in every case. Claims here are restricted to the
  cleanest cases and the ambiguous middle was left out rather than reported as a ratio.
- **Whether any of this varies by platform or configuration.** Every observation comes from a
  single operator, on one operating system, under one configuration. Nothing here has been
  cross-checked against a second deployment — which is the widest bound on the whole page.

⚠️ **The finding most likely to expire first is the permission attribution gap.** A single
release that adds a decision record would turn it from a true statement into a stale one, and
nothing in the transcript would announce that it had changed.

⭐ **A worked example of why the last item in "Checking these yourself" matters.** The first draft
of this page claimed permission refusals were only visible in two forms. A second pass found a
third, emitted by the runtime itself — and the earlier claim had been built on a search whose
hits were overwhelmingly the operator's **own prose**, echoed back into context by the very
mechanism described in §"Files that load every session". The corrected finding above is sharper
than the one it replaced. **If it happened here, on a page written to guard against exactly
this, assume it can happen to you.**

---

## Corrections

**2026-09-24 — finding 1 (HTML comments) was wrong as published.**

- **What the page said:** HTML comments in instruction files are not stripped; every comment
  body tested was present in context; this was "the finding to lead with".
- **What is observed now:** comments on their own line, and multi-line comment blocks, did
  **not** reach context; a comment that shares its line with text — at the end of a line, at
  the end of a heading, or mid-line — **did**. The table in §"Comments: free or not depends on
  where they sit" gives each cell and the method behind it, including the cells that were not
  tested.
- **Measured the same day:** the placements this correction first left untested in the
  instruction file and the rules file — a comment at the end of a line, at the end of a
  heading, and mid-line, plus a block in the instruction file — were measured on 2026-09-24 by
  a controlled probe in an isolated project, with a visible control token in each file and an
  answer key to catch invented tokens. Both controls held. Only memory-index cells remain
  untested.
- **How it was found:** a short trailing comment on a heading was seen in a live session's
  context, which is what the original claim predicted — but the own-line and block comments
  loaded in the same session were absent, which it did not. A controlled probe, run before this
  page was first published, had already shown own-line and block comments being removed. **It
  was not reconciled with this page before publication** — that part is our process failure.
  Whether the product also changed in between, we cannot exclude: there are measurements from
  before publication and from after, and none from the day.
- **Why the original test came out the other way:** not established. We have not re-run it, and
  we do not guess at it here. §"Checking these yourself", item 5, names the most likely way to
  fool yourself with this kind of search; we cannot say it is what happened.
- **What did not change:** the cost argument in §"What you actually pay for" — an edit near the
  top of the prompt is paid for as a whole prefix — stands. It now applies to comments that
  reach context, not to all of them.

---

## See also

- `docs/13-runtime-requirements.md` — the six capabilities this page is the behavioural
  counterpart to
- `docs/05-guardrails.md` and `examples/guardrails/` — the design pattern these facts constrain
- `patterns/adversarial-review/` — why a probe must prove it can see its target
- `patterns/provenance-and-dating/` — the dating discipline this page is written under
