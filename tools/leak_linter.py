#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
leak_linter.py  --  Anti-leak linter for the enterprise-open clean-room repo.

Hardened after internal security review. The --public mode and --redact-matches
flag implement the split-linter safe-variant from that review.

WHAT IT DOES
------------
Scans a staging tree (default: ../repo-staging) for:

  BLOCK  -- real internal identifiers that MUST NEVER leave the private repo:
            18 real personas + surnames, orchestrator/owner handles, real path
            roots, infra hostnames/channels, incident refs (BSR-), real DB
            schema identifiers, and secret/token/baseline-SHA patterns.
            One or more BLOCK => process exit code != 0 (build-breaking).

  WARN   -- non-blocking signals that demand *conscious* acknowledgment:
            * upstream-name-overlap        : a staging file/name reproduces a
              name that exists in the freskhu/genesis upstream tree.
            * mempalace-taxonomy-unattributed : MemPalace/mempalace taxonomy
              (wings/halls/drawers/...) used in a file with NO acknowledgment
              marker on the same page.

MODES
-----
Default (no flag): full private run; SELF-CHECK refuses (exit 3) if this
  script or the deny-list JSON is found inside the staging tree -- neither
  may ever ship in the public repo. Verbose match output.

--public: safe variant for public CI. Fail-closed via an allowlist inversion:
  exits 3 unless EVERY loaded block rule's category is in the public-allowed
  set {secret, secret-baseline}. Unknown/new categories therefore fail closed
  by default instead of slipping through. Self-check adapted: linter/public-
  deny-list presence inside the staging tree is expected and NOT flagged.
  Detection of the private deny-list is delegated to the internal_artifacts
  tripwire in the public deny-list. Always combine with --redact-matches in CI.

--maintainer (alias --allow-shipped-tool): maintainer axis-A run over a tree
  that legitimately SHIPS the linter. Loads the FULL private deny-list (all
  axis-A rules active) but the self-check treats the shipped artefacts
  (leak_linter.py, leak_linter_denylist.public.json) inside the staging tree
  as EXPECTED and does not flag them. The never-ship deny-lists
  (leak_linter_denylist.json, leak_linter_denylist.private.json) remain fatal
  if found inside staging. Mutually exclusive with --public (exit 3 if both).

--redact-matches: suppresses match values and context lines in ALL output
  (text and JSON). Match is replaced with <redacted:N chars>; context is
  replaced with <redacted>. Use in public CI to prevent any matched value
  from appearing in public job logs (C2).

DESIGN
------
* Python 3 stdlib only. Single file.
* All match rules live in a SEPARATE data file (leak_linter_denylist.json for
  the full private run; leak_linter_denylist.public.json for public CI) so
  the reviewer can audit/extend the deny-list without touching code.
* SELF-CHECK (private mode): refuses to run if this script OR the deny-list
  JSON is found inside the staging tree.
* PUBLIC-MODE SELF-CHECK: skipped entirely; relies on internal_artifacts.
* Exit codes: 0 = PASS (0 BLOCK) / 2 = FAIL (>=1 BLOCK) /
              3 = self-check fail / public-mode fail-closed / bad args.

USAGE
-----
  # Private/maintainer run (full deny-list, verbose):
  python3 leak_linter.py
  python3 leak_linter.py --staging /abs/path/to/repo
  python3 leak_linter.py --denylist /abs/path/to/leak_linter_denylist.json

  # Public CI run (axis-B only, fail-closed, redacted output):
  python3 leak_linter.py --public --staging . \\
      --denylist tools/leak_linter_denylist.public.json --redact-matches
