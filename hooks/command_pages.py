"""The command reference: one page per RobotClient command, generated at build time (2026-10-23).

Every page follows the layout decided for the Programming Guide (the user's choice of "option A"):

    title, then a facts strip         queued or at once, mode, state, homed, control        robot rules
    description                       the docstring's summary and text, names linked        docstring
    Syntax                            the call, with real defaults                          signature
    Arguments                         a table: name, type, default, description;            signature + docstring
                                      **options lists every per-move setting with its
                                      default, each linking to the Per-move settings page   settings file + robot
    (a figure)                        docs/includes/command_extras/<command>.md, if any     written in the docs
    Default values                    the docstring's Defaults: section, if any             docstring
    Returns                           the type and what it means                            signature + docstring
    Examples                          the docstring's examples, without the >>> prompts     docstring
    Further details                   the docstring's Note: / Warning:                      docstring
    Usage restrictions (collapsed)    when the robot accepts it; every code it can be       robot rules + error
                                      refused or fail with, linked to the error codes;      catalog + docstring
                                      one line on the Python exceptions                     Errors: and Raises:
    Protocol                          the JSON line a raw client sends                      generated
    See also                          related commands                                      docstring

Sources: api_src/ (the client's source, the robot's command rules in communication/protocol.py, the error catalog and
runtime_facts.json, all copied from the runtime's release tag by tools/sync_runtime.py) and
docs/includes/per_move_settings.yml. Nothing on a command page is typed by hand except figures and longer
explanations in command_extras. The docstrings follow the runtime's docstrings_guide.md.

Also fills three placeholders: `<!-- command-overview: GROUP -->` (a group's table of commands),
`<!-- command-aliases: GROUP -->` (its commands' other names, from the protocol) and
`<!-- per-move-settings -->` (every per-move setting). Registered in mkdocs.yml under hooks.
"""
from __future__ import annotations

import ast
import json
import posixpath
import re
from pathlib import Path

import yaml
from griffe import AliasResolutionError, GriffeLoader, ParameterKind

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api_src"
SETTINGS_YML = ROOT / "docs" / "includes" / "per_move_settings.yml"
EXTRAS = ROOT / "docs" / "includes" / "command_extras"

# The groups' commands, in the order of the reference (each group's overview table).
GROUPS_MOTION = ["move_joints", "move_pose", "move_linear", "move_linear_rel_world", "move_linear_rel_tool",
                 "move_arc", "move_arc_rel_world", "move_arc_rel_tool", "move_circle", "move_circle_rel_world",
                 "move_circle_rel_tool", "move_spline", "move_spline_rel_world", "move_spline_rel_tool", "delay"]
GROUPS_ROBOT_CONTROL = ["enable", "disable", "home", "clear_errors", "enter_idle_mode", "enter_exec_mode",
                        "enter_jog_mode", "stop", "pause", "resume", "safety_stop", "release_safety_stop",
                        "enter_flashing_mode", "exit_flashing_mode", "take_control", "release_control",
                        "control_holder", "holds_control", "set_force_confirm"]
GROUPS_WAITING = ["wait_idle", "wait_motion_complete", "wait_mode", "wait_homed", "wait_enabled", "wait_error_reset",
                  "wait"]
GROUPS_MOTION_SETTINGS = ["set_joint_speed", "set_profile", "set_blending", "set_ik_solver", "set_completion_policy"]
GROUPS_JOGGING = ["jog", "jog_stop", "set_jog_accel", "set_jog_profile", "set_jog_jerk_factor", "set_jog_control_mode"]
GROUPS_GRIPPER = ["open_gripper", "close_gripper", "move_gripper", "wait_gripper_move_complete", "wait_holding_part",
                  "wait_released_part", "gripper_result", "calibrate_gripper", "set_gripper_ctrl_mode", "set_gripper"]
GROUPS_IO = ["set_digital_output", "get_digital_input"]
GROUPS_STATUS = ["get_joints", "get_pose", "latest_status", "get_status", "errors", "is_reachable", "get_health",
                 "get_hardware", "get_versions"]
GROUPS_SAFETY = ["set_gravity_comp", "set_inertia_comp", "set_coriolis_comp", "set_friction_ff", "set_friction_comp",
                 "set_payload", "set_collision_detection", "get_zones", "reload_zones", "get_joint_walls",
                 "set_joint_wall", "save_joint_walls"]
GROUPS_RTI = ["rti_connect", "rti_claim", "rti_release", "rti_disconnect", "rti_set_start_pose_check",
              "rti_set_rate_limiter", "rti_set_tcp_vel_limit", "rti_set_vel_scale", "rti_set_command_timeout",
              "rti_set_gravity_comp", "rti_set_dynamics_ff", "rti_set_servo_generator", "rti_set_min_duration",
              "rti_set_pace", "rti_set_lowpass", "rti_set_state_rate"]
GROUPS_CONNECTION = ["connect", "disconnect", "connected", "on_error", "on_status_change", "on_motion_complete",
                     "on_motion_error", "remote_ip", "local_ip", "local_label"]
GROUPS_DIAGNOSTICS = ["joint_test", "free_joint", "hall_check", "set_pid_gains", "set_can_read_first",
                      "set_log_level", "capture_telemetry", "stop_capture", "set_recipe", "reload_recipes",
                      "reload_filters"]
