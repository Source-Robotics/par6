# Contributing

The documentation, the runtime and the firmware are open source. This page says how a change gets in.

## The documentation

The source of these pages is a public repository (the card at the top right of every page). Two ways in:

**Small fix, from the browser.** Every page ends with *Edit it on GitHub*. GitHub forks the repository for you,
opens the page's Markdown, and turns your edit into a pull request.

**Larger change, locally.**

```bash
git clone https://github.com/Source-Robotics/PAR6-docs.git
cd PAR6-docs
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve        # http://127.0.0.1:8000/PAR6-docs/
```

Edit under `docs/`, check the page in the browser, open a pull request. The repository's build check must pass.

By contributing you agree that your text and images are published under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) and your code examples under the MIT license, the
licenses of the rest of the documentation.

House rules, so the manuals read as one voice:

- Each page belongs to one manual and one chapter; say one thing at one depth, and link the page that says the
  rest.
- Highlighted text uses the three kinds defined in every manual's *About* page: Note, Notice (damage), Danger (injury).
- Units on every number: degrees and millimetres in the API pages, the gripper's 0 to 255, seconds.
- Second person for procedures ("Press…"), third person for reference pages.
- Describe what the robot does; do not compare it with other manufacturers' products.
- A screenshot or figure carries a caption; a page that moves the arm opens with its preconditions.

## The runtime

Issues and pull requests: [Source-Robotics/RCB-Runtime](https://github.com/Source-Robotics/RCB-Runtime). Read
the repository's README first (the Pi setup, the Python version, the service) and the Developer reference in the
[Control Box Manual](../rcb/developer/architecture.md).

What a runtime change brings with it: a test that fails without it, the full test suite green, and the manual
page it affects updated in the same pull request. A change that moves the arm is tested on an arm before it is
merged.

## The firmware

The joint and gripper drive firmware have their own repositories; releases are flashed from the dashboard or the
command line. A firmware change needs a bench test on one drive before it goes on a robot.

## Hardware

Mechanical and electronic changes to the arm and the control box are discussed on the forum first; the CAD files
are linked from each manual's *Supplementary material*.
