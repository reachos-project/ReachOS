#!/usr/bin/env bash
# workspace-enforcement.pseudo.sh
# SKELETON / PSEUDO-CODE -- NOT runnable as-is. Tokens {{...}} must be filled in.
# Illustrates: an agent may only write inside its own workspace; writes elsewhere
# are denied and logged. Detection specifics are intentionally left as tokens.
#
# Output convention: exit 0 = allow, exit != 0 = block (reason on stderr).
#
# LOAD-BEARING: the `exit 3` guard below is the ONLY thing that stops this file from running.
# `bash -n` on it returns 0 -- {{TOKEN}} is valid shell, so the tokens do NOT break execution.
# Remove the guard last, after every token is filled in, never while editing.

# --- SKELETON GUARD: this file is illustrative and must not run as-is --------
echo "SKELETON, not a runnable hook. Fill in {{...}} / <...> tokens first." >&2
exit 3

set -u

# --- inputs provided by the tool boundary (structured payload) --------------
AGENT_SLUG="{{AGENT_SLUG}}"            # e.g. market-analyst
WRITE_TARGET="{{WRITE_TARGET_PATH}}"  # absolute path the agent wants to write

# Each agent's allowed workspace root. Fictional example base:
WORKSPACE_ROOT="/opt/halcyon/assistant/workspaces/${AGENT_SLUG}"

# --- fail-safe: if we cannot parse the target, block ------------------------
if [ -z "${WRITE_TARGET}" ]; then
  echo "block: empty/unparseable write target (fail-safe over-block)" >&2
  exit 2
fi

# --- decision: target must be INSIDE the agent workspace --------------------
# NOTE: a real implementation resolves symlinks and normalises '..' before the
#       prefix check -- a naive prefix match is a bypass. Left as <resolve()>.
RESOLVED="$(<resolve_and_normalise "${WRITE_TARGET}">)"

case "${RESOLVED}" in
  "${WORKSPACE_ROOT}"/*)
    exit 0 ;;                          # inside workspace -> allow
  *)
    echo "block: write outside workspace ${WORKSPACE_ROOT}: ${RESOLVED}" >&2
    # ... append to an append-only audit log here ...
    exit 2 ;;
esac
