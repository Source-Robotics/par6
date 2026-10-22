#!/usr/bin/env python3
"""Tests for hooks/versions.py and tools/sync_runtime.py (versioning step V6, 2026-10-22). No network, no runtime
repository: fixtures only. Run: .venv/bin/python tools/test_tools.py   (the build check runs it on every push)."""
from __future__ import annotations

import datetime
import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []


def check(name, cond, detail=""):
    print(("  PASS  " if cond else "  FAIL  ") + name + (f"   [{detail}]" if detail and not cond else ""))
    if not cond:
        fails.append(name)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hook = load_module("versions_hook", ROOT / "hooks" / "versions.py")
sync = load_module("sync_runtime", ROOT / "tools" / "sync_runtime.py")
from mkdocs.exceptions import PluginError  # noqa: E402

GOOD = """docs_version: "0.9"
runtime: {repository: x, tag: v0.9.0}
manuals:
  prog: {number: SR-4001, title: Programming Guide, revision: 2026.A, status: draft, published: null, guide: true,
         applies_to: "", covers: everything}
  arm: {number: SR-1001, title: Arm Manual, revision: 2026.B, status: published, published: 2026-11-02,
        applies_to: "arm v1.x", covers: the arm}
"""


def load_text(text):
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(text)
    try:
        return hook.load(f.name), None
    except PluginError as exc:
        return None, str(exc)
    finally:
        Path(f.name).unlink()


# ---------------------------------------------------------------- the hook
data, err = load_text(GOOD)
check("A1 a valid versions.yml loads", data is not None, err)
for label, bad, word in (
        ("docs_version not MAJOR.MINOR", GOOD.replace('"0.9"', '"0.9.1"'), "docs_version"),
        ("a tag of another version", GOOD.replace("v0.9.0", "v1.0.0"), "does not belong"),
        ("a malformed tag", GOOD.replace("v0.9.0", "0.9.0"), "runtime.tag"),
        ("a revision not YEAR.LETTER", GOOD.replace("2026.A", "A"), "YEAR.LETTER"),
        ("an unknown status", GOOD.replace("status: draft", "status: final"), "status"),
        ("published without a date", GOOD.replace("published: 2026-11-02", "published: null"), "publication date"),
        ("a missing field", GOOD.replace("covers: everything", "covers: ''"), "lacks covers")):
    d, e = load_text(bad)
    check(f"A2 refused: {label}", d is None and word in (e or ""), e)
meta = hook.meta_block("prog", data)
check("A3 a guide's box: number, runtime version, revision (draft), applies to the runtime",
      "SR-4001" in meta and "**Runtime version:** 0.9" in meta and "2026.A (draft)" in meta
      and "**Applies to:** runtime 0.9" in meta, meta)
meta = hook.meta_block("arm", data)
check("A4 a published manual's box: no runtime line, the date, no (draft)",
      "Runtime version" not in meta and "2026-11-02" in meta and "(draft)" not in meta and "arm v1.x" in meta, meta)
try:
    hook.meta_block("nope", data)
    raised = False
except PluginError:
    raised = True
check("A5 an unknown manual stops the build", raised)
table = hook.documents_table(data)
check("A6 the documents table: one row per manual", table.count("| SR-") == 2 and "0.9" in table, table)
hook._facts = data
page = hook.on_page_markdown("x\n<!-- doc-meta: prog -->\ny\n<!-- documents-table -->\n", None, None, None)
check("A7 both placeholders are replaced", "doc-meta:" not in page and "documents-table" not in page and "SR-1001" in page)
check("A8 the shipped versions.yml loads", hook.load(ROOT / "versions.yml")["docs_version"])
check("A9 every placeholder in the docs names a manual of versions.yml",
      all(k in hook.load(ROOT / "versions.yml")["manuals"]
          for p in (ROOT / "docs").rglob("*.md") for k in hook.META_RE.findall(p.read_text(encoding="utf-8"))))

# ---------------------------------------------------------------- the sync tool
check("B1 esc: an XML name stays visible, no emphasis, no table break",
      sync.esc("<max_payload_kg> a*b c|d") == r"&lt;max_payload_kg&gt; a\*b c\|d", sync.esc("<max_payload_kg> a*b c|d"))
compat = sync.gen_compatibility("# C\n\nintro\n\n| R | X |\n|---|---|\n| 0.9.0 | 1 |\n\n## What each column means\n\n- **R:** r\n")
check("B2 compatibility: the table and the column meanings, not the title",
      compat.startswith("| R | X |") and "### What each column means" in compat and "# C" not in compat, compat)
notes = sync.gen_release_notes("# Changelog\n\nintro\n\n## [Unreleased]\n\nwip\n\n## [0.9.0] - 2026-10-22\n\nfirst\n")
check("B3 release notes: released versions only, with their date", notes.startswith("## 0.9.0 (2026-10-22)")
      and "wip" not in notes and "first" in notes, notes)
try:
    sync.gen_release_notes("## [Unreleased]\n\nwip\n")
    raised = False
except sync.SyncError:
    raised = True
check("B4 a changelog without a release is refused", raised)
cat = ('GROUPS = {1: "Safety", 9: "Events"}\n'
       'CATALOG = {"ESTOP": {"number": 1001, "title": "E-stop", "kind": "stop", "cause": "pressed <x>", '
       '"effect": "stops", "fix": "release"}, "BOOT": {"number": 9001, "title": "Boot", "kind": "event", '
       '"cause": None, "effect": None, "fix": None}}\n')
codes = sync.gen_error_codes(cat)
check("B5 error codes: by group, number + code, cause / effect / fix, events without them",
      "## 1xxx: Safety" in codes and "### 1001 `ESTOP`" in codes and "&lt;x&gt;" in codes
      and "### 9001 `BOOT`" in codes and codes.count("- Cause:") == 1, codes)
tags = sync.gen_telemetry_tags('TAGS = {"j_p": {"src": "joint", "prec": 4, "desc": "positions (rad)"}, '
                               '"g_p": {"src": "gripper", "prec": 0, "desc": "jaw"}}\n')
check("B6 telemetry tags: grouped by source, joints first", tags.index("Joints") < tags.index("Gripper")
      and "| `j_p` | positions (rad) | 4 |" in tags, tags)
# B7 (another maker's name is caught): see the current tools/test_tools.py — the list of names is not in
# this repository (history rewritten 2026-10-23).
check("B8 ... but not inside a plain word", not sync.VENDORS.search("sessionStorage.removeItem(x)"))

print()
print(f"{len(fails)} failed" if fails else "ALL PASSED")
sys.exit(1 if fails else 0)
