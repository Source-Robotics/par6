#!/usr/bin/env python3
"""Fill the generated pages from the runtime's tagged release (versioning step V6, 2026-10-22).

    .venv/bin/python tools/sync_runtime.py              write docs/includes/generated/ from the release in versions.yml
    .venv/bin/python tools/sync_runtime.py --check      exit 1 when a generated file differs from what the release gives
    .venv/bin/python tools/sync_runtime.py --runtime PATH --tag v0.9.0

It reads the runtime repository with `git show <tag>:<file>`, so always the TAGGED release, never uncommitted work:
VERSION, COMPATIBILITY.md, CHANGELOG.md, utility/error_catalog.py, data/robotics_data.py. It writes, into
docs/includes/generated/:

    compatibility.md          the compatibility table and what its columns mean     (support/versions.md)
    runtime_release_notes.md  every released version's changelog section           (runtime release notes)
    error_codes.md            every error, warning and event code with cause, effect and fix  (error codes)
    telemetry_tags.md         every telemetry tag with its meaning and decimals     (telemetry tags)

The pages include them with `--8<-- "generated/<file>"`. Never edit a generated file: change the runtime, release
it, set runtime.tag in versions.yml, and run this tool again. It refuses a release whose VERSION does not match its
tag or whose MAJOR.MINOR is not docs_version, and generated text that names another robot maker (the public docs
never do).

The Python API reference (2026-10-23) is built by mkdocstrings from the client's own docstrings. The tool copies the
source it reads into api_src/, from the same tag: the robotclient package and communication/protocol.py (the command
rules hooks/griffe_robot_rules.py turns into each method's "Command rules" box). api_src/SOURCE.txt says where the
copy came from.

    .venv/bin/python tools/sync_runtime.py --worktree   api_src/ from the runtime's WORKING TREE, for a local preview
                                                        of docstrings not yet released; generated/ is left alone

A preview copy is marked in SOURCE.txt: --check reports it out of date and tools/test_tools.py (the build check)
fails on it, so it cannot be published. Run the tool without --worktree before committing.

The runtime repository is --runtime, else $RCB_RUNTIME_DIR, else an RCB-Runtime folder next to this repository or
next to its parent folder. Python 3.11+, PyYAML (installed with MkDocs).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "includes" / "generated"
API_OUT = ROOT / "api_src"
API_SOURCE = "SOURCE.txt"                  # where the copy came from
WORKTREE_MARK = "WORKTREE PREVIEW"         # first words of SOURCE.txt for a copy of the working tree
# Other robot makers' names never appear in the public docs. The list of names is not published either: it is the
# runtime's pre-push hook's (RCB-Runtime/.git/hooks/pre-push, never pushed), read when the sync runs (2026-10-23).
HOOK = Path(".git") / "hooks" / "pre-push"
KIND_TEXT = {"stop": "the robot stops and is disabled", "fails": "the command, move or program fails or is refused; "
             "the robot is not affected", "warning": "the robot keeps running", "event": "information only"}
SOURCE_TITLE = {"joint": "Joints, TCP and the loop", "motor": "Joint drives", "motor_config": "Joint drive settings",
                "gripper": "Gripper", "gripper_motor": "Gripper drive", "gripper_config": "Gripper drive settings"}


class SyncError(Exception):
    pass


def find_runtime(arg: str | None) -> Path:
    candidates = [arg, os.environ.get("RCB_RUNTIME_DIR"), ROOT.parent / "RCB-Runtime", ROOT.parent.parent / "RCB-Runtime"]
    for c in candidates:
        if c and (Path(c) / ".git").exists():
            return Path(c)
    raise SyncError("no RCB-Runtime repository found: pass --runtime PATH or set RCB_RUNTIME_DIR")


class Names:
    """The hook's names (PAT, any case) and acronyms (ACR, exact case) as one search()."""

    def __init__(self, pat: str, acr: str):
        self.pat = re.compile(pat, re.I)
        self.acr = re.compile(acr) if acr else None

    def search(self, text: str):
        return self.pat.search(text) or (self.acr.search(text) if self.acr else None)


def other_makers(runtime: Path) -> Names:
    """The list of other makers' names from the runtime's pre-push hook. No hook, no sync: the guard is not optional."""
    hook = runtime / HOOK
    text = hook.read_text(encoding="utf-8") if hook.exists() else ""
    pat = re.search(r"^PAT='(.*)'$", text, re.M)
    acr = re.search(r"^ACR='(.*)'$", text, re.M)
    if not pat:
        raise SyncError(f"{hook}: no list of other makers' names (the hook's PAT='...' line) — restore the hook first")
    return Names(pat.group(1), acr.group(1) if acr else "")


