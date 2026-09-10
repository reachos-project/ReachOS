# Two-way messaging for a sandboxed agent

*A validated pattern and its findings — not an installable implementation.*

This note describes how an autonomous agent that runs inside an OS sandbox can hold a
two-way text conversation with its human operator over a consumer messaging service,
without weakening the sandbox that confines it. It is written from a working channel
that was validated end-to-end on one machine. It is a **pattern**, not a product: there
is no code here, and nothing in it has been tested on a second configuration.

---

## The problem

A useful autonomous agent needs a back-channel to a human: to report, to ask, to be
steered when the operator is away from a terminal. A consumer messaging service (an
iMessage-style platform tied to the operator's account) is attractive because it is
already on the operator's phone and survives hostile networks that kill SSH and VPNs.

But the agent runs confined. The same sandbox that makes the agent safe to run also
blocks it from driving the OS automation that would send a message. The naïve fix —
give the agent a send command — is exactly the capability you spent effort removing.
The pattern below keeps the send capability **out** of the confined process and still
gets messages delivered.

---

## The finding: sandboxing re-attributes automation identity

On macOS, sending a message programmatically means driving the messaging app through
its scripting interface (Apple Events, typically via `osascript`). Access to that
interface is gated by the OS automation-consent subsystem (TCC): the *responsible*
process must hold a granted "control this app" permission.

The non-obvious failure: **wrapping the send command inside a sandbox re-attributes the
TCC responsibility to the sandbox wrapper.** If you take a command that would send fine
on its own and run it under a sandboxing tool, the OS now asks "does the *sandbox
wrapper* have automation consent?" — and it does not. Under a background launcher there
is no UI to answer the consent prompt, so the request is never satisfied and the send
hangs until it times out. The sandbox is not *denying* the send; the confidentiality
layers are all fine. The consent simply belongs to the wrong identity.

This is the crux, and it dictates the architecture: **you cannot both confine the
sender and let it hold automation consent.** So don't. Split them.

---

## The pattern: two jobs, one outbox

Separate the work into two scheduled jobs with different privileges:

- **Job A — the confined daemon.** Runs inside the tight sandbox. It does everything the
  agent-facing logic needs *except* send: it reads the agent's intent, validates it,
  builds the outgoing record, and writes it to a single **outbox**. It has no network
  and no automation consent. If it is ever compromised, the blast radius is "can write a
  file to one directory."
- **Job B — the sender.** Runs *outside* the write-sandbox, launched directly (no
  wrapper), so it keeps the automation consent that was granted to the real send binary.
  It does one thing: read a record from the outbox and hand it to the messaging app.
  It holds no agent logic and makes no decisions.

The outbox is the airlock. The confined side can only *propose* a message by dropping a
file; the privileged side *disposes* by sending it. Neither side holds both the agent's
reasoning and the OS's send capability at the same time. That separation is the whole
security argument.

A consequence worth stating plainly: **Job B must treat the outbox as hostile input.**
It is written by a less-trusted process, so the sender re-validates every record —
length, character set, destination — rather than trusting that Job A got it right. The
recipient of a message is fixed in the sender, not carried in the record, so a
compromised outbox cannot redirect a message to a new address.

---

## The provenance envelope

Every outbound message carries a mandatory, non-suppressible **envelope**: a short
banner at the very start and a trailer at the end, marking the message as coming from
the autonomous agent. Two reasons, both load-bearing:

1. **The human must never mistake the agent for a person.** On a shared thread the
   operator has to know, at a glance, that a message was machine-originated — especially
   because an autonomous channel can carry requests, and a request that looks like it
   came from a trusted human is a social-engineering vector waiting to happen.
2. **The receiver uses the envelope to recognise its own output** (see the echo trap).

The envelope is applied by the privileged sender, where the confined side cannot strip
it, and its provenance marking fails safe: if anything is ambiguous, it is marked as
machine-originated, never as human.

---

## The echo trap

If the agent and the operator share one account — the agent sends *as* the operator's
account back to that same account — then **every message the agent sends reappears to it
as an incoming message.** A receiver that naïvely ingests all inbound traffic will read
its own output, react to it, possibly reply to it, and loop.

The fix falls straight out of the envelope: the receiver recognises the agent's own
envelope on an inbound message and drops it. The banner-plus-trailer must match for the
drop to fire, so a genuine human message that merely quotes the agent is not
accidentally swallowed. This has to be designed in from the first message, not bolted on
after the loop appears.

---

## Operational lessons

- **Inbound is data, never authority.** A message arriving on an unauthenticated
  consumer channel is *information*, never consent and never an instruction that carries
  privilege. "I changed my number, do X" is not honoured; a message never authorises a
  privileged or irreversible action on its own. Anything gated stays gated behind the
  controls that were already there — the channel does not become a new path around them.
  This is the single most important rule and the easiest to get wrong once the channel
  feels conversational.

- **A rate limit tuned for alerts strangles a conversation.** A cap sized for occasional
  autonomous notifications (a handful per hour) will silently starve a live back-and-
  forth: replies queue, arrive minutes late, and — if there is a time-to-live on queued
  items — some are dropped outright, which reads to the human as the agent going silent.
  The burst you actually need to bound is already bounded by the daemon's poll interval;
  so prefer a short **inter-send interval** plus a **generous daily backstop**, not a
  tight hourly cap. Make the limit fit the *interactive* case, and note that the limit
  protects outbound only — the human's inbound should never be throttled.

- **Delivery is asynchronous; don't read "queued" as "delivered."** With the two-job
  split, the confined side only knows the message reached the outbox. Whether it left
  the machine is the sender's business, recorded on the sender's side. A monitor that
  checks only the hand-off log will report false success. Reconcile against the side that
  actually sends.

- **Validate the full text path, including non-ASCII.** Accented characters and anything
  that has to survive an intermediate scripting layer must be tested end-to-end, from
  the agent's intent to the message as received. Escaping bugs hide here.

- **Fail open on the process, closed on the message.** A single malformed record must
  not kill the daemon; it should be rejected and logged, and error logging itself should
  be rate-limited so a storm of failures cannot exhaust the log.

- **Same-user is not an authentication boundary.** If both jobs run as the same OS user,
  nothing cryptographic separates them — the confined side could, in principle, forge
  what the privileged side reads. The separation here is one of *capability and
  structure* (who holds automation consent, who can reach the network), not of identity.
  Be honest about which guarantee you have.

---

## Frontier — what this pattern does *not* yet claim

- It was validated on **one** machine and **one** OS version. Portability to another
  configuration is untested.
- The **stop controls** for the channel were reasoned about but not put through a formal
  drill; treat "you can always cut it" as designed-in, not proven.
- A **full acceptance battery** was not run; the evidence is end-to-end delivery,
  correct rendering, echo suppression, and integrity — not exhaustive coverage.
- The same-user forge path above is an **accepted residual**, not a closed hole.

If any of these matters for your use, close it before you rely on the channel. Publishing
prose that describes a validated design is honest; shipping code that others install
would demand a level of assurance this pattern does not yet carry — which is why there
is no code here.
