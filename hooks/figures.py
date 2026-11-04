"""Captions under the pictures: every standalone picture becomes a numbered figure, its description the caption.

The same hook as PAROL-docs' (2026-11-02), with three additions for this site: a figure written as raw HTML (a
command page's drawing, docs/includes/command_extras/) gets its number too, pictures inside fenced code are left
alone, and the Dev Lab tab, which shows Material's elements as they are, is not touched.

A picture on a line of its own, with a blank line (or the start of its block) before and after it, is wrapped in the
manuals' figure form (the Dev Lab's "Figure with a numbered caption"):

    <figure markdown="span">
      ![alt](picture.webp#only-light){ width="900" }
      ![alt](picture_dark.webp#only-dark){ width="900" }
      <figcaption>Figure 3.2: alt.</figcaption>
    </figure>

A light and a dark version of one picture (two lines, #only-light and #only-dark) are one figure. The caption is the
picture's alt text, so a picture is described once. A raw <figure> keeps its own caption, written on one line as
<figcaption>text</figcaption> without a number; the hook puts "Figure N: " in front. Never type a figure number: the
build check (tools/test_tools.py) refuses one.

Numbering: per chapter in reading order (nav order) for pages under a numbered chapter folder or file
(par6/03-technical-specifications/..., par6/10-decommissioning.md, rcb/03-technical-specifications.md: "Figure 3.2"),
per page elsewhere ("Figure 2"). Pictures with the class .hero, pictures inside a paragraph of text and pictures
without alt text are left as they are. Registered in mkdocs.yml under `hooks:`, after command_pages.py, whose
generated pages it numbers too.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict

IMG = re.compile(r"^(?P<ind>[ \t]*)!\[(?P<alt>[^\]]+)\]\((?P<src>[^)\s]+)\)(?P<attr>\{[^}]*\})?[ \t]*$")
CAPTION = re.compile(r"^(?P<ind>[ \t]*)<figcaption>(?P<text>.*?)</figcaption>[ \t]*$")
FENCE = re.compile(r"^[ \t]*(```|~~~)")
NUMBERED = re.compile(r"^(\d{2})-")
SKIP = ("devlab/",)          # page paths the hook leaves alone
_start: dict[str, int] = {}


def chapter(uri: str) -> tuple[str, str]:
    """(counter key, label prefix): a numbered chapter counts across its pages, any other page on its own."""
    parts = uri.replace("\\", "/").split("/")
    for i, part in enumerate(parts):
        m = NUMBERED.match(part)
        if m:
            return "/".join(parts[:i + 1]), f"{int(m.group(1))}."
    return uri, ""


def fenced(lines: list[str]) -> list[bool]:
    """For each line: is it inside (or a fence of) a fenced code block?"""
    out, inside = [], None
    for line in lines:
        m = FENCE.match(line)
        if inside is None and m:
            inside = m.group(1)
            out.append(True)
        elif inside is not None:
            out.append(True)
            if m and m.group(1) == inside and line.strip() == inside:
                inside = None
        else:
            out.append(False)
    return out


def figure_runs(lines: list[str]):
    """(first, last) line index of each run of one or two standalone pictures that makes one figure."""
    code = fenced(lines)
    runs, i = [], 0
    while i < len(lines):
        m = IMG.match(lines[i])
        if code[i] or not m or ".hero" in (m["attr"] or "") or (i > 0 and lines[i - 1].strip()
                                                               and not lines[i - 1].lstrip().startswith(("===", "!!!", "???"))):
            i += 1
            continue
        j = i
        if j + 1 < len(lines):
            n = IMG.match(lines[j + 1])
            if n and n["ind"] == m["ind"] and ("#only-light" in m["src"] or "#only-dark" in m["src"]):
                j += 1
        if j + 1 < len(lines) and lines[j + 1].strip():
            i = j + 1
            continue
        runs.append((i, j))
        i = j + 1
    return runs


def raw_captions(lines: list[str]) -> list[int]:
    """Line index of each one-line <figcaption> of a raw HTML figure, outside fenced code."""
    code = fenced(lines)
    return [i for i, line in enumerate(lines) if not code[i] and CAPTION.match(line)]


def items(lines: list[str]) -> list[tuple[int, int, str]]:
    """Every figure of a page in reading order: (first, last, kind), kind "picture" or "raw"."""
    found = [(a, b, "picture") for a, b in figure_runs(lines)] + [(i, i, "raw") for i in raw_captions(lines)]
    return sorted(found)


def wrap(lines: list[str], first: int, last: int, label: str) -> list[str]:
    m = IMG.match(lines[first])
    ind = m["ind"]
    alt = m["alt"].strip()
    caption = alt if alt.endswith((".", "!", "?")) else alt + "."
    out = [f'{ind}<figure markdown="span">']
    out += [f"{ind}  {lines[k].strip()}" for k in range(first, last + 1)]
    out += [f"{ind}  <figcaption>Figure {label}: {html.escape(caption, quote=False)}</figcaption>", f"{ind}</figure>"]
    return out


def number_caption(line: str, label: str) -> list[str]:
    m = CAPTION.match(line)
    return [f"{m['ind']}<figcaption>Figure {label}: {m['text'].strip()}</figcaption>"]


def transform(markdown: str, start: int, prefix: str) -> tuple[str, int]:
    lines = markdown.split("\n")
    found = items(lines)
    labels = {first: f"{prefix}{start + k + 1}" for k, (first, _, _) in enumerate(found)}
    for first, last, kind in reversed(found):
        new = wrap(lines, first, last, labels[first]) if kind == "picture" else number_caption(lines[first], labels[first])
        lines[first:last + 1] = new
    return "\n".join(lines), len(found)


def skipped(uri: str) -> bool:
    return uri.replace("\\", "/").startswith(SKIP)


def on_nav(nav, config, files):
    """Number in reading order: count each page's figures in nav order, per chapter."""
    _start.clear()
    count = defaultdict(int)
    for page in nav.pages:
        uri = page.file.src_uri
        if skipped(uri):
            continue
        key, _ = chapter(uri)
        try:
            text = page.file.content_string.replace("\r\n", "\n")   # also the generated command pages
        except (OSError, TypeError, ValueError):
            continue
        _start[uri] = count[key]
        count[key] += len(items(text.split("\n")))
    return nav


def on_page_markdown(markdown, page, config, files):
    uri = page.file.src_uri
    if skipped(uri):
        return markdown
    _, prefix = chapter(uri)
    text, _ = transform(markdown.replace("\r\n", "\n"), _start.get(uri, 0), prefix)
    return text
