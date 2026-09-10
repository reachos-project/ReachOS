#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression test: the assert-absent tripwire must BLOCK on every never-ship deny-list
basename, including inside tools/ -- which ignore_paths excludes from content scanning.
Run from the repo root:  python3 tools/test_leak_linter_tripwire.py"""

import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DECOYS = ["leak_linter_denylist.json", "leak_linter_denylist.private.json",
          "leak_linter_denylist_internal.json"]

tmp = tempfile.mkdtemp(prefix="leaklint-")
staging = os.path.join(tmp, "staging")
shutil.copytree(ROOT, staging, ignore=shutil.ignore_patterns(".git", "__pycache__"))
for name in DECOYS:  # dropped in tools/, the prefix ignore_paths excludes from scanning
    with open(os.path.join(staging, "tools", name), "w", encoding="utf-8") as fh:
        fh.write('{"block": []}\n')

out = subprocess.run([sys.executable, os.path.join(staging, "tools", "leak_linter.py"),
                      "--public", "--staging", staging, "--denylist",
                      os.path.join(staging, "tools", "leak_linter_denylist.public.json"),
                      "--redact-matches", "--format", "json"], capture_output=True, text=True)
blocked = {os.path.basename(f["file"]) for f in json.loads(out.stdout)["files"]
           for g in f["findings"] if g["rule"] == "internal-artifact-in-staging"}
shutil.rmtree(tmp)

missed = [d for d in DECOYS if d not in blocked]
print("decoys planted : %d in tools/ (excluded from content scanning)" % len(DECOYS))
print("decoys BLOCKed : %d  %s" % (len(blocked & set(DECOYS)), sorted(blocked & set(DECOYS))))
print("exit code      : %d (2 = FAIL/blocked, as required)" % out.returncode)
print("RESULT         : %s" % ("PASS" if not missed and out.returncode == 2
                               else "FAIL - missed %s" % missed))
sys.exit(0 if not missed and out.returncode == 2 else 1)
