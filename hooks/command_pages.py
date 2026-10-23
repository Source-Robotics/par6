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
GROUPS = {
    "motion": GROUPS_MOTION,
}
# The pages built so far: command -> its page. A command joins when its docstring has the guide's sections,
# Errors: included (every Motion command since 2026-10-23).
PAGES = {name: f"programming/commands/motion/{name}.md" for name in GROUPS_MOTION}
SETTINGS_PAGE = "programming/commands/per-move-settings.md"
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
                 "MOTION_ABORTED": "an earlier move failed; clear errors first",
                 "BAD_OPTIONS": "a setting is unknown, out of range, or refused for a single move",
                 "CLIENT_TOO_OLD": "only a raw client that sends no `\"protocol\": 1`"}
STANDARD_RAISES = {"CommandRejected", "MotionFailed", "RobotTimeout", "RobotConnectionError"}


class Data:
    """Everything the pages are built from, loaded once per build."""

    def __init__(self) -> None:
        self.ok = (API / "robotclient" / "__init__.py").exists()
        if not self.ok:
            return
        loader = GriffeLoader(search_paths=[str(API)], docstring_parser="google")
        self.client = loader.load("robotclient")["client.RobotClient"]
        self.rules = _exec_module(API / "communication" / "protocol.py")
        self.catalog = _exec_module(API / "utility" / "error_catalog.py")["CATALOG"]
        self.facts = json.loads((API / "runtime_facts.json").read_text(encoding="utf-8"))
        self.settings = yaml.safe_load(SETTINGS_YML.read_text(encoding="utf-8"))
        consts = ast.parse((API / "robotclient" / "constants.py").read_text(encoding="utf-8"))
        self.port = next(ast.literal_eval(n.value) for n in consts.body if isinstance(n, ast.Assign)
                         and any(getattr(t, "id", "") == "DEFAULT_PORT" for t in n.targets))

    def method(self, name):
        return self.client.members[name]

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


def linkify(text: str, here: str, current: str) -> str:
    """`name()` of a command that has a page becomes a link to it."""
    def sub(m):
        name = m.group(1)
        if name in PAGES and name != current:
            return f"[`{name}()`]({rel(here, PAGES[name])})"
        return m.group(0)
    return re.sub(r"`(\w+)\(\)`", sub, text)


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
        return None

    robot._queued = robot._queued_gripper = queued
    robot._immediate = immediate
    robot.wait_idle = lambda *a, **k: []
    try:
        exec("\n".join(lines), {"robot": robot})     # noqa: S102 - our own docstring examples
    except Exception:                                 # noqa: BLE001 - an example the stand-in cannot run: no line
        return None, False
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


def page(name: str, data: Data) -> str:
    """The Markdown of one command's page."""
    here = PAGES[name]
    func = data.method(name)
    doc = sections(func)
    command = command_of(name, data.rules)
    kind, modes, state, homed = data.rules["COMMAND_RULES"][command]
    queued = kind == data.rules["QUEUED"]
    owned = data.rules["is_owned"](command)
    out = [f"# {name} {{ .cmd-title }}", ""]

    facts = ["Queued" if queued else "Runs at once", f"{' or '.join(modes)} mode" if modes else "Any mode"]
    facts += ([str(state).capitalize()] if state else []) + (["Homed"] if homed else [])
    facts.append("Takes control" if owned else "Open to every client")
    out += ['<div class="cmd-facts" markdown>', " ".join(
        f'<span class="fact{" q" if i == 0 else ""}">{f}</span>' for i, f in enumerate(facts)), "</div>", ""]
    # The summary and the first paragraph read as one opening paragraph, as in the decided layout.
    paras = [" ".join(p.split()) for p in doc["text"].split("\n\n") if p.strip()]
    if len(paras) > 1:
        paras = [paras[0] + " " + paras[1]] + paras[2:]
    out += [p for para in paras for p in (linkify(para, here, name), "")]

    params = [p for p in func.parameters if p.name not in ("self", "cls")]
    call = []
    for p in params:
        star = "*" if p.kind is ParameterKind.var_positional else "**" if p.kind is ParameterKind.var_keyword else ""
        d = default_text(p, func) if not star else ""
        call.append(f"{star}{p.name}" + (f"={d}" if d else ""))
    kw_only = [i for i, p in enumerate(params) if p.kind is ParameterKind.keyword_only]
    if kw_only and not any(p.kind is ParameterKind.var_positional for p in params):
        call.insert(kw_only[0], "*")
    out += ["## Syntax", "", "```python", f"robot.{name}({', '.join(call)})", "```", ""]

    out += ["## Arguments", "", "| Name | Type | Default | Description |", "|---|---|---|---|"]
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
        out.append(f"| `{star}{p.name}` | `{p.annotation}` | {default} | {cell(desc)} |")
    out.append("")
    extra = EXTRAS / f"{name}.md"
    if extra.exists():
        out += [extra.read_text(encoding="utf-8").strip(), ""]

    if "defaults" in doc["adm"]:
        out += ["## Default values", "", linkify(doc["adm"]["defaults"], here, name), ""]
    out += ["## Returns", ""]
    if doc["returns"]:
        out += [f"`{func.returns}`", "", linkify(" ".join(doc["returns"].split()), here, name), ""]
    else:
        out += ["Nothing. The call returns once the robot has applied it.", ""]
    lines = code_lines(doc["examples"])
    out += ["## Examples", "", "```python", *lines, "```", ""]
    for adm, title, typ in (("note", "Note", "note"), ("warning", "Warning", "warning")):
        if adm in doc["adm"]:
            out += ["## Further details", "", f'!!! {typ} "{title}"', "",
                    *[f"    {ln}" for ln in linkify(doc["adm"][adm], here, name).splitlines()], ""]

    refusals = [c for c in data.facts["queued_refusals"] if c != "UNKNOWN_CMD"
                and (c != "CLIENT_TOO_OLD" or command in data.rules.get("POSE_COMMANDS", ()))]
    own = errors_section(doc["adm"].get("errors", ""))
    fails = own + [(c, "") for c in QUEUED_FAILS]
    n = len(refusals) + len(fails) + len(QUEUED_ENDINGS)
    body = []
    if queued:
        conds = ([f"{' or '.join(modes)} mode"] if modes else []) + ([str(state).lower()] if state else []) \
            + (["homed"] if homed else [])
        when = conds[0] if len(conds) == 1 else ", ".join(conds[:-1]) + " and " + conds[-1]
        body.append("This command is added to the robot's motion queue. The robot accepts it only when it is ready "
                    f"for motion ({when}), from the client that holds control or when no client does. Otherwise, "
                    "the robot refuses it with one of:")
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
    # Collapsed: a <details> box (the theme styles it like its own collapsible notes), the count in the title.
    out += ['<details class="restrictions" markdown>',
            f'<summary>Usage restrictions <span class="count">{n} codes</span></summary>', "", *body, "", "</details>", ""]

    msg, read_pose = wire_message(name, lines, data.rules)
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


def overview(group: str, here: str, data: Data) -> str:
    rows = ["| Command | What it does | Runs |", "|---|---|---|"]
    for name in GROUPS[group]:
        func = data.method(name)
        summary = func.docstring.value.splitlines()[0] if func.docstring else ""
        command = command_of(name, data.rules)
        runs = "Queued" if data.rules["COMMAND_RULES"][command][0] == data.rules["QUEUED"] else "At once"
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
        files.append(File.generated(config, path, content=page(name, _data)))
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
