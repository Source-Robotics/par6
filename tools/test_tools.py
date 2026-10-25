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
handlers = ('def reply(c, o):\n    pass\n'
            'def _helper(c):\n    return reply(c, {"code": "FROM_HELPER"})\n'
            'def _worker(c):\n    reply(c, {"code": "FROM_WORKER"})\n'
            'def _check_x(v):\n    return v > 0\n'
            'def _forward(prefix, checks=None):\n    def handler(a, c):\n'
            '        if checks:\n            return reply(c, {"code": "BAD_ARGS"})\n    return handler\n'
            'def _handle_take(a, c):\n    if a:\n        return reply(c, {"status": "error", "code": "OWN"})\n'
            '    threading.Thread(target=_worker).start()\n    _helper(c)\n'
            'def _handle_plain(a, c):\n    reply(c, {"status": "ok"})\n'
            'def _unused(c):\n    reply(c, {"code": "NEVER"})\n'
            'IMMEDIATE_HANDLERS = {"take": _handle_take, "plain": _handle_plain,\n'
            '                      "set_x": _forward("x", (_check_x,)), "fwd": _forward("y")}\n')
got = sync._handler_codes(handlers)
check("B14 an immediate command's codes: its handler's, a helper's it calls, a worker thread's it starts, a "
      "factory's, in source order (depth first); never another function's",
      got == {"take": ["OWN", "FROM_WORKER", "FROM_HELPER"], "plain": [],
                                                      "set_x": ["BAD_ARGS"], "fwd": ["BAD_ARGS"]}, got)
try:
    sync._handler_codes('IMMEDIATE_HANDLERS = {"odd": lambda a, c: None}\n')
    odd = False
except sync.SyncError:
    odd = True
