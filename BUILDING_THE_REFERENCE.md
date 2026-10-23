# How the command reference is built

The Programming Guide's command reference has **one page per command** of the Python client (`RobotClient`), grouped
by topic, with an overview page per group and one **Per-move settings** page. These pages are generated, not
written by hand: the same facts that run the robot produce its documentation, so the two cannot drift apart.

This file says where every part of a command page comes from, which rules apply, and what to do when something
changes. It applies to people and AI assistants alike.

## The pipeline

```text
RCB-Runtime (the code)                         this repository
──────────────────────                         ───────────────
robotclient/*.py docstrings  ──┐
communication/protocol.py      │   tools/sync_runtime.py      api_src/             hooks/command_pages.py
utility/error_catalog.py       ├── from a release TAG ──────► (a copy, plus  ───► one page per command,
motion/exec_commands.py        │   (or --worktree to          runtime_facts.json)  the overview tables and
command_executor.py          ──┘    preview)                                       the Per-move settings page
                                                              docs/includes/per_move_settings.yml ──┘
                                                              docs/includes/command_extras/<command>.md ──┘
```

1. **The runtime's docstrings** are written to `docstrings_guide.md` in RCB-Runtime (Google style, imperative
   summary, every parameter with its unit, plus this project's own `Defaults:`, `Errors:` and `See also:` sections).
   The runtime's test `test_docstrings` checks them.
2. **`tools/sync_runtime.py`** copies, from the runtime's release tag set in `versions.yml`:
   - the `robotclient` package and `communication/protocol.py` (the robot's command rules) into `api_src/`;
   - `utility/error_catalog.py` (every code's number and title);
   - `runtime_facts.json`, computed from the runtime's code: every per-move setting the robot accepts and the ones
     it refuses per move, every value of every choice with its other accepted spellings, and every code the robot
     can refuse a queued command with when it is sent.

   `--worktree` copies the runtime's working tree instead, to preview docstrings not released yet. That copy is
   marked in `api_src/SOURCE.txt`; `--check` and the build check refuse it, so it is never published.
3. **`hooks/command_pages.py`** (an MkDocs hook) builds the pages at every build from `api_src/`,
   `docs/includes/per_move_settings.yml` and, for a command that has one, `docs/includes/command_extras/<command>.md`.
   It also fills a group overview's command table (`<!-- command-overview: GROUP -->`) and its "Other names" table
   (`<!-- command-aliases: GROUP -->`) from the protocol's `COMMAND_ALIASES`: every old command name the robot still
   accepts, and the command it means.

## A command page, part by part

| Part | What it shows | Comes from |
|---|---|---|
| Title | The command's name | The client method |
| Facts strip | Queued or at once, the mode, enabled, homed, control | The robot's command rules |
| Description | The summary and text, command names linked to their pages | The docstring |
| Syntax | The call, with real default values | The function signature |
| Arguments | Name, type, default, description. `**options` lists every per-move setting with its default, each linked to the Per-move settings page | The signature, the docstring, the settings file, the robot's list of settings |
| Figure | Only where one helps | `command_extras/<command>.md` |
| Default values | Only for commands that change a default | The docstring's `Defaults:` |
| Returns | The type and what the value means | The signature and the docstring |
| Examples | Always, as a script without `>>>` prompts | The docstring's `Examples:` |
| Further details | A note or a warning | The docstring's `Note:` / `Warning:` |
| Usage restrictions | Collapsed. When the robot accepts the command, every code it can be refused or fail with (each linked to the error codes page), and one line on the Python exceptions | The command rules, the executor's replies, the docstring's `Errors:` and `Raises:`, the error catalog |
| Protocol | The JSON line a client that does not use `robotclient` sends | The example run against the real client from `api_src/`, with a transport that keeps the message (its packing, defaults and unit conversion exactly); `get_pose()` answers a reference pose the page states |
| See also | Related commands and the Per-move settings page | The commands the docstring names, its `See also:` |

The parts appear in this order on every page. The layout is decided; change it only with the project owner. Its look
(the plain table, the left-aligned figure with a small caption, the orange collapsed box, the setting links) is in
`docs/stylesheets/extra.css`, in rules that apply only to command pages (`h1.cmd-title`), so the manuals keep the
theme's own look.

## Colours

Four colours, each with one meaning:

| Colour | Means | Used for |
|---|---|---|
| **Blue** (the theme's link colour) | Takes you elsewhere | Setting links, error codes, See also, cross-references |
| **Green** (the accent) | Status, or part of a drawing | The facts strip's "Queued", a figure's path and markers |
| **Orange** | Restrictions and warnings | The Usage restrictions box, warning boxes |
| **Grey** | Secondary detail | A default beside a setting, the code count, captions |

A link is always blue and blue is always a link (the theme's note boxes may stay blue: they are boxes, not text).
Colour is never the only signal: every coloured element also says what it means in words. A new colour needs a
meaning none of the four covers, and goes into this table first. Check every colour in light and dark mode.

## Rules

- **Document everything.** Every parameter, every per-move setting, every value of a choice, every code a command
  can produce. Never a subset. Where a setting has no effect on a command, its docstring says so.
- **Facts come from the code.** The lists of settings, values, refusal codes and code numbers are read from the
  runtime, never typed here. The only hand-written facts are the descriptions in `per_move_settings.yml` and the
  extras; each was checked against the code that decides it, and must be again when that code changes.
- **No hand edits of generated content.** To change a command page, change the runtime's docstring (or the settings
  file, or an extras file), release, sync.
- **No other robot makers' names** anywhere in this repository.

## What the build check tests

`tools/test_tools.py` (run on every push) fails when:

- the settings file misses a setting the robot accepts, has one it does not, or misses a description for a value
  of a choice;
- a page's Usage restrictions does not list exactly the robot's refusals, the command's own `Errors:`, the failures
  every queued command shares and the ways a running move ends;
- a generated page is missing from the navigation, or an overview names a method the client does not have;
- `api_src/` is a working-tree preview instead of a release's copy.

The strict build (`mkdocs build --strict`) fails on any broken link or anchor, so every code and setting link is
checked too.

## Adding a command's page

1. In RCB-Runtime, write the command's docstring to `docstrings_guide.md`, including `Errors:` for a queued command
   (find every code in the planner's path for it) and `See also:`. Add its group to `DOCUMENTED` in
   `test_docstrings` and run it.
2. Here, preview it: `tools/sync_runtime.py --worktree`, then add the command to `PAGES` in
   `hooks/command_pages.py` and its page to the navigation in `mkdocs.yml`.
3. If a figure helps, add `docs/includes/command_extras/<command>.md`.
4. Build with `--strict` and run `tools/test_tools.py`.
5. Before committing here: release the runtime, set `runtime.tag`, run `tools/sync_runtime.py` without
   `--worktree`.

## When the runtime changes

- **A new per-move setting, or a new value of a choice:** the build check fails until `per_move_settings.yml`
  describes it.
- **A new refusal code in the executor:** it appears on every queued command's page by itself; check that the page
  still reads well.
- **A new failure in a command's planning:** add it to that command's `Errors:` docstring section.
- **A renamed or new command:** update `PAGES`, `GROUPS` and the navigation. A renamed command keeps its old name
  in the runtime: a Python alias (the same function), an entry in `COMMAND_ALIASES` (the robot accepts the old ID)
  and one in the client's `WIRE_NAMES_BEFORE_RENAME` (the client sends an older robot the old ID). The "Other names"
  table then lists it by itself.
