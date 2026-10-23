#!/usr/bin/env python3
"""Tests for hooks/versions.py and tools/sync_runtime.py (versioning step V6, 2026-10-22) and the API reference's
hooks/command_pages.py (2026-10-23). No network, no runtime repository: fixtures, and the api_src/ copy.
Run: .venv/bin/python tools/test_tools.py   (the build check runs it on every push)."""
from __future__ import annotations

import datetime
import importlib.util
import json
import re
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
# The list of other makers' names lives in the runtime's pre-push hook, never in a published file (2026-10-23): the
# test takes a name from the list itself. The CI build has no runtime checkout and never syncs: skipped there.
try:
    names = sync.other_makers(sync.find_runtime(None))
except sync.SyncError:
    names = None
if names is None:
    print("  SKIP  B7 / B8: no runtime checkout with its pre-push hook here (the CI build; the sync never runs there)")
else:
    first = re.match(r"[a-z]+", names.pat.pattern).group(0)
    check("B7 another robot maker's name is caught (a name from the hook's own list)",
          bool(names.search(f"works like a {first.upper()} arm")), first)
    check("B8 ... but not inside a plain word", not names.search("sessionStorage.removeItem(x)"))
try:
    sync.other_makers(Path("/nonexistent/runtime"))
    refused = False
except sync.SyncError:
    refused = True
check("B8b the sync refuses to run without the list (a runtime whose hook is missing)", refused)
real_api_out = sync.API_OUT
with tempfile.TemporaryDirectory() as tmp:
    sync.API_OUT = Path(tmp) / "api_src"
    want = {"robotclient/__init__.py": "x = 1\n", "robotclient/client.py": "y = 2\n", sync.API_SOURCE: "RCB v0.9.0\n"}
    sync.write_api({**want, "robotclient/old.py": "z\n"})
    written, removed = sync.write_api(want)
    write, extra = sync.api_stale(want)
    check("B9 api_src/ is brought to exactly the copy: a file the copy lacks is removed, nothing left to write",
          (written, removed) == (0, 1) and not write and not extra
          and not (sync.API_OUT / "robotclient" / "old.py").exists(), (written, removed, write, extra))
    (sync.API_OUT / "robotclient" / "client.py").write_text("y = 3\n", encoding="utf-8")
    check("B10 an edited copy reads as out of date", sync.api_stale(want)[0] == ["robotclient/client.py"])
sync.API_OUT = real_api_out
source = (ROOT / "api_src" / sync.API_SOURCE)
source_text = source.read_text(encoding="utf-8") if source.exists() else ""
check("B11 api_src/ is a release's copy, not a working-tree preview (run tools/sync_runtime.py before publishing)",
      source_text.startswith("RCB-Runtime v") and not source_text.startswith(sync.WORKTREE_MARK), source_text.strip())

# ---------------------------------------------------------------- the sync tool's runtime facts
src = ('ALLOWED = {"speed", "dry_run", "completion_policy"}\nPROFILES = {"a": "a", "aa": "a"}\n'
       'def norm(v):\n    aliases = {"c1": "c1", "quad": "c1"}\n    return aliases[v]\n')
check("B12 a literal is read at module level and inside a function", sync._literal(src, "ALLOWED") ==
      {"speed", "dry_run", "completion_policy"} and sync._literal(src, "aliases", "norm") == {"c1": "c1", "quad": "c1"})
ex = ('def dispatch(conn):\n    if 1:\n        return reply(conn, {"status": "error", "code": "REJECTED"})\n'
      '    reply(conn, {"code": "CONTROL_HELD", "x": 1})\n'
      'def _submit_queued(c):\n    reply(c, {"code": "QUEUE_FULL"})\n'
      'def other(c):\n    reply(c, {"code": "NOT_THIS"})\n')
check("B13 the executor's reply codes come from dispatch and _submit_queued only",
      sync._reply_codes(ex, ("dispatch", "_submit_queued")) == ["REJECTED", "CONTROL_HELD", "QUEUE_FULL"],
      sync._reply_codes(ex, ("dispatch", "_submit_queued")))

# ---------------------------------------------------------------- the command pages (hooks/command_pages.py)
cp = load_module("command_pages", ROOT / "hooks" / "command_pages.py")
ns_fake = {"COMMAND_RULES": {"move_linear_rel_world": 1, "delay": 1},
           "COMMAND_ALIASES": {"move_linear_rel_wrf": "move_linear_rel_world"}}
check("C1 a method maps to its protocol command; an old name through the protocol's aliases",
      cp.command_of("delay", ns_fake) == "delay" and cp.command_of("move_linear_rel_wrf", ns_fake)
      == "move_linear_rel_world" and cp.command_of("connect", ns_fake) is None)
check("C2 the examples become a script: prompts removed, output dropped",
      cp.code_lines([">>> a = 1\n... b = 2\n3\n>>> c()"]) == ["a = 1", "b = 2", "c()"])
check("C5 Errors: lines are read with their continuation lines",
      cp.errors_section("A_B: First line\n    goes on.\nCC: Second.") == [("A_B", "First line goes on."), ("CC", "Second.")])