check("B14b ... and a handler the docs cannot read stops the sync instead of reading as 'never refused'", odd)
got = sync._handler_codes(handlers + 'RTI_ANSWER_CODES = {"fwd": ("MODE_REJECTED",), "set_x": ("BAD_ARGS", "RTI_REFUSED")}\n')
check("B14c RTI's answer codes (runtime 2026-10-25: command_executor.RTI_ANSWER_CODES) follow the handler's own, "
      "without repeating one; a runtime without the table adds nothing (B14)",
      got["fwd"] == ["BAD_ARGS", "MODE_REJECTED"] and got["set_x"] == ["BAD_ARGS", "RTI_REFUSED"]
      and got["plain"] == [], got)

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
              "linear": lambda n: n == 6,
              # the gripper's queued commands (2026-10-24): position, then optional speed and current
              "open_gripper": lambda n: n == 0, "close_gripper": lambda n: n == 0,
              "move_gripper": lambda n: 1 <= n <= 3}
    def is_queued(name):
        command = cp.command_of(name, data.rules)
        return command is not None and data.rules["COMMAND_RULES"][command][0] == data.rules["QUEUED"]

    def page_codes(md):
        return [numbers.get(int(n)) for n in re.findall(r"\[\*\*\[(\d+)\]\*\*\]", md)]

    # The immediate pages, against the codes traced by hand through the executor (2026-10-23): the dispatch refusals
    # the rule allows, then the handler's own replies, in the order the robot checks them.
    # 2026-10-23 (the user's decisions): the strict argument check first (BAD_ARGS); home, the flashing commands and
    # the motors-off release carry mode rules (REJECTED).
    TRACED = {"take_control": ["BAD_ARGS", "CONFIRM_BUSY", "CONFIRM_REQUIRED", "CONTROL_HELD", "INTERNAL"],
              "set_force_confirm": ["BAD_ARGS", "CONTROL_HELD"], "enable": ["CONTROL_HELD"], "disable": [], "stop": [],
              "home": ["REJECTED", "CONTROL_HELD"], "release_safety_stop": ["REJECTED", "CONTROL_HELD"],
              "enter_flashing_mode": ["REJECTED", "CONTROL_HELD"], "exit_flashing_mode": ["REJECTED", "CONTROL_HELD"],
              "safety_stop": [], "clear_errors": [], "release_control": [],
              "enter_exec_mode": ["REJECTED", "CONTROL_HELD"], "pause": ["REJECTED"],
              "resume": ["REJECTED", "CONTROL_HELD"]}
    for name, want in TRACED.items():
        md = cp.page(name, data)
        check(f"C14 {name}: Usage restrictions lists exactly the codes traced by hand, in the robot's order",
              page_codes(md) == want and ("never refused" in md) == (not want), page_codes(md))
    for name in [n for n in cp.PAGES if not is_queued(n) and cp.command_of(n, data.rules) is not None]:
        md = cp.page(name, data)
        command = cp.command_of(name, data.rules)
        own = set(data.facts["immediate_codes"].get(command, []))
        check(f"C15 {name}: an immediate page — 'Runs at once', every code its handler answers with, each catalogued, "
              "no queue failures", 'class="fact q">Runs at once' in md and own <= set(page_codes(md))
              and None not in page_codes(md) and not set(page_codes(md)) & set(cp.QUEUED_FAILS + cp.QUEUED_ENDINGS))
    for name in [n for n in cp.PAGES if cp.command_of(n, data.rules) is None and n not in cp.CLASS_PAGES]:
        md = cp.page(name, data)
        check(f"C16 {name}: a client-side page — 'Runs in the client', no Usage restrictions, no protocol line",
              'class="fact q">Runs in the client' in md and "restrictions" not in md and "## Protocol" not in md)
    wire, _ = cp.wire_message("enter_flashing_mode", ["robot.enter_flashing_mode(force=True, wait=True)"], data.rules)
    check("C17 an immediate command's protocol line is what the real client sends, and a wait in the example is "
          "not run", msg_of(wire) == {"id": "c1", "cmd": "enter_flashing_mode", "args": [True]}, wire)
    wire, _ = cp.wire_message("stop", ["robot.stop(wait=True)"], data.rules)
    check("C17b ... also for a call that reads the connection after sending (stop)",
          msg_of(wire) == {"id": "c1", "cmd": "stop", "args": []}, wire)
    wire, _ = cp.wire_message("enter_exec_mode", ["robot.enable(wait=True)", 'robot.wait_mode("IDLE")',
                                                  "robot.home(wait=True)", "robot.enter_exec_mode(wait=True)"],
                              data.rules)
    check("C17c ... and the waits before the page's own command do not end the example early",
          msg_of(wire) == {"id": "c1", "cmd": "enter_exec_mode", "args": []}, wire)

    # 2026-10-24: properties, class pages, reference phrases
    md = cp.page("connected", data)
    check("C19 a property's page: read without parentheses, no Arguments, its value's type",
          "robot.connected\n" in md and "robot.connected(" not in md and "## Arguments" not in md
          and "## Value" in md, md[:400])
    for cname, spec in cp.CLASS_PAGES.items():
        md = cp.class_page(cname, data)
        klass = data.cls(cname)
        public = [n for n, m in klass.members.items() if not n.startswith("_") and not m.is_alias
                  and (m.is_function or m.has_labels("property"))]
        anchors = [f"{{ #{(cname + '.' + n).replace('.', '-').lower()} }}" for n in public]
        check(f"C20 {cname}: its page has a section for every public method and property, and each of its module's "
              "classes", all(a in md for a in anchors) and all(f"## `{e}`" in md for e in spec["extras"])
              and cp.PAGES[cname] in (ROOT / "mkdocs.yml").read_text(encoding="utf-8"),
              [n for n, a in zip(public, anchors) if a not in md])
    check("C22 a list in a docstring stays a list; prose is joined into one line",
          cp.paragraphs("Text one\n    goes on.\n\n- a: one\n  more\n- b: two") == ["Text one goes on.", "- a: one more\n- b: two"],
          cp.paragraphs("Text one\n    goes on.\n\n- a: one\n  more\n- b: two"))
    md = cp.class_page("RTIClient", data)
    check("C23 on a class page, the class's own methods link to their sections, never to the robot's pages",
          "[`connect()`](#rticlient-connect)" in md and "connection/connect.md" not in md)
    linked = cp.linkify("is in the Status fields\n    reference.", cp.PAGES["get_status"], "get_status")
    check("C21 a reference page named in words becomes a link, also across a line break",
          "](../../references/status-fields.md)" in linked, linked)

    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        old_api = cp.API
        cp.API = Path(tmp) / "api_src"
        shutil.copytree(old_api, cp.API)
        facts = json.loads((cp.API / "runtime_facts.json").read_text(encoding="utf-8"))
        facts.pop("immediate_codes")
        (cp.API / "runtime_facts.json").write_text(json.dumps(facts), encoding="utf-8")
        try:
            cp.Data()
            refused = False
        except RuntimeError:
            refused = True
        finally:
            cp.API = old_api
    check("C18 a copy without the handlers' codes stops the build (every immediate page would say 'never refused')",
          refused)

    for name in [n for n in cp.PAGES if is_queued(n)]:
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