GROUPS = {
    "motion": GROUPS_MOTION,
    "robot_control": GROUPS_ROBOT_CONTROL,
    "waiting": GROUPS_WAITING,
    "motion_settings": GROUPS_MOTION_SETTINGS,
    "jogging": GROUPS_JOGGING,
    "gripper": GROUPS_GRIPPER,
    "io": GROUPS_IO,
    "status": GROUPS_STATUS,
    "safety": GROUPS_SAFETY,
    "rti": GROUPS_RTI,
    "connection": GROUPS_CONNECTION,
    "diagnostics": GROUPS_DIAGNOSTICS,
}
# Each group's folder: its overview is index.md there, each command a page of its own.
GROUP_DIRS = {"motion": "programming/commands/motion", "robot_control": "programming/commands/robot-control",
              "waiting": "programming/commands/waiting", "motion_settings": "programming/commands/motion-settings",
              "jogging": "programming/commands/jogging", "gripper": "programming/commands/gripper",
              "io": "programming/commands/io", "status": "programming/commands/status",
              "safety": "programming/commands/safety-and-dynamics", "rti": "programming/commands/real-time-interface",
              "connection": "programming/commands/connection", "diagnostics": "programming/commands/diagnostics"}
# Classes with a page of their own (2026-10-24): the class, its group, the module it is in, the name an example gives
# an instance, and the module's other public classes documented on the same page (results, commands, exceptions).
CLASS_PAGES = {
    "RTIClient": {"group": "rti", "module": "rti_client", "var": "rti",
                  "extras": ["RobotState", "JointPositionCommand", "JointVelocityCommand", "JointTorqueCommand",
                             "ControlLost", "MotionFinished"]},
    "GripperResult": {"group": "gripper", "module": "client", "var": "result", "extras": []},
}
# The pages: command -> its page, for every command of every group, and every class page.
PAGES = {name: f"{GROUP_DIRS[group]}/{name}.md" for group, names in GROUPS.items() for name in names}
PAGES.update({name: f"{GROUP_DIRS[c['group']]}/{name}.md" for name, c in CLASS_PAGES.items()})
SETTINGS_PAGE = "programming/commands/per-move-settings.md"
REFERENCE_PHRASES = {"Status fields reference": "programming/references/status-fields.md"}
ERRORS_PAGE = "programming/references/error-codes.md"

# What every queued command shares and its docstring leaves out (docstrings_guide.md, "Errors:"): the refusals when it
# is sent come from runtime_facts.json (the executor's own replies); these two can end any planning, these three any
# running move (the executor's and the motion handler's replies for a cancelled, stopped or unsettled move).
QUEUED_FAILS = ["PLAN_FAIL", "SEND_TIMEOUT"]
QUEUED_ENDINGS = ["ABORTED", "STOPPED", "SETTLE_TIMEOUT"]
ENDING_NOTES = {"ABORTED": "an earlier move failed, or the robot left EXEC mode",
                "STOPPED": "`stop()` was called",
                "SETTLE_TIMEOUT": "only with `set_completion_policy(\"strict\")`"}
REFUSAL_NOTES = {"REJECTED": "the message names the mode or state it needs",
                 "CONTROL_HELD": "another client holds control; the message names it",
                 "MOTION_ABORTED": "an earlier move failed; clear errors first",
                 "BAD_OPTIONS": "a setting is unknown, out of range, or refused for a single move",
                 "CLIENT_TOO_OLD": "only a raw client that sends no `\"protocol\": 2`"}
STANDARD_RAISES = {"CommandRejected", "MotionFailed", "RobotTimeout", "RobotConnectionError"}
LOST_CONNECTION = ("If the connection drops while the call waits for the robot's answer, it raises `CommandRejected` "
                   "with the code `CONNECTION_LOST` (`DISCONNECTED` after `disconnect()`); while it waits for the "
                   "robot's status, `RobotConnectionError`.")
# The executor's one guard around every immediate handler (command_executor.handle_immediate, 2026-10-24): not a code
# of any one handler, so said once here.
UNREADABLE = ("Like every immediate command, it also answers `BAD_ARGS` when a raw client sends a value the robot "
              "cannot read at all, and `INTERNAL` when it fails inside the robot.")


class Data:
    """Everything the pages are built from, loaded once per build."""

    def __init__(self) -> None:
        self.ok = (API / "robotclient" / "__init__.py").exists()
        if not self.ok:
            return
        loader = GriffeLoader(search_paths=[str(API)], docstring_parser="google")
        self.package = loader.load("robotclient")
        self.client = self.package["client.RobotClient"]
        self.rules = _exec_module(API / "communication" / "protocol.py")
        self.catalog = _exec_module(API / "utility" / "error_catalog.py")["CATALOG"]
        self.facts = json.loads((API / "runtime_facts.json").read_text(encoding="utf-8"))
        if "immediate_codes" not in self.facts:
            # Without them every immediate command's page would say "never refused": stop instead of publishing that.
            raise RuntimeError("api_src/runtime_facts.json has no immediate_codes: run tools/sync_runtime.py again")
        self.settings = yaml.safe_load(SETTINGS_YML.read_text(encoding="utf-8"))
        consts = ast.parse((API / "robotclient" / "constants.py").read_text(encoding="utf-8"))
        self.port = next(ast.literal_eval(n.value) for n in consts.body if isinstance(n, ast.Assign)
                         and any(getattr(t, "id", "") == "DEFAULT_PORT" for t in n.targets))

    def method(self, name):
        return self.client.members[name]

    def cls(self, name):
        """A class with a page of its own (CLASS_PAGES), from its module."""
        return self.package[f"{CLASS_PAGES[name]['module']}.{name}"]

    def ordered_settings(self) -> list[str]:
        """The robot's per-move settings, in the settings file's order (a setting it lacks comes last: the build check
        fails on it anyway)."""
        robot = set(self.facts["settings"])
        return [s for s in self.settings if s in robot] + sorted(robot - set(self.settings))