"""

import argparse
import json
import os
import re
import sys

# ---- text file extensions we scan (skip binaries) -------------------------
TEXT_EXTS = {
    ".md", ".markdown", ".txt", ".sql", ".json", ".py", ".sh", ".bash",
    ".yml", ".yaml", ".toml", ".cfg", ".ini", ".env", ".template", ".example",
    ".js", ".ts", ".css", ".html", ".xml", ".csv", "",  # "" = no-ext files
}

SELF_FILES = {"leak_linter.py", "leak_linter_denylist.json"}

# Maintainer mode: files that legitimately ship in the public repo tree and are
# therefore EXPECTED to live inside staging. They are NOT flagged by the
# self-check when running with --maintainer.
MAINTAINER_EXPECTED_FILES = {"leak_linter.py", "leak_linter_denylist.public.json"}

# Files that must NEVER ship in the public repo tree, in ANY mode: the full and
# private deny-lists carry real identifiers. Presence inside staging is fatal.
NEVER_SHIP_FILES = {"leak_linter_denylist.json", "leak_linter_denylist.private.json"}

# Descriptive: axis-A categories that carry real identifiers and must never
# appear in a public deny-list. Kept for documentation of the axis-A surface;
# the public gate below enforces an allowlist inversion rather than this set.
SENSITIVE_CATEGORIES = {
    "real-persona",
    "real-persona-surname",
    "real-orchestrator",
    "real-owner-handle",
    "real-path",
    "real-infra",
    "secret-channel",
    "internal-incident-ref",
    "real-schema",
}

# --public allowlist: the ONLY categories permitted in a public deny-list.
# The public gate fails closed (exit 3) if any loaded block rule has a category
# outside this set, so unknown/new categories fail closed by default (hardening
# from an internal security review).
PUBLIC_ALLOWED_CATEGORIES = {"secret", "secret-baseline"}


def _flags(spec):
    f = 0
    if spec and "i" in spec:
        f |= re.IGNORECASE
    return f


def _line_of(text, pos):
    """1-based line number of character offset `pos`."""
    return text.count("\n", 0, pos) + 1


def _line_text(text, pos):
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end == -1:
        end = len(text)
    return text[start:end]


def load_denylist(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    compiled_block = []
    for rule in data.get("block", []):
        try:
            rx = re.compile(rule["regex"], _flags(rule.get("flags", "")))
        except re.error as exc:
            sys.stderr.write(
                "[denylist] bad regex in rule '%s': %s\n" % (rule.get("id"), exc)
            )
            raise
        exempt = rule.get("exempt_regex")
        exempt_rx = re.compile(exempt, re.IGNORECASE) if exempt else None
        compiled_block.append({
            "id": rule.get("id", rule["regex"]),
            "rx": rx,
            "exempt": exempt_rx,
            "category": rule.get("category", "unknown"),
            "note": rule.get("note", ""),
        })

    up = data.get("upstream_names", {})
    up_ignore = {n.lower() for n in up.get("ignore_universal", [])}
    up_names = []
    for name in up.get("names", []):
        # token match allowing -, _ or space between parts; word-bounded
        parts = re.split(r"[-_ ]+", name)
        pat = r"\b" + r"[-_ ]".join(re.escape(p) for p in parts) + r"\b"
        up_names.append((name, re.compile(pat, re.IGNORECASE)))

    mp = data.get("mempalace_terms", {})
    mp_ack = [m.lower() for m in mp.get("acknowledgment_markers", [])]
    mp_terms = [(t, re.compile(t, re.IGNORECASE)) for t in mp.get("terms", [])]

    # assert-absent tripwire (internal review invariant): basenames that must NEVER live
    # inside staging. Presence => synthetic BLOCK. NOT a scan-skip.
    internal_artifacts = data.get("internal_artifacts", {}).get("basenames", [])

    return {
        "block": compiled_block,
        "up_ignore": up_ignore,
        "up_names": up_names,
        "mp_ack": mp_ack,
        "mp_terms": mp_terms,
        "internal_artifacts": internal_artifacts,
    }


def check_internal_artifacts(staging_root, basenames):
    """Assert-absent invariant enforcement (internal review invariant, C1).

    Walk the WHOLE staging tree (any extension, not just text) and flag any
    file whose basename is on the internal-artifacts list. These are internal
    build-audit artifacts that legitimately carry real identifiers and MUST
    NOT live in the shippable tree. Presence => BLOCK (exit != 0).
    """
    wanted = set(basenames)
    hits = []
    for dirpath, dirnames, filenames in os.walk(staging_root):
        dirnames.sort()
        if ".git" in dirnames:
            dirnames.remove(".git")
        for fn in sorted(filenames):
            if fn in wanted:
                rel = os.path.relpath(os.path.join(dirpath, fn), staging_root)
                hits.append(rel)
    return hits


def iter_text_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        if ".git" in dirnames:
            dirnames.remove(".git")
        for fn in sorted(filenames):
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS:
                yield os.path.join(dirpath, fn)


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (UnicodeDecodeError, OSError):
        return None  # binary / unreadable -> skip


def scan_file(path, rel, text, dl):
    """Return list of finding dicts for one file."""
    findings = []

    # ---- BLOCK rules -----------------------------------------------------
    for rule in dl["block"]:
        for m in rule["rx"].finditer(text):
            line_txt = _line_text(text, m.start())
            if rule["exempt"] and rule["exempt"].search(line_txt):
                continue
            findings.append({
                "severity": "BLOCK",
                "rule": rule["id"],
                "category": rule["category"],
                "line": _line_of(text, m.start()),
                "match": m.group(0),
                "context": line_txt.strip()[:120],
            })

    # ---- WARN: upstream-name-overlap ------------------------------------
    base = os.path.basename(rel).lower()
    base_stem = os.path.splitext(base)[0]
    for name, rx in dl["up_names"]:
        if name.lower() in dl["up_ignore"]:
            continue
        # (a) filename overlap
        if rx.search(base_stem) and base_stem not in dl["up_ignore"]:
            findings.append({
                "severity": "WARN",
                "rule": "upstream-name-overlap",
                "category": "upstream:" + name,
                "line": 0,
                "match": base,
                "context": "filename overlaps genesis name '%s'" % name,
            })
        # (b) content overlap (first occurrence is enough to signal)
        m = rx.search(text)
        if m:
            findings.append({
                "severity": "WARN",
                "rule": "upstream-name-overlap",
                "category": "upstream:" + name,
                "line": _line_of(text, m.start()),
                "match": m.group(0),
                "context": _line_text(text, m.start()).strip()[:120],
            })

    # ---- WARN: mempalace-taxonomy-unattributed --------------------------
    low = text.lower()
    has_ack = any(marker in low for marker in dl["mp_ack"])
    if not has_ack:
        for term, rx in dl["mp_terms"]:
            m = rx.search(text)
            if m:
                findings.append({
                    "severity": "WARN",
                    "rule": "mempalace-taxonomy-unattributed",
                    "category": "mempalace:" + term,
                    "line": _line_of(text, m.start()),
                    "match": m.group(0),
                    "context": _line_text(text, m.start()).strip()[:120],
                })

    return findings


def self_check(staging_root, linter_path, denylist_path, mode="default"):
    """Check that linter and deny-list are not inside the staging tree.

    mode="public": the linter and its public deny-list are expected to live
      inside the scanned repo tree, so all path-prefix and SELF_FILES checks are
      skipped. Detection of the private deny-list is instead delegated to the
      internal_artifacts tripwire in the public deny-list.

    mode="maintainer": the shipped artefacts (leak_linter.py,
      leak_linter_denylist.public.json) are EXPECTED inside the staging tree and
      are NOT flagged. The never-ship deny-lists (full/private, which carry real
      identifiers) remain fatal if found inside staging.

    mode="default": the original private-run behaviour is preserved unchanged.
    """
    if mode == "public":
        return []

    if mode == "maintainer":
        # Only assert absence of the never-ship deny-lists; the shipped linter
        # and public deny-list are expected artefacts of the public tree.
        problems = []
        for dirpath, _dirs, files in os.walk(staging_root):
            for fn in files:
                if fn in NEVER_SHIP_FILES:
                    problems.append(os.path.join(dirpath, fn))
        return problems

    staging_abs = os.path.abspath(staging_root)
    problems = []
    for p in (linter_path, denylist_path):
        if os.path.abspath(p).startswith(staging_abs + os.sep):
            problems.append(p)
    # also: no file NAMED like our tool inside staging
    for dirpath, _dirs, files in os.walk(staging_root):
        for fn in files:
            if fn in SELF_FILES:
                problems.append(os.path.join(dirpath, fn))
    return problems


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    default_staging = os.path.normpath(os.path.join(here, "..", "repo-staging"))
    default_denylist = os.path.join(here, "leak_linter_denylist.json")

    ap = argparse.ArgumentParser(description="Anti-leak linter for enterprise-open.")
    ap.add_argument("--staging", default=default_staging,
                    help="staging tree to scan (default: ../repo-staging)")
    ap.add_argument("--denylist", default=default_denylist,
                    help="deny-list JSON (default: ./leak_linter_denylist.json)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--public", action="store_true",
                    help="public CI mode: fail-closed unless every deny-list "
                         "category is in the public allowlist {secret, "
                         "secret-baseline}; self-check adapted for a "
                         "repo-committed linter")
    ap.add_argument("--maintainer", "--allow-shipped-tool", action="store_true",
                    dest="maintainer",
                    help="maintainer axis-A run over a tree that legitimately "
                         "ships the linter: full deny-list active, but the "
                         "shipped linter + public deny-list inside staging are "
                         "expected and not flagged. Mutually exclusive with "
                         "--public")
    ap.add_argument("--redact-matches", action="store_true",
                    help="suppress match values and context lines in all output "
                         "to prevent secrets from appearing in public CI logs")
    args = ap.parse_args(argv)

    if args.public and args.maintainer:
        sys.stderr.write(
            "ERROR: --public and --maintainer are mutually exclusive\n")
        return 3

    if args.public:
        mode = "public"
    elif args.maintainer:
        mode = "maintainer"
    else:
        mode = "default"

    if not os.path.isdir(args.staging):
        sys.stderr.write("ERROR: staging dir not found: %s\n" % args.staging)
        return 3
    if not os.path.isfile(args.denylist):
        sys.stderr.write("ERROR: denylist not found: %s\n" % args.denylist)
        return 3

    # SELF-CHECK -----------------------------------------------------------
    # public   : returns [] immediately; relies on internal_artifacts.
    # maintainer: asserts only the never-ship deny-lists are absent from staging.
    # default  : unchanged behaviour from the original private linter.
    problems = self_check(args.staging, __file__, args.denylist, mode=mode)
    if problems:
        sys.stderr.write(
            "SELF-CHECK FAIL: linter/denylist must NOT be inside staging:\n"
        )
        for p in problems:
            sys.stderr.write("  - %s\n" % p)
        return 3

    dl = load_denylist(args.denylist)

    # PUBLIC-MODE FAIL-CLOSED (allowlist inversion) -------------------------------
    # After loading, reject the deny-list unless EVERY block rule's category is
    # in the public allowlist {secret, secret-baseline}. This fails closed for
    # unknown/new categories (they slip through a deny-only check), and in
    # particular causes a hard build break (exit 3) when --public is accidentally
    # pointed at the private deny-list rather than silently scanning with
    # sensitive rules and logging real identifiers to the public CI log.
    if args.public:
        disallowed_cats = sorted({
            rule["category"]
            for rule in dl["block"]
            if rule["category"] not in PUBLIC_ALLOWED_CATEGORIES
        })
        if disallowed_cats:
            for cat in disallowed_cats:
                sys.stderr.write(
                    "PUBLIC-MODE FAIL: non-allowlisted category '%s' in "
                    "deny-list %s\n" % (cat, args.denylist)
                )
            return 3

    per_file = []
    total_block = 0
    total_warn = 0
    files_scanned = 0

    for path in iter_text_files(args.staging):
        text = read_text(path)
        if text is None:
            continue
        files_scanned += 1
        rel = os.path.relpath(path, args.staging)
        findings = scan_file(path, rel, text, dl)
        if findings:
            findings.sort(key=lambda f: (f["severity"] != "BLOCK", f["line"]))
            per_file.append((rel, findings))
            total_block += sum(1 for f in findings if f["severity"] == "BLOCK")
            total_warn += sum(1 for f in findings if f["severity"] == "WARN")

    # assert-absent tripwire: internal build-audit artifacts must not exist in
    # the shippable tree (internal review invariant, C1). Synthetic BLOCK per hit.
    per_file_map = dict(per_file)
    for rel in check_internal_artifacts(args.staging, dl["internal_artifacts"]):
        finding = {
            "severity": "BLOCK",
            "rule": "internal-artifact-in-staging",
            "category": "internal-artifact",
            "line": 0,
            "match": os.path.basename(rel),
            "context": "internal build-audit artifact must not live in the "
                       "shippable tree",
        }
        per_file_map.setdefault(rel, []).insert(0, finding)
        total_block += 1
    per_file = sorted(per_file_map.items(), key=lambda x: x[0])

    for _rel, _fs in per_file:
        _fs.sort(key=lambda f: (f["severity"] != "BLOCK", f["line"]))

    # OUTPUT ---------------------------------------------------------------
    # --redact-matches: replace match value with <redacted:N chars> and omit
    # context entirely. Applied at output time; raw findings used for counting.
    if args.format == "json":
        files_out = []
        for rel, fs in per_file:
            findings_out = []
            for f in fs:
                if args.redact_matches:
                    fout = {
                        "severity": f["severity"],
                        "rule": f["rule"],
                        "category": f["category"],
                        "line": f["line"],
                        "match": "<redacted:%d chars>" % len(f["match"]),
                        "context": "<redacted>",
                    }
                else:
                    fout = f
                findings_out.append(fout)
            files_out.append({"file": rel, "findings": findings_out})
        out = {
            "staging": os.path.abspath(args.staging),
            "files_scanned": files_scanned,
            "total_block": total_block,
            "total_warn": total_warn,
            "files": files_out,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("=" * 72)
        print("ANTI-LEAK LINTER  --  enterprise-open")
        if args.public:
            print("MODE    : --public (allowlist-inversion; fail-closed)")
        if args.maintainer:
            print("MODE    : --maintainer (full deny-list; shipped tool expected)")
        if args.redact_matches:
            print("OUTPUT  : --redact-matches (match values suppressed)")
        print("staging : %s" % os.path.abspath(args.staging))
        print("denylist: %s" % os.path.abspath(args.denylist))
        print("=" * 72)
        if not per_file:
            print("\n  No findings. %d files scanned. CLEAN.\n" % files_scanned)
        else:
            for rel, fs in per_file:
                print("\n### %s" % rel)
                for f in fs:
                    loc = ("L%d" % f["line"]) if f["line"] else "name"
                    if args.redact_matches:
                        match_str = "<redacted:%d chars>" % len(f["match"])
                        print("  [%-5s] %-30s %-6s  match=%s"
                              % (f["severity"], f["rule"], loc, match_str))
                        # context omitted: may contain the matched secret value
                    else:
                        print("  [%-5s] %-30s %-6s  match=%r"
                              % (f["severity"], f["rule"], loc, f["match"]))
                        if f["context"]:
                            print("          ctx: %s" % f["context"])
        print("\n" + "-" * 72)
        print("SUMMARY: %d files scanned | BLOCK=%d | WARN=%d"
              % (files_scanned, total_block, total_warn))
        verdict = "FAIL (>=1 BLOCK)" if total_block else "PASS (0 BLOCK)"
        print("VERDICT: %s" % verdict)
        print("-" * 72)

    return 2 if total_block else 0


if __name__ == "__main__":
    sys.exit(main())
