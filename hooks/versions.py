"""Write the version facts of versions.yml into the pages (versioning step V6, 2026-10-22).

Five placeholders, each replaced when the site is built:

    <!-- doc-meta: KEY -->      a manual's version box, on its landing page: document number, runtime version (the
                                software guides), revision, publication date, what it applies to
    <!-- documents-table -->    the list of every document, on every About page
    <!-- version: COMPONENT -->      a component's version in running text or a command: its tag without the
                                leading v (v1.1.1 is written 1.1.1)
    <!-- version-url: COMPONENT -->  the address of the component's files at its tag, {repository}/tree/{tag};
                                with `release_page: true`, its release page {repository}/releases/tag/{tag}
                                (where an image is downloaded)
    <!-- version-link: COMPONENT --> a link to that address with the version as its text

COMPONENT is a top-level entry of versions.yml with a repository and a tag (runtime, os_image), or GROUP.KEY for
one inside a group: the same syntax as PAROL-docs' hook (2026-11-02), whose downloads page these serve too.

The facts live in versions.yml only. A malformed or missing fact, or an unknown manual, stops the build: a version
on a page is never guessed. Registered in mkdocs.yml under `hooks:`.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

import yaml
from mkdocs.exceptions import PluginError

META_RE = re.compile(r"<!--\s*doc-meta:\s*([A-Za-z0-9_-]+)\s*-->")
TABLE_RE = re.compile(r"<!--\s*documents-table\s*-->")
COMP_RE = re.compile(r"<!--\s*version(-url|-link)?:\s*([A-Za-z0-9_-]+)(?:\.([A-Za-z0-9_-]+))?\s*-->")
REQUIRED = ("number", "title", "revision", "status", "covers")

_facts: dict = {}


def load(path) -> dict:
    """versions.yml, checked. Raises PluginError naming what is wrong."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise PluginError(f"versions.yml: {exc}") from exc
    if not isinstance(data, dict):
        raise PluginError("versions.yml: not a mapping")
    docs_version = str(data.get("docs_version", ""))
    if not re.fullmatch(r"\d+\.\d+", docs_version):
        raise PluginError(f"versions.yml: docs_version {docs_version!r} is not MAJOR.MINOR, e.g. \"0.9\"")
    tag = str((data.get("runtime") or {}).get("tag", ""))
    m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", tag)
    if not m:
        raise PluginError(f"versions.yml: runtime.tag {tag!r} is not vMAJOR.MINOR.PATCH, e.g. v0.9.0")
    if f"{m.group(1)}.{m.group(2)}" != docs_version:
        raise PluginError(f"versions.yml: runtime.tag {tag} does not belong to docs_version {docs_version}")
    manuals = data.get("manuals")
    if not isinstance(manuals, dict) or not manuals:
        raise PluginError("versions.yml: no manuals")
    for key, doc in manuals.items():
        missing = [f for f in REQUIRED if not (doc or {}).get(f)]
        if missing:
            raise PluginError(f"versions.yml: manual {key!r} lacks {', '.join(missing)}")
        if not re.fullmatch(r"\d{4}\.[A-Z]", str(doc["revision"])):
            raise PluginError(f"versions.yml: manual {key!r} revision {doc['revision']!r} is not YEAR.LETTER, e.g. 2026.A")
        if doc["status"] not in ("draft", "published"):
            raise PluginError(f"versions.yml: manual {key!r} status {doc['status']!r} is not draft or published")
        published = doc.get("published")
        if doc["status"] == "published" and not isinstance(published, datetime.date):
            raise PluginError(f"versions.yml: manual {key!r} is published but has no publication date (YYYY-MM-DD)")
    return data


def meta_block(key: str, data: dict) -> str:
    """The version box of manual `key`."""
    doc = data["manuals"].get(key)
    if doc is None:
        raise PluginError(f"doc-meta: no manual {key!r} in versions.yml")
    draft = doc["status"] == "draft"
    lines = [f"**Document number:** {doc['number']}"]
    if doc.get("guide"):
        lines.append(f"**Runtime version:** {data['docs_version']}")
    lines.append(f"**Revision:** {doc['revision']}" + (" (draft)" if draft else ""))
    published = doc.get("published")
    lines.append(f"**Published:** {published.isoformat() if isinstance(published, datetime.date) else '—'}")
    applies = [f"runtime {data['docs_version']}"] if doc.get("guide") else []
    if doc.get("applies_to"):
        applies.insert(0, str(doc["applies_to"]))
    lines.append(f"**Applies to:** {', '.join(applies)}")
    lines.append("*Original instructions*")
    return '<div class="doc-meta" markdown>\n\n' + "\n\n".join(lines) + "\n\n</div>"


def documents_table(data: dict) -> str:
    """Every document, with its number and what it covers."""
    rows = [f"| {d['title']} | {d['number']} | {d['covers']} |" for d in data["manuals"].values()]
    return ("| Document | Number | Covers |\n|---|---|---|\n" + "\n".join(rows) + "\n\n"
            f"The software guides describe one runtime version each, here {data['docs_version']}; the manuals carry a "
            "revision and describe a hardware revision. Which versions of the runtime, the client, the drive "
            "firmware, the control box, the arm and the description package work together is listed under "
            "*Support → Versions & compatibility*, together with each part's release notes.")


def component(group: str, key, data: dict) -> dict:
    """A top-level entry (runtime, os_image) or GROUP.KEY, with a repository and a tag. Unknown names stop the build."""
    comp = data.get(group) if key is None else (data.get(group) or {}).get(key)
    name = group + (f".{key}" if key else "")
    if not isinstance(comp, dict) or not comp.get("repository") or not comp.get("tag") or group == "manuals":
        raise PluginError(f"versions.yml: no {name} with a repository and a tag for <!-- version: {name} -->")
    return comp


def version_text(comp: dict) -> str:
    tag = str(comp["tag"])
    return tag[1:] if re.fullmatch(r"v\d.*", tag) else tag


def version_placeholder(kind, group: str, key, data: dict) -> str:
    """<!-- version: ... -->, <!-- version-url: ... --> and <!-- version-link: ... -->."""
    comp = component(group, key, data)
    if not kind:
        return version_text(comp)
    repo = str(comp["repository"]).rstrip("/")
    url = f"{repo}/releases/tag/{comp['tag']}" if comp.get("release_page") else f"{repo}/tree/{comp['tag']}"
    return url if kind == "-url" else f"[{version_text(comp)}]({url})"


def on_config(config):
    global _facts
    _facts = load(Path(config.config_file_path).parent / "versions.yml")
    config.extra["docs_version"] = _facts["docs_version"]
    return config


def on_page_markdown(markdown, page, config, files):
    markdown = META_RE.sub(lambda m: meta_block(m.group(1), _facts), markdown)
    markdown = COMP_RE.sub(lambda m: version_placeholder(m.group(1), m.group(2), m.group(3), _facts), markdown)
    return TABLE_RE.sub(lambda m: documents_table(_facts), markdown)