def _exec_module(path: Path) -> dict:
    ns: dict = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)    # noqa: S102 — the runtime's own data
    return ns


def command_of(method: str, ns: dict) -> str | None:
    """The protocol command a client method sends, or None. A method's name is its command (the runtime's
    test_command_aliases checks it); an old name goes through the protocol's own COMMAND_ALIASES."""
    command = ns.get("COMMAND_ALIASES", {}).get(method, method)
    return command if command in ns["COMMAND_RULES"] else None


def rel(here: str, target: str) -> str:
    """A link from page `here` to page `target`, both relative to docs/."""
    return posixpath.relpath(target, posixpath.dirname(here))


def cell(text: str) -> str:
    """Markdown text for a table cell: one line, no column breaks."""
    return " ".join(str(text).split()).replace("|", r"\|")


def is_list(para: str) -> bool:
    return any(ln.strip().startswith(("- ", "* ")) or re.match(r"\d+\. ", ln.strip()) for ln in para.splitlines())


def paragraphs(text: str) -> list[str]:
    """A docstring's text as Markdown paragraphs: prose joined into one line, a list kept item by item (2026-10-24:
    joining every line flattened a field list into one run-on line)."""
    out = []
    for para in [p for p in text.split("\n\n") if p.strip()]:
        if is_list(para):
            items: list[str] = []
            for ln in para.splitlines():
                s = ln.strip()
                if s.startswith(("- ", "* ")) or re.match(r"\d+\. ", s) or not items:
                    items.append(s)
                else:
                    items[-1] += " " + s
            out.append("\n".join(items))
        else:
            out.append(" ".join(para.split()))
    return out


def linkify(text: str, here: str, current: str, own: dict | None = None) -> str:
    """`name()` of a command that has a page becomes a link to it."""
    def sub(m):
        name = m.group(1)
        if own and name in own:                 # a class page's own method: its section on the same page
            return f"[`{name}()`](#{own[name]})"
        if name in PAGES and name != current:
            return f"[`{name}()`]({rel(here, PAGES[name])})"
        return m.group(0)

    def sub_class(m):                   # `RTIClient`, `GripperResult`: their class pages (2026-10-24)
        name = m.group(1)
        if name in CLASS_PAGES and name != current:
            return f"[`{name}`]({rel(here, PAGES[name])})"
        return m.group(0)
    text = re.sub(r"`([A-Z]\w+)`", sub_class, re.sub(r"`(\w+)\(\)`", sub, text))
    # Reference pages a docstring names in words (2026-10-24): the phrase becomes a link, also across a line break.
    for phrase, target in REFERENCE_PHRASES.items():
        text = re.sub(r"\s+".join(phrase.split()), lambda m: f"[{m.group(0)}]({rel(here, target)})", text)
    return text


def default_text(param, func) -> str:
    """A parameter's default as the reader should see it: a named constant as its value."""
    if param.default is None:
        return ""
    name = str(param.default)
    member = func.module.members.get(name) if name.isidentifier() and name.isupper() else None
    if member is not None:
        try:
            value = getattr(member.final_target if member.is_alias else member, "value", None)
        except AliasResolutionError:
            value = None
        if value is not None:
            return str(value)
    return name


def sections(func) -> dict:
    """The docstring's parts: text, params, returns, raises, examples, and the admonitions by kind."""
    out = {"text": "", "params": {}, "returns": "", "raises": [], "examples": [], "adm": {}}
    if func.docstring is None:          # a method not documented yet: an empty page, never a failed build
        return out
    for s in func.docstring.parse("google", returns_multiple_items=False, warnings=False):
        kind = s.kind.value
        if kind == "text" and not out["text"]:
            out["text"] = s.value
        elif kind == "parameters":
            out["params"] = {p.name.lstrip("*"): p.description for p in s.value}
        elif kind == "returns":
            out["returns"] = s.value[0].description if s.value else ""
        elif kind == "raises":
            out["raises"] = [(str(r.annotation), r.description) for r in s.value]
        elif kind == "examples":
            out["examples"] = [t for k, t in s.value if k.value == "examples"]
        elif kind == "admonition":
            out["adm"][s.value.annotation] = s.value.description
        elif kind == "attributes":                  # a data class's fields (class pages, 2026-10-24)
            out["attributes"] = [(a.name, str(a.annotation or ""), " ".join(a.description.split())) for a in s.value]
    return out


def code_lines(examples: list[str]) -> list[str]:
    """The examples as a script: the >>> and ... prompts removed, output lines dropped."""
    lines = []
    for block in examples:
        for ln in block.splitlines():
            if ln.startswith(">>> ") or ln.startswith("... "):
                lines.append(ln[4:])
            elif ln in (">>>", "..."):
                lines.append("")
    return lines


