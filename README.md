# PAR6 documentation

The documentation of the PAR6 robot arm system by [Source Robotics](https://source-robotics.com): the arm, the Robot
Control Box, programming and the real-time interface, the dashboard, end effectors, and simulation.

**Read it at [docs.source-robotics.com/par6](https://docs.source-robotics.com/par6/).**

## What is in this repository

| Folder in `docs/` | Manual |
|---|---|
| `par6/` | PAR6 Hardware Manual |
| `rcb/` | Robot Control Box Manual |
| `programming/`, `rti/` | Programming Guide, including the real-time interface |
| `dashboard/` | Dashboard Guide |
| `grippers/` | End effectors |
| `simulation/` | Simulation and AI Guide |
| `support/` | Contact, reporting a problem, contributing, versions and compatibility |
| `includes/` | Text shared by several pages, such as the warning symbols and the terminology |

The site is built with [MkDocs](https://www.mkdocs.org/) and the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme. `mkdocs.yml` holds the navigation and the
settings, and `overrides/` holds the theme changes.

## Preview it locally

You need Python 3.11 or newer.

```bash
git clone https://github.com/Source-Robotics/par6.git
cd par6
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve
```

Open `http://127.0.0.1:8000/par6/`. The page reloads by itself when you save a file.

Every push and pull request runs `mkdocs build --strict`, which fails on a broken link or a missing page. Run it
before you open a pull request.

## Versions and releases

Each minor release of the robot's runtime has its own version of the documentation, for example `0.9`. The version
selector in the site's header switches between them. The versions are built with
[mike](https://github.com/jimporter/mike) and kept in the `gh-pages` branch.

**All version facts live in `versions.yml`, never in a page.** It holds:

- `docs_version`: the runtime's `MAJOR.MINOR` these pages describe, which is also the name the version is published under
- `runtime.tag`: the runtime release the generated pages come from
- one entry per manual: document number, title, revision, status, publication date, what it applies to

`hooks/versions.py` writes these into every manual's version box and into the list of documents on every About
page. A malformed or missing fact stops the build.

**Some pages are generated from the runtime repository.** They are the compatibility table, the runtime release
notes, the error and event codes, and the telemetry tags. Their content is in `docs/includes/generated/`. Never edit
those files by hand: `tools/sync_runtime.py` writes them from the runtime's tagged release, and only from the tag,
never from uncommitted work.

```bash
.venv/bin/python tools/sync_runtime.py           # write them from the release in versions.yml
.venv/bin/python tools/sync_runtime.py --check   # exit 1 if they are out of date
```

**The command reference is generated: one page per command of the Python client.** `hooks/command_pages.py` builds
each page from `api_src/`, a copy of the runtime's `robotclient` package, its command rules, its error catalog and
facts read from its code, which the same tool writes from the same tag. The docstrings are written to the runtime's
`docstrings_guide.md`; to change one, change the runtime. Where every part of a page comes from, the rules, and how to
add a command: [BUILDING_THE_REFERENCE.md](BUILDING_THE_REFERENCE.md).

To preview docstrings that are not released yet, copy the runtime's working tree instead:

```bash
.venv/bin/python tools/sync_runtime.py --worktree   # api_src/ from the working tree, for a local preview only
```

That copy is marked as a preview. `--check` reports it, and the build check fails on it, so it cannot be published.
Run the tool without `--worktree` before you commit.

### When the runtime releases a new version

1. **A patch release, for example 0.9.1:** set `runtime.tag` to `v0.9.1` and run `tools/sync_runtime.py`. Commit
   and push. The `0.9` version is published again with the new generated pages.
2. **A minor or major release, for example 0.10.0:**
   1. Set `docs_version` to `"0.10"` and `runtime.tag` to `v0.10.0`, then run `tools/sync_runtime.py`.
   2. Update the software guides for what changed, using the release's changelog section, and give each changed
      guide a new revision letter in `versions.yml`, with a line in its About page's *Document history*.
   3. Commit and push. The site publishes `0.10`, "latest" moves to it, and `0.9` stays as it was.

### When a manual is revised

Give it the next revision letter in `versions.yml`, for example `2026.A` to `2026.B`, and add a line to the
*Document history* on its About page saying what changed. When the revision is published, set `status: published`
and `published:` to the date.

### Publishing

`.github/workflows/publish.yml` publishes on every push to `main`. It runs a strict build first, then
`mike deploy` for `docs_version` with the alias `latest`. In the repository's Settings, under Pages, the source must
be "Deploy from a branch", branch `gh-pages`, folder `/ (root)`. Every push and pull request also runs
`tools/test_tools.py` and a strict build (`.github/workflows/build.yml`).

To preview the published versions locally, with the version selector, run `.venv/bin/mike serve`.

Which runtime, firmware and hardware versions work together is on the site's *Versions & compatibility* page.

## Contributing

A small fix can be made from the browser: every page ends with a link that opens it for editing on GitHub. For
anything larger, open an issue first, then a pull request. The *Contributing* page on the site has the house rules.

Questions about the robot itself go to the issue tracker of the repository it concerns, for example
[RCB-Runtime](https://github.com/Source-Robotics/RCB-Runtime) for the robot's software.

## License

- **Text and images:** [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/),
  see [LICENSE](LICENSE). You may copy, adapt and share them, also commercially, if you credit Source Robotics and
  share your changes under the same license.
- **Code:** the [MIT license](LICENSE-CODE). This covers the code examples in the pages and the site's own code, so
  you can use an example in your own program without other conditions.
- **Names and logos:** the Source Robotics name, the product names and the logos are not covered by either license.

By contributing you agree that your contribution is published under these licenses.