def git_show(runtime: Path, tag: str, path: str) -> str:
    r = subprocess.run(["git", "-C", str(runtime), "show", f"{tag}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        raise SyncError(f"{tag}:{path} not readable in {runtime}: {r.stderr.strip()} (are the tags fetched?)")
    return r.stdout


def git_lines(runtime: Path, *args: str) -> list[str]:
    r = subprocess.run(["git", "-C", str(runtime), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SyncError(f"git {' '.join(args)} failed in {runtime}: {r.stderr.strip()}")
    return [ln for ln in r.stdout.splitlines() if ln]


def api_paths(runtime: Path, tag: str | None) -> list[str]:
    """The files the Python API reference reads: the robotclient package's modules and the command rules."""
    if tag is None:
        names = git_lines(runtime, "ls-files", "--cached", "--others", "--exclude-standard", "--", "robotclient")
        names = [n for n in names if (runtime / n).is_file()]
    else:
        names = git_lines(runtime, "ls-tree", "-r", "--name-only", tag, "--", "robotclient")
    py = sorted(n for n in names if n.endswith(".py"))
    if "robotclient/__init__.py" not in py:
        raise SyncError(f"no robotclient package in {tag or 'the working tree'}")
    return py + ["communication/protocol.py"]


def _literal(source: str, name: str, inside: str | None = None):
    """A literal assigned to `name` at module level, or inside function `inside`."""
    tree = ast.parse(source)
    scope = tree.body
    if inside is not None:
        scope = next(n.body for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == inside)
    for node in scope:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        if any(isinstance(t, ast.Name) and t.id == name for t in targets):
            return ast.literal_eval(node.value)
    raise SyncError(f"{name} not found")


def _reply_codes(source: str, functions: tuple[str, ...]) -> list[str]:
    """Every error code the named functions answer with: the "code" of each {"status": "error", "code": ...} reply."""
    found = []
    for fn in ast.parse(source).body:
        if isinstance(fn, ast.FunctionDef) and fn.name in functions:
            for node in ast.walk(fn):
                if isinstance(node, ast.Dict):
                    for k, v in zip(node.keys, node.values):
                        if (isinstance(k, ast.Constant) and k.value == "code" and isinstance(v, ast.Constant)
                                and isinstance(v.value, str)):
                            found.append((v.lineno, v.col_offset, v.value))
    return list(dict.fromkeys(code for _, _, code in sorted(found)))       # in the order the code checks them


def runtime_facts(read) -> str:
    """runtime_facts.json, read from the runtime's own code (2026-10-23, "document everything"):

    settings / refused   every per-move setting the robot accepts, and the ones it refuses per move;
    values               every value of a choice, with its other accepted spellings (and which are built);
    queued_refusals      every code the executor answers a queued command with when it is sent (dispatch and
                         _submit_queued; UNKNOWN_CMD never reaches a client method, CLIENT_TOO_OLD only pose commands).
    """
    opts = read("motion/exec_commands.py")
    executor = read("command_executor.py")
    refused = _literal(executor, "_UNSUPPORTED_PER_COMMAND_OPTIONS")
    allowed = set(_literal(opts, "_ALLOWED_OPTION_KEYS"))
    values = {}
    for key, name, inside in (("profile", "_PROFILE_ALIASES", None), ("ik_solver", "_IK_SOLVER_ALIASES", None),
                              ("blend_mode", "_BLEND_MODE_ALIASES", None),
                              ("singularity_strategy", "_SINGULARITY_STRATEGY_ALIASES", None),
                              ("blend_continuity", "aliases", "normalize_blend_continuity")):
        aliases = _literal(opts, name, inside)
        canonical = list(dict.fromkeys(aliases.values()))
        values[key] = {"values": canonical, "also_accepted": {a: v for a, v in aliases.items() if a not in canonical}}
    values["singularity_strategy"]["built"] = list(_literal(opts, "IMPLEMENTED_SINGULARITY_STRATEGIES"))
    return json.dumps({"settings": sorted(allowed - set(refused)), "refused": refused, "values": values,
                       "queued_refusals": _reply_codes(executor, ("dispatch", "_submit_queued"))},
                      indent=2, sort_keys=True) + "\n"


def build_api(runtime: Path, tag: str | None) -> dict[str, str]:
    """api_src/'s files: the source from the tag (tag None: the working tree), the error catalog, the per-move settings
    (computed from the runtime's code) and SOURCE.txt."""
    read = (lambda p: (runtime / p).read_text(encoding="utf-8")) if tag is None else (lambda p: git_show(runtime, tag, p))
    if tag is None:
        files = {p: (runtime / p).read_text(encoding="utf-8") for p in api_paths(runtime, None)}
        head = git_lines(runtime, "rev-parse", "--short=12", "HEAD")[0]
        dirty = git_lines(runtime, "status", "--porcelain", "--", "robotclient", "communication/protocol.py")
        source = (f"{WORKTREE_MARK}: the RCB-Runtime working tree at {head}"
                  f"{' with uncommitted changes' if dirty else ''}. Never publish it: run tools/sync_runtime.py "
                  f"without --worktree.\n")
    else:
        files = {p: git_show(runtime, tag, p) for p in api_paths(runtime, tag)}
        commit = git_lines(runtime, "rev-list", "-n", "1", tag)[0]
        source = f"RCB-Runtime {tag} ({commit[:12]}), copied by tools/sync_runtime.py. Do not edit.\n"
    files["utility/error_catalog.py"] = read("utility/error_catalog.py")
    files["runtime_facts.json"] = runtime_facts(read)
    names = other_makers(runtime)
    for name, text in files.items():
        hit = names.search(text)
        if hit:
            raise SyncError(f"{name}: names another robot maker ({hit.group(0)!r}) — fix the runtime text first")
    files[API_SOURCE] = source
    return files


def api_stale(files: dict[str, str]) -> tuple[list[str], list[str]]:
    """(files to write, files in api_src/ that the copy does not have)."""
    have = {p.relative_to(API_OUT).as_posix(): p for p in API_OUT.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts} if API_OUT.exists() else {}
    write = [n for n, text in files.items() if n not in have or have[n].read_text(encoding="utf-8") != text]
    return write, sorted(set(have) - set(files))


def write_api(files: dict[str, str]) -> tuple[int, int]:
    """Bring api_src/ to exactly `files`; returns (written, removed)."""
    write, extra = api_stale(files)
    for n in extra:
        (API_OUT / n).unlink()
    for n in write:
        (API_OUT / n).parent.mkdir(parents=True, exist_ok=True)
        (API_OUT / n).write_text(files[n], encoding="utf-8")
    for d in sorted((p for p in API_OUT.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    return len(write), len(extra)


def esc(text) -> str:
    """Plain text for Markdown: no HTML tags (an XML element name like <max_payload_kg> stays visible), no emphasis."""
    return str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("*", r"\*").replace("|", r"\|")


def banner(tag: str, commit: str) -> str:
    return (f"<!-- Generated by tools/sync_runtime.py from RCB-Runtime {tag} ({commit[:12]}). Do not edit: change the "
            f"runtime, release it, then run the tool again. -->\n")


def gen_compatibility(text: str) -> str:
    """The table and the column meanings of COMPATIBILITY.md (its title and intro belong to the page)."""
    lines = text.splitlines()
    table = [ln for ln in lines if ln.startswith("|")]
    if len(table) < 3:
        raise SyncError("COMPATIBILITY.md: no table with at least one release row")
    start = next((i for i, ln in enumerate(lines) if ln.strip() == "## What each column means"), None)
    if start is None:
        raise SyncError("COMPATIBILITY.md: no '## What each column means' section")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    meaning = "\n".join(lines[start + 1:end]).strip()
    return "\n".join(table) + "\n\n### What each column means\n\n" + meaning + "\n"


def gen_release_notes(text: str) -> str:
    """Every released section of CHANGELOG.md, newest first (Unreleased is not a release)."""
    heading = re.compile(r"^## \[(?P<v>[^\]]+)\](?: - (?P<d>\d{4}-\d{2}-\d{2}))?\s*$")
    out, cur = [], None
    for ln in text.splitlines():
        m = heading.match(ln)
        if m:
            cur = None if m.group("v") == "Unreleased" else {"v": m.group("v"), "d": m.group("d"), "body": []}
            if cur:
                out.append(cur)
        elif ln.startswith("## "):
            cur = None
        elif cur is not None:
            cur["body"].append(ln)
    if not out:
        raise SyncError("CHANGELOG.md: no released version")
    parts = [f"## {s['v']} ({s['d']})\n\n" + "\n".join(s["body"]).strip() + "\n" for s in out]
    return "\n".join(parts)


def gen_error_codes(source: str) -> str:
    """Every catalogued code, by group: number, code, kind, title, cause, effect, fix."""
    ns: dict = {}
    exec(compile(source, "utility/error_catalog.py", "exec"), ns)                       # noqa: S102 — our own module
    catalog, groups = ns["CATALOG"], ns["GROUPS"]
    kinds = "; ".join(f"**{k}**: {v}" for k, v in KIND_TEXT.items())
    parts = [f"Every code has a number, a name and a kind. Kinds: {kinds}.\n"]
    by_group: dict[int, list] = {}
    for code, e in catalog.items():
        by_group.setdefault(int(e["number"]) // 1000, []).append((int(e["number"]), code, e))
    for g in sorted(by_group):
        parts.append(f"## {g}xxx: {esc(groups.get(g, 'Other'))}\n")
        for number, code, e in sorted(by_group[g], key=lambda t: t[0]):
            block = [f"### {number} `{code}`\n", f"**{esc(e['title'])}**. Kind: {e['kind']}.\n"]
            for label in ("cause", "effect", "fix"):
                if e.get(label):
                    block.append(f"- {label.capitalize()}: {esc(e[label])}")
            parts.append("\n".join(block) + "\n")
    return "\n".join(parts)


def gen_telemetry_tags(source: str) -> str:
    """Every telemetry tag, by where its value comes from."""
    ns: dict = {}
    exec(compile(source, "data/robotics_data.py", "exec"), ns)                          # noqa: S102 — our own module
    tags = ns["TAGS"]
    by_src: dict[str, list] = {}
    for tag, t in tags.items():
        by_src.setdefault(t["src"], []).append((tag, t))
    parts = []
    for src in sorted(by_src, key=lambda s: list(SOURCE_TITLE).index(s) if s in SOURCE_TITLE else 99):
        rows = [f"| `{tag}` | {esc(t.get('desc'))} | {t.get('prec', '')} |" for tag, t in by_src[src]]
        parts.append(f"## {SOURCE_TITLE.get(src, src)}\n\n| Tag | Meaning | Decimals |\n|---|---|---|\n" + "\n".join(rows) + "\n")
    return "\n".join(parts)


def build(runtime: Path, tag: str, docs_version: str) -> dict[str, str]:
    version = git_show(runtime, tag, "VERSION").strip()
    if f"v{version}" != tag:
        raise SyncError(f"the release's VERSION file says {version}, its tag is {tag}")
    if ".".join(version.split(".")[:2]) != docs_version:
        raise SyncError(f"release {version} does not belong to docs_version {docs_version} (versions.yml)")
    commit = subprocess.run(["git", "-C", str(runtime), "rev-list", "-n", "1", tag], capture_output=True,
                            text=True).stdout.strip()
    head = banner(tag, commit)
    files = {
        "compatibility.md": gen_compatibility(git_show(runtime, tag, "COMPATIBILITY.md")),
        "runtime_release_notes.md": gen_release_notes(git_show(runtime, tag, "CHANGELOG.md")),
        "error_codes.md": gen_error_codes(git_show(runtime, tag, "utility/error_catalog.py")),
        "telemetry_tags.md": gen_telemetry_tags(git_show(runtime, tag, "data/robotics_data.py")),
    }
    files = {name: head + "\n" + text for name, text in files.items()}
    names = other_makers(runtime)
    for name, text in files.items():
        hit = names.search(text)
        if hit:
            raise SyncError(f"{name}: names another robot maker ({hit.group(0)!r}) — fix the runtime text first")
    return files


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runtime", help="the RCB-Runtime repository")
    ap.add_argument("--tag", help="the release tag (default: runtime.tag in versions.yml)")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when a generated file is out of date")
    ap.add_argument("--worktree", action="store_true",
                    help="copy the API source from the runtime's working tree (a local preview, never published)")
    args = ap.parse_args(argv)
    if args.worktree and (args.check or args.tag):
        ap.error("--worktree takes no --check or --tag")
    facts = yaml.safe_load((ROOT / "versions.yml").read_text(encoding="utf-8"))
    tag = args.tag or facts["runtime"]["tag"]
    try:
        runtime = find_runtime(args.runtime)
        if args.worktree:
            written, removed = write_api(build_api(runtime, None))
            print(f"api_src/ from the RCB-Runtime working tree (PREVIEW, never publish): {written} file(s) written, "
                  f"{removed} removed")
            return 0
        files = build(runtime, tag, str(facts["docs_version"]))
        api = build_api(runtime, tag)
    except SyncError as exc:
        print(f"sync_runtime: {exc}", file=sys.stderr)
        return 2
    stale = [n for n, text in files.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding="utf-8") != text]
    api_write, api_extra = api_stale(api)
    if args.check:
        for n in stale:
            print(f"out of date: docs/includes/generated/{n}")
        for n in api_write:
            print(f"out of date: api_src/{n}")
        for n in api_extra:
            print(f"not in {tag}: api_src/{n}")
        bad = len(stale) + len(api_write) + len(api_extra)
        print("generated pages up to date" if not bad else f"{bad} out of date: run tools/sync_runtime.py")
        return 1 if bad else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for n in stale:
        (OUT / n).write_text(files[n], encoding="utf-8")
    written, removed = write_api(api)
    print(f"from RCB-Runtime {tag}: {len(stale)} generated file(s) written, {len(files) - len(stale)} unchanged; "
          f"api_src/ {written} written, {removed} removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