# What get_pose() returns when an example reads it: the TCP pose at the standard start pose (90, -105, 165, 0, -30,
# 180) deg with the MSG gripper, in metres and radians, rounded to 4 decimals (the runtime's DryRunRobotClient,
# 2026-10-23). Only an illustration for the Protocol line; the page says so.
REFERENCE_POSE = [0.0, 0.2617, 0.2329, -2.0944, 0.0, -1.5708]


def _real_client():
    """The RobotClient class of api_src, imported fresh (a build after a re-sync must not reuse the last one)."""
    import importlib
    import sys
    for mod in [m for m in sys.modules if m == "robotclient" or m.startswith("robotclient.")]:
        del sys.modules[mod]
    sys.path.insert(0, str(API))
    try:
        return importlib.import_module("robotclient.client").RobotClient
    finally:
        sys.path.remove(str(API))


def wire_message(name: str, lines: list[str], rules: dict) -> tuple[str | None, bool]:
    """The JSON a raw client sends for the page's example, and whether the example read get_pose().

    The example runs against the REAL client (api_src) with a transport that keeps the message instead of sending
    it, so the line is exactly what robotclient sends: its packing of lists, its defaults, its unit conversion
    (2026-10-23: reading the call as text got 6 of 8 lines wrong). get_pose() answers REFERENCE_POSE."""
    client_cls = _real_client()
    robot = client_cls.__new__(client_cls)
    sent, read_pose = [], []

    def queued(cmd, args=None, timeout=None, options=None):
        sent.append((cmd, list(args or []), dict(options or {})))
        return "c1"

    def immediate(cmd, args=None, timeout=None):
        if cmd == "get_pose":
            read_pose.append(True)
            return list(REFERENCE_POSE)
        sent.append((cmd, list(args or []), {}))
        return None

    robot._queued = robot._queued_gripper = queued
    robot._immediate = immediate
    robot.wait_idle = lambda *a, **k: []
    # Immediate commands: the message is all the line shows, so no call waits for the robot's status afterwards.
    robot._should_wait = lambda wait=None: False
    robot.wait = robot.wait_mode = robot.wait_enabled = lambda *a, **k: None
    robot._conn = type("NoConnection", (), {"take_motion_errors": staticmethod(lambda: []), "wire_names": {}})()
    try:
        exec("\n".join(lines), {"robot": robot})     # noqa: S102 - our own docstring examples
    except Exception:                                 # noqa: BLE001 - a line the stand-in cannot run: what was sent
        pass                                          # before it still counts (an example reading a reply, say)
    command = command_of(name, rules) or name
    found = next(((c, a, o) for c, a, o in sent if c == command), None)
    if found is None:
        return None, False
    msg = {"id": "c1", "cmd": found[0], "args": found[1]}
    if found[2]:
        msg["options"] = found[2]
    if msg["cmd"] in rules.get("POSE_COMMANDS", ()):
        msg["protocol"] = rules.get("PROTOCOL_VERSION", 1)
    return json.dumps(msg), bool(read_pose)


def code_item(code: str, data: Data, here: str, note: str = "") -> str:
    entry = data.catalog[code]
    link = f"{rel(here, ERRORS_PAGE)}#{entry['number']}-{code.lower()}"
    return f"- [**[{entry['number']}]**]({link}) {entry['title']}" + (f" — {note}" if note else "")


def errors_section(text: str) -> list[tuple[str, str]]:
    """The docstring's Errors: lines as (code, when)."""
    items: list[list[str]] = []
    for ln in text.splitlines():
        m = re.match(r"([A-Z][A-Z0-9_]+):\s*(.*)", ln)
        if m:
            items.append([m.group(1), m.group(2)])
        elif items and ln.strip():
            items[-1][1] += " " + ln.strip()
    return [(c, w) for c, w in items]


def conditions(modes, state, homed) -> str:
    """'in IDLE or EXEC mode, enabled and homed': what a command's rule asks for, in words ('' for nothing)."""
    conds = ([f"in {' or '.join(modes)} mode"] if modes else []) + ([str(state).lower()] if state else []) \
        + (["homed"] if homed else [])
    return "" if not conds else conds[0] if len(conds) == 1 else ", ".join(conds[:-1]) + " and " + conds[-1]


def restrictions_box(count: str, body: list[str]) -> list[str]:
    """Collapsed: a <details> box (the theme styles it like its own collapsible notes), the count in the title."""
    return ['<details class="restrictions" markdown>',
            f'<summary>Usage restrictions <span class="count">{count}</span></summary>', "", *body, "", "</details>", ""]


