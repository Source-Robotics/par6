---
title: Page and site features
description: Front matter a page can carry, and the theme features that are on, off, or need a plugin.
icon: material/flask
status: new
tags:
  - devlab
  - example
---

# Page and site features

## What this page's front matter does

```yaml
---
title: Page and site features          # the title in the sidebar and the browser tab
description: ...                       # the meta description (search engines, social cards)
icon: material/flask                   # an icon before the title in the sidebar
status: new                            # a marker in the sidebar: new / deprecated / draft (extra.status)
tags: [devlab, example]                # shown under the title; the tags plugin
---
```

Other keys a page can carry:

```yaml
hide:
  - navigation        # no left sidebar on this page (a wide table, a landing page)
  - toc               # no right sidebar
search:
  boost: 2            # rank this page higher in search results
  exclude: true       # or keep it out of search entirely
template: custom.html # a different page template from overrides/
```

## Theme features: on, available, needs a plugin

| Feature | State | Note |
|---|---|---|
| tabs as documents, bold sidebar groups, chapter index pages | on | `navigation.tabs`, `.sections`, `.indexes` |
| Previous / Next, back-to-top, breadcrumbs | on | `navigation.footer`, `.top`, `.path` |
| search with suggestions, highlighting, share link | on | |
| code copy button, code annotations | on | |
| view / edit this page actions | on | plus the custom edit / report line |
| tooltips on abbreviations, links with a title, footnotes | on | |
| announcement bar, dismissable | on | the block in `overrides/main.html` |
| version selector + older-version banner | on | `mike`; only on the versioned preview |
| language selector | on | one language today |
| repository card per document | on | custom partial |
| light / dark toggle | on | |
| page status markers, tags | on | this page |
| image zoom | on | `glightbox` plugin |
| sortable tables | on | a 1 kB script |
| **instant navigation** (no full page load between pages) | available | `navigation.instant`; needs a check of the inline header scripts first |
| expand all sidebar sections / prune the sidebar | available | `navigation.expand`, `navigation.prune` |
| hide the header when scrolling down | available | `header.autohide` |
| table of contents inside the left sidebar | available | `toc.integrate` |
| cookie consent | available | `extra.consent` |
| "Was this page helpful?" feedback widget | available | needs an analytics provider (`extra.analytics`) |
| comments under a page | available | giscus (GitHub discussions) in a partial |
| social preview cards | CI only | `ENABLE_SOCIAL=1` with the imaging extras |
| blog, offline build, privacy (self-host external assets), image optimisation | available | built-in plugins, not enabled |
| generated API reference from docstrings | needs plugin | `mkdocstrings[python]` |
| one metadata file for every landing page | needs plugin | `mkdocs-macros-plugin` |
| last-updated line from git | needs plugin | `git-revision-date-localized` |
| PDF per manual | needs plugin | `mkdocs-exporter` or `mkdocs-with-pdf` |
| redirects for moved pages | needs plugin | `mkdocs-redirects` |

## Typeset titles

Material renders Markdown inside headings, so a heading can carry code or an icon:

### `move_joints` — the queued joint move

### :material-alert: Hazard headings read differently

```markdown
### `move_joints` — the queued joint move
### :material-alert: Hazard headings read differently
```

## Linking

Relative links between pages, with anchors to headings: [the twelve admonition types](admonitions.md#the-twelve-types).
A broken link fails the strict build, so links cannot rot silently.

```markdown
[the twelve admonition types](admonitions.md#the-twelve-types)
```
