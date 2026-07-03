#!/usr/bin/env python3
# content-inspection.pseudo.py
# SKELETON / PSEUDO-CODE -- NOT runnable as-is. The <<FILL: ...>> tokens are
# invalid Python on purpose (SyntaxError), so this file cannot be compiled or
# executed against a real system until an implementer fills them in.
#
# Illustrates layer C2 (pre-execution content inspection):
#   * robust structured extraction of the command (NOT a fragile regex)
#   * detection of destructive ops on critical paths (signature sets omitted)
#   * fail-safe: block on parse failure
#   * output convention: allow() -> exit 0, deny(reason) -> exit != 0 + stderr
#
# The real DESTRUCTIVE_VERBS / CRITICAL_PATHS / matching logic are configuration
# of each install and are deliberately NOT shipped here (see
# patterns/defense-in-depth/ for why: publishing signatures aids evasion).

import sys

# Placeholders -- each install fills these from its OWN private config.
# The <<FILL: ...>> tokens are deliberately invalid Python (SyntaxError) so this
# skeleton cannot be run as-is.
DESTRUCTIVE_VERBS = <<FILL: set of destructive verbs -- not shipped>>
CRITICAL_PATHS    = <<FILL: globs of protected critical paths -- not shipped>>


def parse_tool_payload(raw):
    """Structured parse of the tool payload (JSON), never a fragile regex.
    A regex that stops at the first escaped quote is a bypass waiting to happen.
    """
    ...  # real parser here


def references_destructive_op(command, verbs):
    """True if `command` invokes a destructive op, including indirectly
    (the critical path passed as an argument to another command or script)."""
    ...


def touches_any(command, path_globs):
    ...


def deny(reason):
    sys.stderr.write("block: %s\n" % reason)
    sys.exit(2)


def allow():
    sys.exit(0)


def main():
    raw = sys.stdin.read()
    payload = parse_tool_payload(raw)
    if payload is None:
        deny("malformed payload -- fail-safe over-block")   # fail-safe

    command = payload.command
    if references_destructive_op(command, DESTRUCTIVE_VERBS) \
       and touches_any(command, CRITICAL_PATHS):
        deny("destructive operation on a critical path")

    allow()


if __name__ == "__main__":
    main()