def queued_restrictions(name, command, doc, data, here, modes, state, homed) -> list[str]:
    """A queued command's box: the refusals when it is sent, its own failures, the shared failures and endings."""
    refusals = [c for c in data.facts["queued_refusals"] if c != "UNKNOWN_CMD"
                and (c != "CLIENT_TOO_OLD" or command in data.rules.get("POSE_COMMANDS", ()))]
    own = errors_section(doc["adm"].get("errors", ""))
    fails = own + [(c, "") for c in QUEUED_FAILS]
    n = len(refusals) + len(fails) + len(QUEUED_ENDINGS)
    body = ["This command is added to the robot's motion queue. The robot accepts it only when it is ready "
            f"for motion ({conditions(modes, state, homed).removeprefix('in ')}), from the client that holds control "
            "or when no client does. Otherwise, the robot refuses it with one of:"]
    body += [""] + [code_item(c, data, here, REFUSAL_NOTES.get(c, "")) for c in refusals] + [""]
    body += ["Once accepted, the move can still fail before it starts:", ""]
    body += [code_item(c, data, here, linkify(w[0].lower() + w[1:] if w else "", here, name).rstrip("."))
             for c, w in fails] + [""]
    body += ["A move that has started can end early with:", ""]
    body += [code_item(c, data, here, ENDING_NOTES.get(c, "")) for c in QUEUED_ENDINGS] + [""]
    extra_raises = [(e, d) for e, d in doc["raises"] if e not in STANDARD_RAISES]
    body.append("In Python, a refusal raises `CommandRejected`; its `number` is the code above. A failure after the "
                "robot accepted the move is raised by `wait_idle()` as `MotionFailed`, or by this call itself in sync "
                "mode as `CommandRejected`. No answer raises `RobotTimeout`; no connection, `RobotConnectionError`."
                + "".join(f" `{e}`: {' '.join(d.split())}" for e, d in extra_raises))
    return restrictions_box(f"{n} codes", body)


def immediate_codes(command, doc, data, modes, state, homed, owned) -> tuple[list[str], dict]:
    """An immediate command's codes, in the order the robot checks them, and the docstring's words for each:
    the executor's dispatch refusals that its rule allows (CLIENT_TOO_OLD, REJECTED, CONTROL_HELD — read from the
    executor, in its order), then every code its own handler answers with (runtime_facts.json), then any other code
    its docstring's Errors: names."""
    applies = {"CLIENT_TOO_OLD": command in data.rules.get("POSE_COMMANDS", ()),
               "REJECTED": bool(modes or state or homed), "CONTROL_HELD": bool(owned)}
    codes = [c for c in data.facts["queued_refusals"] if applies.get(c)]
    codes += data.facts.get("immediate_codes", {}).get(command, [])
    own = errors_section(doc["adm"].get("errors", ""))
    codes += [c for c, _ in own]
    return list(dict.fromkeys(codes)), dict(own)


def immediate_restrictions(name, command, doc, data, here, modes, state, homed, owned) -> list[str]:
    """An immediate command's box: when the robot accepts it, every code it can answer with, what the call raises."""
    codes, notes = immediate_codes(command, doc, data, modes, state, homed, owned)
    when = conditions(modes, state, homed)
    who = "from the client that holds control or when no client does" if owned else "from every client"
    body = ["This command runs at once; it is not queued. The robot accepts it "
            + (f"only when it is {when}, {who}." if when else f"in any mode and state, {who}.")]
    if codes:
        body += ["", "It answers with one of these codes when it does not carry the command out:", ""]
        body += [code_item(c, data, here, linkify(notes[c][0].lower() + notes[c][1:], here, name).rstrip(".")
                           if notes.get(c) else REFUSAL_NOTES.get(c, "")) for c in codes] + [""]
    else:
        body += ["", "It never answers with an error code.", ""]
    lead = "In Python, a code above raises `CommandRejected`; its `number` is the code." if codes else "In Python,"
    if doc["raises"]:
        body += [f"{lead} {'The call raises' if codes else 'the call raises'}:", ""]
        body += [f"- `{e}`: {linkify(' '.join(d.split()), here, name)}" for e, d in doc["raises"]] + [""]
    else:
        body += [f"{lead} {'No' if codes else 'no'} answer raises `RobotTimeout`; no connection, "
                 "`RobotConnectionError`.", ""]
    # The client's own behaviour on a lost connection (robotclient/connection.py: _fail_all, wait_status), the same
    # for every immediate command, so said here once rather than in every docstring.
    body.append(LOST_CONNECTION)
    body += ["", UNREADABLE]
    count = f"{len(codes)} code{'s' if len(codes) != 1 else ''}" if codes else "never refused"
    return restrictions_box(count, body)


