#!/usr/bin/env bash
# sql-readonly.pseudo.sh
# SKELETON / PSEUDO-CODE -- NOT runnable as-is. Tokens {{...}} must be filled in.
# Illustrates: the state database is read-only by default. Read statements pass;
# anything that could mutate or drop data is blocked. The concrete statement
# classifier is left as <is_read_only()> -- each install provides its own.
#
# Output convention: exit 0 = allow, exit != 0 = block (reason on stderr).

# --- SKELETON GUARD: this file is illustrative and must not run as-is --------
echo "SKELETON, not a runnable hook. Fill in {{...}} / <...> tokens first." >&2
exit 3

set -u

SQL_STATEMENT="{{SQL_STATEMENT}}"     # the statement the caller wants to run

if [ -z "${SQL_STATEMENT}" ]; then
  echo "block: empty statement (fail-safe over-block)" >&2
  exit 2
fi

# A read-only statement is one that cannot mutate state. A real classifier must
# handle comments, multiple statements, and quoting -- a keyword grep is NOT
# enough (it is a bypass). Left as a placeholder function.
if <is_read_only "${SQL_STATEMENT}">; then
  exit 0                              # read -> allow
else
  echo "block: non-read statement against a read-only database" >&2
  # ... log the blocked statement to an append-only audit log ...
  exit 2
fi
