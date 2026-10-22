#!/usr/bin/env python3
"""Create every page the nav names and that does not exist yet, as a stub in its template.

Never overwrites an existing file. Run from PAR-docs/:  .venv/bin/python tools/make_stubs.py [--dry-run]

Templates (by what the nav entry is):
  * a document's landing page   (par6/index.md, rcb/index.md, ... — see DOCUMENTS)   -> title, hero, document block
  * "About this manual/guide"    (<doc>/about.md)                                      -> scope, finding your way,
                                                                                         warnings and notes, related
                                                                                         documents, document history
  * a chapter page               (<doc>/<chapter>/index.md)                            -> intro + list of its pages
  * a Glossary page              (<doc>/terminology.md)                                -> the shared glossary snippet
  * any other page                                                                     -> heading + stub notice
Every stub carries `status: draft` in its front matter, so the sidebar shows which pages are not written yet.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from mkdocs.config import load_config

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# folder -> (short name, landing title, document number, kind: hardware | software, "applies to")
DOCUMENTS = {
    "par6": ("PAR6 Hardware Manual", "PAR6 Hardware Manual", "SR-1001", "hardware", "PAR6 arm, revision 1.x"),
    "rcb": ("Control Box Manual", "Robot Control Box Manual", "SR-2001", "software",
            "control box PCB v1 and v2, runtime 0.9"),
    "programming": ("Programming Guide", "Programming Guide", "SR-4001", "software", "runtime 0.9"),
    "dashboard": ("Dashboard Guide", "Dashboard Guide", "SR-4002", "software", "runtime 0.9"),
    "grippers/msg": ("MSG Gripper Manual", "MSG Gripper Manual", "SR-3001", "hardware", "MSG grippers, revision 1.x"),
    "grippers/ssg48": ("SSG48 Gripper Manual", "SSG48 Gripper Manual", "SR-3002", "hardware",
                       "SSG48 gripper, revision 1.x"),
    "grippers/pneumatic": ("Pneumatic Tools Manual", "Pneumatic Tools Manual", "SR-3003", "hardware",
                           "pneumatic gripper and vacuum tool, revision 1.x"),
    "simulation": ("Simulation Guide", "Simulation and AI Guide", "SR-4003", "software",
                   "description package 2.0, runtime 0.9"),
}

# Pages whose subject does not exist in the product yet: they say so instead of "stub".
PLANNED = {
    "simulation/isaac-sim.md", "simulation/ai/index.md", "simulation/ai/teleoperation.md",
    "simulation/ai/vla.md", "simulation/ai/inference.md", "rti/soft/teleoperation.md",
    "par6/appendices/emc-test-results.md", "par6/appendices/letter-of-volatility.md",
    "par6/building/bill-of-materials.md", "par6/building/printing.md",
    "par6/building/mechanical-assembly.md", "par6/building/electronics-wiring.md",
}

DRAFT = "---\nstatus: draft\n---\n\n"

PUBLISHER = (
    "Source Robotics d.o.o. publishes this document as part of the open-source PAR6 project. It is revised as the "
    "product changes; the document number, revision and date above identify the version you are reading, and the "
    "revision history on the next page says what changed. Take care that the revision you follow matches the "
    "hardware revision or runtime version named under *Applies to*. The licence that covers this text is stated in "
    "the documentation repository."
)


def strip_number(title: str) -> str:
    """'3. Technical data' -> 'Technical data'; 'Step 2: ...' is kept."""
    return re.sub(r"^\d+\.\s+", "", title)


def walk(items, chapter_title=None, out=None):
    """Yield (path, title, kind, siblings) for every page in the nav."""
    if out is None:
        out = []
    for item in items:
        if isinstance(item, str):                       # a bare path: a section's own page
            out.append((item, chapter_title, "section-index", items))
        elif isinstance(item, dict):
            for title, value in item.items():
                if isinstance(value, str):
                    out.append((value, title, "page", items))
                else:
                    walk(value, title, out)
    return out


def document_of(path: str):
    for folder, meta in DOCUMENTS.items():
        if path.startswith(folder + "/"):
            return folder, meta
    return None, None


def landing(folder, meta):
    short, title, number, kind, applies = meta
    up = "../" * (folder.count("/") + 1)
    runtime = "**Runtime version:** 0.9 (development)\n\n" if kind == "software" else ""
    return (
        "---\nhide:\n  - toc\n---\n\n"
        f"# {title}\n\n"
        f"![{short}]({up}assets/placeholder-hero.png){{ .hero }}\n\n"
        '<div class="doc-meta" markdown>\n\n'
        f"**Document number:** {number}\n\n"
        f"{runtime}"
        "**Revision:** 2026.A (draft)\n\n"
        "**Published:** —\n\n"
        f"**Applies to:** {applies}\n\n"
        "*Original instructions*\n\n"
        "</div>\n\n"
        f"{PUBLISHER}\n"
    )


def about(folder, meta):
    short, title, number, kind, applies = meta
    word = "guide" if kind == "software" else "manual"
    history = (
        f"The {short} is written for a specific runtime `{{major}}.{{minor}}` version; one revision is kept per "
        "runtime version, and the version selector in the header switches between them."
        if kind == "software"
        else f"The {short} does not depend on the runtime version. It describes the hardware revision named on its "
        "landing page and is revised as the hardware changes."
    )
    return (
        DRAFT +
        f"# About this {word}\n\n"
        "## Scope and audience\n\n"
        f"<!-- purpose, audience, prerequisites of the {short}; planning/02_attack_plan_v2.md §3, "
        "planning/03_site_model_v3.md §5.2 -->\n\n"
        f"*Stub.* One paragraph on what the {short} covers, who it is for, and what must be read first.\n\n"
        "## Finding your way\n\n"
        '--8<-- "navigation.md"\n\n'
        "## Warnings and notes\n\n"
        "Three kinds of highlighted text appear in this documentation. Read every Danger and Notice before you act "
        "on the step it belongs to.\n\n"
        '--8<-- "symbols.md"\n\n'
        "## Related documents\n\n"
        '--8<-- "documents.md"\n\n'
        "## Document history\n\n"
        f"{history}\n\n"
        "| Revision | Date | Changes |\n|---|---|---|\n| 2026.A (draft) | — | First version |\n"
    )


def chapter(title, siblings):
    lines = [DRAFT.rstrip("\n"), "", f"# {strip_number(title)}", "",
             "*Stub.* One paragraph on what this chapter covers.", "", "## In this chapter", ""]
    for item in siblings:
        if isinstance(item, dict):
            for t, v in item.items():
                if isinstance(v, str):
                    lines.append(f"- [{t}]({Path(v).name})")
    return "\n".join(lines) + "\n"


def glossary():
    return "# Glossary\n\n" '--8<-- "terminology.md"\n'


def page(title, path):
    heading = strip_number(title)
    if path in PLANNED:
        body = ('!!! note "Planned"\n    This feature or document does not exist yet. The page is here so the '
                "structure is complete; it will say so until the content exists.\n")
    else:
        body = "*Stub.* <!-- sources: planning/01_structure_proposal_v1.md §4 -->\n"
    return f"{DRAFT}# {heading}\n\n{body}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = load_config(str(ROOT / "mkdocs.yml"))
    created = 0
    for path, title, kind, siblings in walk(cfg["nav"]):
        target = DOCS / path
        if target.exists():
            continue
        folder, meta = document_of(path)
        if meta and path == f"{folder}/index.md":
            text = landing(folder, meta)
        elif meta and path == f"{folder}/about.md":
            text = about(folder, meta)
        elif path.endswith("/terminology.md"):
            text = glossary()
        elif kind == "section-index":
            text = chapter(title or Path(path).parent.name, siblings)
        else:
            text = page(title or Path(path).stem, path)
        print(("would create " if args.dry_run else "create ") + path)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        created += 1
    print(f"{created} page(s) {'to create' if args.dry_run else 'created'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