def page(name: str, data: Data) -> str:
    """The Markdown of one command's page."""
    here = PAGES[name]
    func = data.method(name)
    doc = sections(func)
    command = command_of(name, data.rules)
    is_prop = func.has_labels("property")         # Griffe: a property is an Attribute (no parameters, no returns)
    out = [f"# {name} {{ .cmd-title }}", ""]
    if command is None:                 # a client-side method: it reads what the client already has, sends nothing
        queued = immediate = False
        modes = state = homed = owned = None
        facts = ["Runs in the client", "Sends nothing to the robot"]
    else:
        kind, modes, state, homed = data.rules["COMMAND_RULES"][command]
        queued = kind == data.rules["QUEUED"]
        immediate = not queued
        owned = data.rules["is_owned"](command)
        facts = ["Queued" if queued else "Runs at once", f"{' or '.join(modes)} mode" if modes else "Any mode"]
        facts += ([str(state).capitalize()] if state else []) + (["Homed"] if homed else [])
        facts.append("Takes control" if owned else "Open to every client")
    out += ['<div class="cmd-facts" markdown>', " ".join(
        f'<span class="fact{" q" if i == 0 else ""}">{f}</span>' for i, f in enumerate(facts)), "</div>", ""]
    # The summary and the first paragraph read as one opening paragraph, as in the decided layout.
    paras = paragraphs(doc["text"])
    if len(paras) > 1 and not is_list(paras[1]):
        paras = [paras[0] + " " + paras[1]] + paras[2:]
    out += [p for para in paras for p in (linkify(para, here, name), "")]

    params = [] if is_prop else [p for p in func.parameters if p.name not in ("self", "cls")]
    call = []
    for p in params:
        star = "*" if p.kind is ParameterKind.var_positional else "**" if p.kind is ParameterKind.var_keyword else ""
        d = default_text(p, func) if not star else ""
        call.append(f"{star}{p.name}" + (f"={d}" if d else ""))
    kw_only = [i for i, p in enumerate(params) if p.kind is ParameterKind.keyword_only]
    if kw_only and not any(p.kind is ParameterKind.var_positional for p in params):
        call.insert(kw_only[0], "*")
    out += ["## Syntax", "", "```python", f"robot.{name}" if is_prop else f"robot.{name}({', '.join(call)})", "```",
            ""]

    if not is_prop:                     # a property is read, not called: no arguments
        out += ["## Arguments", ""]
        out += ["| Name | Type | Default | Description |", "|---|---|---|---|"] if params else ["None.", ""]
    settings_link = rel(here, SETTINGS_PAGE)
    for p in params:
        star = "*" if p.kind is ParameterKind.var_positional else "**" if p.kind is ParameterKind.var_keyword else ""
        desc = linkify(doc["params"].get(p.name, ""), here, name)
        if star == "**" and p.name == "options":
            _, _, rest = " ".join(desc.split()).partition("takes its default.")
            chips = " ".join(f'[`{s}` <span class="od">= {data.settings[s]["default"].strip("`")}</span>]'
                             f"({settings_link}#{s}){{ .opt }}" for s in data.ordered_settings())
            desc = (f"Settings for this move only. Each one you leave out takes its default: "
                    f'<span class="optlinks">{chips}</span>{rest.replace("See Per-move settings.", "")}')
            default = "*each setting's own*"
        elif star == "*" or p.default is None:
            default = "*required*"
        else:
            default = f"`{default_text(p, func)}`"
        out.append(f"| `{star}{p.name}` | {type_cell(p.annotation)} | {default} | {cell(desc)} |")
    if params:
        out.append("")
    extra = EXTRAS / f"{name}.md"
    if extra.exists():
        out += [extra.read_text(encoding="utf-8").strip(), ""]

    if "defaults" in doc["adm"]:
        out += ["## Default values", "", linkify(doc["adm"]["defaults"], here, name), ""]
    if is_prop:                         # its summary says what the value is
        out += ["## Value", "", f"`{func.annotation}`", ""]
    else:
        out += ["## Returns", ""]
    if is_prop:
        pass
    elif doc["returns"]:
        out += [f"`{func.returns}`", "", linkify(" ".join(doc["returns"].split()), here, name), ""]
    elif str(func.returns) in ("None", ""):
        out += ["Nothing.", ""]
    else:                               # a value the docstring does not describe yet: at least its type
        out += [f"`{func.returns}`", ""]
    lines = code_lines(doc["examples"])
    if lines:
        out += ["## Examples", "", "```python", *lines, "```", ""]
    for adm, title, typ in (("note", "Note", "note"), ("warning", "Warning", "warning")):
        if adm in doc["adm"]:
            out += ["## Further details", "", f'!!! {typ} "{title}"', "",
                    *[f"    {ln}" for ln in linkify(doc["adm"][adm], here, name).splitlines()], ""]

    if queued:
        out += queued_restrictions(name, command, doc, data, here, modes, state, homed)
    elif immediate:
        out += immediate_restrictions(name, command, doc, data, here, modes, state, homed, owned)
    elif doc["raises"]:                 # a client-side method: no robot rules, only what it raises
        out += ["## Exceptions", ""] + [f"- `{e}`: {linkify(' '.join(d.split()), here, name)}"
                                        for e, d in doc["raises"]] + [""]

    msg, read_pose = wire_message(name, lines, data.rules) if command is not None else (None, False)
    if msg:
        where = (f", with the tool at the standard start pose (`get_pose()` returning "
                 f"`{REFERENCE_POSE}`)" if read_pose else "")
        out += ["## Protocol", "", f"A client that does not use `robotclient` sends this over the TCP command protocol "
                f"(port {data.port}) for the example above{where}:", "", "```json", msg, "```", ""]

    mentioned = re.findall(r"`(\w+)\(\)`", " ".join([doc["text"], doc["returns"], *doc["params"].values()]))
    also = re.findall(r"`(\w+)\(\)`", doc["adm"].get("see-also", ""))
    see = [s for s in dict.fromkeys(mentioned + also) if s != name and s in data.client.members]
    links = [f"[`{s}`]({rel(here, PAGES[s])})" if s in PAGES else f"`{s}`" for s in see]
    if any(p.kind is ParameterKind.var_keyword for p in params):
        links.append(f"[Per-move settings]({settings_link})")
    if links:
        out += ["## See also", "", '<div class="seealso" markdown>', "", " ".join(links), "", "</div>", ""]
    return "\n".join(out)


def type_cell(annotation) -> str:
    """A table's type cell: the annotation in code font, blank when the code gives none."""
    return f"`{annotation}`" if annotation not in (None, "", "None") else ""


