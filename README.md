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

## Versions

Each release of the robot's runtime has its own version of the documentation. The version selector in the site's
header switches between them. The versions are built with [mike](https://github.com/jimporter/mike) and kept in the
`gh-pages` branch. Which runtime, firmware and hardware versions work together is on the site's
*Versions & compatibility* page.

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
