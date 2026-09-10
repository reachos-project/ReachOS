# Settings sync — what must be identical across configuration vaults

<!--
  Use this when the assistant's configuration directory is selected per entry path
  (local vs remote, one shell branch) — see docs/11. Fill the table for your installation
  and keep it next to the vaults. Nothing here should contain secrets or real paths.
-->

**Vaults:** `{{VAULT_LOCAL}}` · `{{VAULT_REMOTE}}` (add more if more entry paths exist).
**Rule:** a change to any row below is applied to **every** vault in the **same** window, and
verified by behaviour after restart in **each** entry path — not by reading the file back.

| Item | Must be identical? | Why | How verified |
|---|---|---|---|
| Permission mode (auto / allow-unless-blocked / list-only) | **yes** | decides what runs unattended; a mismatch is a coin flip decided when the multiplexer started | one blocked command blocked, one allowed command allowed, from each entry path |
| `deny` list | **yes** | the only layer that blocks under allow-unless-blocked | probe one entry per class (destructive verb, protected path, network) |
| `allow` list | should be | prompts differ per entry path otherwise; not security-relevant under allow-unless-blocked | count of prompts in a routine session |
| Sandbox profile (filesystem read/write denies, network egress) | **yes** | the OS-level floor; a vault without it runs unsandboxed | attempt a read of a denied path from each entry path |
| Hooks (which, on which tool boundary, deny-only) | **yes** | a hook present in one vault only means a control that exists "sometimes" | fire each hook once with a known-bad input |
| Rules loaded per session | **yes** | behaviour doctrine; drift here is silent | hash the rules directory in both vaults |
| Agent definitions | **yes** | boot cache — only reloaded at restart | hash; then restart |
| Tool/server registrations (MCP-style) | should be | a tool missing on one path fails as "not available" | list tools from each entry path |
| Secrets / credentials | **no — never copied by this procedure** | live in their own store; a sync script that touches them is a leak vector | — |

## Procedure

1. Edit the **source** copy (pick one vault as source, write it down).
2. Apply to the other vault(s) with a byte copy — **not** a metadata-preserving copy, which
   propagates immutability flags and breaks the next attempt.
3. Re-baseline whatever tripwire watches these files, in the same window.
4. Restart the assistant; run the "how verified" column from **each** entry path.
5. Log: what changed, both vault hashes after, who verified.

⚠️ **The shell branch that selects the vault is evaluated once, at shell start-up**, by
variables the multiplexer froze. Do not test "which vault am I in" by inspecting variables;
test it by asking the runtime which config it loaded, or by the behaviour probes above.