def params_table(params, func, doc, here, name, own=None) -> list[str]:
    """An Arguments table for a class page's method (no per-move settings there)."""
    if not params:
        return ["None.", ""]
    out = ["| Name | Type | Default | Description |", "|---|---|---|---|"]
    for p in params:
        star = "*" if p.kind is ParameterKind.var_positional else "**" if p.kind is ParameterKind.var_keyword else ""
        default = "*required*" if star == "*" or p.default is None else f"`{default_text(p, func)}`"
        if star == "**":
            default = "*optional*"
        out.append(f"| `{star}{p.name}` | {type_cell(p.annotation)} | {default} | "
                   f"{cell(linkify(doc['params'].get(p.name, ''), here, name, own))} |")
    return out + [""]


def call_text(params, func) -> str:
    call = []
    for p in params:
        star = "*" if p.kind is ParameterKind.var_positional else "**" if p.kind is ParameterKind.var_keyword else ""
        d = default_text(p, func) if not star else ""
        call.append(f"{star}{p.name}" + (f"={d}" if d else ""))
    kw_only = [i for i, p in enumerate(params) if p.kind is ParameterKind.keyword_only]
    if kw_only and not any(p.kind is ParameterKind.var_positional for p in params):
        call.insert(kw_only[0], "*")
    return ", ".join(call)


def member_block(obj, title: str, syntax: str, here: str, name: str, level: str = "##",
                 own: dict | None = None) -> list[str]:
    """One method (or property) of a class page: its text, syntax, arguments, returns, raises, examples, notes."""
    doc = sections(obj)
    anchor = title.replace(".", "-").lower()
    out = [f"{level} `{title}` {{ #{anchor} }}", ""]
    out += [p for para in paragraphs(doc["text"]) for p in (linkify(para, here, name, own), "")]
    out += ["```python", syntax, "```", ""]
    is_prop = obj.has_labels("property") if hasattr(obj, "has_labels") else False
    params = [] if is_prop or not hasattr(obj, "parameters") else [
        p for p in obj.parameters if p.name not in ("self", "cls")]
    if not is_prop:
        out += ["**Arguments**", ""] + params_table(params, obj, doc, here, name, own)
    if doc["returns"]:
        out += ["**Returns** " + f"`{obj.returns}`: " + linkify(" ".join(doc["returns"].split()), here, name, own), ""]
    elif is_prop:
        out += [f"**Value** `{obj.annotation}`", ""]
    if doc["raises"]:
        out += ["**Raises**", ""] + [f"- `{e}`: {linkify(' '.join(d.split()), here, name, own)}"
                                     for e, d in doc["raises"]] + [""]
    if doc.get("attributes"):
        out += ["| Field | Type | Meaning |", "|---|---|---|"]
        out += [f"| `{a}` | {type_cell(t)} | {cell(linkify(d, here, name, own))} |" for a, t, d in doc["attributes"]] + [""]
    lines = code_lines(doc["examples"])
    if lines:
        out += ["**Example**", "", "```python", *lines, "```", ""]
    for adm, title_, typ in (("note", "Note", "note"), ("warning", "Warning", "warning")):
        if adm in doc["adm"]:
            out += [f'!!! {typ} "{title_}"', "",
                    *[f"    {ln}" for ln in linkify(doc["adm"][adm], here, name, own).splitlines()], ""]
    return out


def class_page(name: str, data: Data) -> str:
    """A class's page (2026-10-24): what it is, how to create one, every public method, the module's classes it works
    with. Its methods run in the client; what they send to the robot is on the commands' own pages."""
    here = PAGES[name]
    spec = CLASS_PAGES[name]
    klass = data.cls(name)
    doc = sections(klass)
    own = {n: (name + "." + n).replace(".", "-").lower() for n, m in klass.members.items()
           if not n.startswith("_") and not m.is_alias}
    out = [f"# {name} {{ .cmd-title }}", "", '<div class="cmd-facts" markdown>',
           '<span class="fact q">A class in the client</span> <span class="fact">from robotclient import '
           f'{name}</span>', "</div>", ""]
    out += [p for para in paragraphs(doc["text"]) for p in (linkify(para, here, name, own), "")]
    for adm, title_, typ in (("note", "Note", "note"), ("warning", "Warning", "warning")):
        if adm in doc["adm"]:
            out += [f'!!! {typ} "{title_}"', "",
                    *[f"    {ln}" for ln in linkify(doc["adm"][adm], here, name, own).splitlines()], ""]
    members = [m for n, m in klass.members.items() if not n.startswith("_") and not m.is_alias
               and (m.is_function or m.has_labels("property"))]
    init = klass.members.get("__init__")
    if init is not None and init.docstring:
        params = [p for p in init.parameters if p.name not in ("self", "cls")]
        out += ["## Create one", ""] + member_block(init, f"{name}()", f"{spec['var']} = {name}({call_text(params, init)})",
                                                   here, name, "###", own)[2:]
    if members:
        out += ["## Methods and properties", "", "| Name | What it does |", "|---|---|"]
        for m in members:
            summary = m.docstring.value.splitlines()[0] if m.docstring else ""
            label = m.name if m.has_labels("property") else f"{m.name}()"
            out.append(f"| [`{label}`](#{(name + '.' + m.name).replace('.', '-').lower()}) | {cell(summary)} |")
        out.append("")
        for m in members:
            if m.has_labels("property"):
                syntax = f"{spec['var']}.{m.name}"
            else:
                params = [p for p in m.parameters if p.name not in ("self", "cls")]
                syntax = f"{spec['var']}.{m.name}({call_text(params, m)})"
            out += member_block(m, f"{name}.{m.name}", syntax, here, name, own=own)
    for extra in spec["extras"]:
        obj = data.package[f"{spec['module']}.{extra}"]
        out += member_block(obj, extra, f"from robotclient.{spec['module']} import {extra}", here, name)[0:2]
        ed = sections(obj)
        out += [p for para in paragraphs(ed["text"]) for p in (linkify(para, here, name, own), "")]
        if ed.get("attributes"):
            out += ["| Field | Type | Meaning |", "|---|---|---|"]
            out += [f"| `{a}` | {type_cell(t)} | {cell(linkify(d, here, name, own))} |" for a, t, d in ed["attributes"]] + [""]
        lines = code_lines(ed["examples"])
        if lines:
            out += ["**Example**", "", "```python", *lines, "```", ""]
    also = re.findall(r"`(\w+)\(\)`", doc["adm"].get("see-also", ""))
    links = [f"[`{s}`]({rel(here, PAGES[s])})" if s in PAGES else f"`{s}`" for s in dict.fromkeys(also)]
    if links:
        out += ["## See also", "", '<div class="seealso" markdown>', "", " ".join(links), "", "</div>", ""]
    return "\n".join(out)