check("C6 a link between two pages is relative", cp.rel("a/b/c.md", "a/d.md") == "../d.md")

data = cp.Data()
if data.ok:
    robot = set(data.facts["settings"])
    check("C7 the settings file describes EVERY per-move setting the robot accepts, and no other",
          set(data.settings) == robot, (sorted(robot - set(data.settings)), sorted(set(data.settings) - robot)))
    check("C8 ... each with its values, default and description",
          all(isinstance(e, dict) and e.get("values") and e.get("default") and e.get("about")
              for e in data.settings.values()))
    missing = {s: sorted(set(v["values"]) - set((data.settings.get(s) or {}).get("choices", {})))
               for s, v in data.facts["values"].items()}
    check("C9 ... and describes every value of every choice the robot knows",
          not any(missing.values()), {s: m for s, m in missing.items() if m})
    nav = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    check("C10 every generated page is in the nav, every overview command is a client method",
          all(p in nav for p in cp.PAGES.values()) and all(n in data.client.members for g in cp.GROUPS.values() for n in g))
    def msg_of(w):
        """The protocol line as a dict; {} when there is none (a missing line must FAIL a check, not crash the run)."""
        return json.loads(w) if w else {}

    wire, read = cp.wire_message("move_joints", ["robot.move_joints([4, 5, 6, 7, 8, 9], speed=0.2)"], data.rules)
    check("C3 the protocol line is what the REAL client sends: a list flattened, the settings as options",
          msg_of(wire) == {"id": "c1", "cmd": "move_joints", "args": [4, 5, 6, 7, 8, 9], "options": {"speed": 0.2}}
          and read is False, wire)
    wire, read = cp.wire_message("move_pose", ["x, y, z, rx, ry, rz = robot.get_pose()",
                                               "robot.move_pose(x, y, z + 0.05, rx, ry, rz)"], data.rules)
    want = list(cp.REFERENCE_POSE)
    want[2] += 0.05
    check("C4 ... a pose command carries the protocol number; get_pose() answers the reference pose, and the page says so",
          msg_of(wire).get("protocol") == data.rules.get("PROTOCOL_VERSION")
          and msg_of(wire).get("args") == want and read is True, wire)
    wire, _ = cp.wire_message("move_linear_rel_world", ['robot.move_linear_rel_world(0, 0, 0, drz=15, angle_unit="deg")'],
                              data.rules)
    check("C4b ... a keyword PARAMETER is an argument, not a setting, and degrees go out in radians (the old reader got "
          "this wrong)", msg_of(wire).get("args", [None])[:5] == [0, 0, 0, 0, 0]
          and len(msg_of(wire).get("args", [])) == 6 and abs(msg_of(wire)["args"][5] - 0.2617994) < 1e-6
          and "options" not in msg_of(wire), wire)
    numbers = {e["number"]: k for k, e in data.catalog.items()}
    # What the planner reads per command (motion/trajectory_planner: _pose_from_args, _build_curve_path, delay):
    LAYOUT = {"move_joints": lambda n: n == 6, "move_pose": lambda n: n == 6, "delay": lambda n: n == 1,
              "arc": lambda n: n == 12, "circle": lambda n: n in (6, 7), "spline": lambda n: n >= 12 and n % 6 == 0,
              "linear": lambda n: n == 6}
    for name in cp.PAGES:
        md = cp.page(name, data)
        codes = [int(n) for n in re.findall(r"\[\*\*\[(\d+)\]\*\*\]", md)]
        command = cp.command_of(name, data.rules)
        expected = ([c for c in data.facts["queued_refusals"] if c != "UNKNOWN_CMD"
                     and (c != "CLIENT_TOO_OLD" or command in data.rules.get("POSE_COMMANDS", ()))]
                    + [c for c, _ in cp.errors_section(cp.sections(data.method(name))["adm"]["errors"])]
                    + cp.QUEUED_FAILS + cp.QUEUED_ENDINGS)
        check(f"C11 {name}: Usage restrictions lists exactly the executor's refusals, its own Errors:, the shared "
              "failures and endings, each a catalogued code", [numbers.get(n) for n in codes] == expected,
              ([numbers.get(n) for n in codes], expected))
        check(f"C12 {name}: the facts strip, every setting linked, the examples without prompts, the protocol line",
              'class="fact q">Queued' in md and md.count("{ .opt }") == len(robot) and ">>>" not in md
              and f'"cmd": "{command}"' in md and "<details class=\"restrictions\" markdown>" in md)
        m = re.search(r"```json\n(.*?)\n```", md, re.S)
        args = json.loads(m.group(1))["args"] if m else None
        kind = next((k for k in ("arc", "circle", "spline", "linear") if f"_{k}" in f"_{name}"), name)
        check(f"C13 {name}: the protocol line's args are a flat list of numbers in the layout the planner reads",
              isinstance(args, list) and all(isinstance(v, (int, float)) for v in args) and LAYOUT[kind](len(args)),
              args)
else:
    check("C7 api_src/ exists (run tools/sync_runtime.py)", False)

print()
print(f"{len(fails)} failed" if fails else "ALL PASSED")
sys.exit(1 if fails else 0)