def overview(group: str, here: str, data: Data) -> str:
    rows = ["| Command | What it does | Runs |", "|---|---|---|"]
    for name, c in CLASS_PAGES.items():         # a class of the group first: what its commands work with
        if c["group"] == group:
            klass = data.cls(name)
            summary = klass.docstring.value.splitlines()[0] if klass.docstring else ""
            rows.append(f"| [`{name}`]({rel(here, PAGES[name])}) | {cell(summary)} | In the client (a class) |")
    for name in GROUPS[group]:
        func = data.method(name)
        summary = func.docstring.value.splitlines()[0] if func.docstring else ""
        command = command_of(name, data.rules)
        runs = ("In the client" if command is None
                else "Queued" if data.rules["COMMAND_RULES"][command][0] == data.rules["QUEUED"] else "At once")
        title = f"[`{name}`]({rel(here, PAGES[name])})" if name in PAGES else f"`{name}`"
        rows.append(f"| {title} | {cell(summary)} | {runs} |")
    return "\n".join(rows)


def aliases_table(group: str, here: str, data: Data) -> str:
    """The other names of a group's commands, from the protocol's own COMMAND_ALIASES."""
    rows = ["| Other name | Same as |", "|---|---|"]
    for old, new in data.rules.get("COMMAND_ALIASES", {}).items():
        if new in GROUPS[group]:
            target = f"[`{new}`]({rel(here, PAGES[new])})" if new in PAGES else f"`{new}`"
            rows.append(f"| `{old}` | {target} |")
    return "\n".join(rows) if len(rows) > 2 else "*None.*"


def settings_section(here: str, data: Data) -> str:
    out = ["| Setting | Values | Default | Default set by |", "|---|---|---|---|"]
    for s in data.ordered_settings():
        e = data.settings[s]
        by = f"`{e['default_set_by']}()`" if e.get("default_set_by") else ""
        out.append(f"| [`{s}`](#{s}) | {cell(e['values'])} | {cell(e['default'])} | {by} |")
    out.append("")
    for s in data.ordered_settings():
        e = data.settings[s]
        out += [f"### `{s}` {{ #{s} }}", "", e["about"].strip(), ""]
        facts = data.facts["values"].get(s)
        if facts:
            built = facts.get("built")
            out += ["| Value | What it does |", "|---|---|"]
            for v in facts["values"]:
                mark = "" if built is None or v in built else " (refused for now)"
                out.append(f'| `"{v}"`{mark} | {cell(e["choices"][v])} |')
            other = facts.get("also_accepted") or {}
            if other:
                out += ["", "Also accepted: " + ", ".join(f'`"{a}"` for `"{v}"`' for a, v in sorted(other.items())) + "."]
            out.append("")
    refused = data.facts.get("refused") or {}
    if refused:
        out += ["### Not a per-move setting", ""]
        out += [f"- `{k}` is refused on a single move (`BAD_OPTIONS`): {v}." for k, v in sorted(refused.items())]
        out.append("")
    return "\n".join(out)


_data: Data | None = None


def on_files(files, config):
    """Add the generated command pages."""
    global _data
    from mkdocs.structure.files import File
    _data = Data()
    if not _data.ok:
        return files
    for name, path in PAGES.items():
        content = class_page(name, _data) if name in CLASS_PAGES else page(name, _data)
        files.append(File.generated(config, path, content=content))
    return files


def on_page_markdown(markdown, page, config, files):
    if _data is None or not _data.ok:
        return markdown
    here = page.file.src_uri
    for group in GROUPS:
        tag = f"<!-- command-overview: {group} -->"
        if tag in markdown:
            markdown = markdown.replace(tag, overview(group, here, _data))
        tag = f"<!-- command-aliases: {group} -->"
        if tag in markdown:
            markdown = markdown.replace(tag, aliases_table(group, here, _data))
    if "<!-- per-move-settings -->" in markdown:
        markdown = markdown.replace("<!-- per-move-settings -->", settings_section(here, _data))
    return markdown
