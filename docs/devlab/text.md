# Text, lists and tooltips

## Emphasis and marks

Plain, *italic*, **bold**, ***both***, `inline code`, ==highlighted==, ^^inserted^^, ~~deleted~~,
H~2~O and x^2^ (subscript, superscript), a [link with a tooltip](https://source-robotics.com "Opens the website").

```markdown
Plain, *italic*, **bold**, ***both***, `inline code`, ==highlighted==, ^^inserted^^, ~~deleted~~,
H~2~O and x^2^ (subscript, superscript), a [link with a tooltip](https://source-robotics.com "Opens the website").
```

## Critic marks (reviewing text)

The payload limit is {--0.75 kg--}{++0.4 kg++}. The wrist {~~struggles~>vibrates~~} with 0.5 kg held sideways.
{==Measured on 2026-10-18.==}{>>Confirm after the J4/J5 retune.<<}

```markdown
The payload limit is {--0.75 kg--}{++0.4 kg++}. The wrist {~~struggles~>vibrates~~} with 0.5 kg held sideways.
{==Measured on 2026-10-18.==}{>>Confirm after the J4/J5 retune.<<}
```

## Keys and symbols

Press ++ctrl+alt+del++, then ++enter++. Jog with ++arrow-left++ / ++arrow-right++.
Symbols: (c) (tm) (r) 1/2 1st 2nd --> <-- <-> =/= +/-

```markdown
Press ++ctrl+alt+del++, then ++enter++. Jog with ++arrow-left++ / ++arrow-right++.
Symbols: (c) (tm) (r) 1/2 1st 2nd --> <-- <-> =/= +/-
```

## Abbreviations (tooltips)

Hover RTI, RCB, CAN, TRF or WRF anywhere on the site: a site-wide list in `docs/includes/abbreviations.md` is
appended to every page. A page can also define its own:

The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium

```markdown
The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium
```

## Footnotes

The drives report their firmware version at every start.[^1] Serial numbers are not unique yet.[^2]

[^1]: Shown in the dashboard's Motor tab and by `get_hardware`.
[^2]: Every drive reports serial number 1 until the firmware writes a real one.

```markdown
The drives report their firmware version at every start.[^1]

[^1]: Shown in the dashboard's Motor tab and by `get_hardware`.
```

Hover a footnote mark: the note appears as a tooltip (`content.footnote.tooltips`).

## Definition lists

`move_joints`
:   Queued joint move on a straight line in joint space.

`move_linear`
:   Queued Cartesian move; the tool follows a straight line.

```markdown
`move_joints`
:   Queued joint move on a straight line in joint space.
```

## Task lists

- [x] the arm is mounted
- [x] the E-stop is wired as a pair
- [ ] the first-run check passed
    - [ ] stage 1: every drive answers
    - [ ] stage 2: E-stop, buttons and I/O

```markdown
- [x] the arm is mounted
- [ ] the first-run check passed
    - [ ] stage 1: every drive answers
```

## Ordered and nested lists

1. Switch on the control box.
2. Wait for the front panel to show *IDLE*.
    1. The LED turns green.
    2. The dashboard shows `RTI: RUNNING`.
3. Press **Enable**, then **Home**.
    - J1 to J5 find their endstops.
    - J6 finds its Hall sensor.

## Emoji and icons

Emoji: :robot: :warning: :white_check_mark: :x: :tada:
Icons: :material-robot-industrial: :material-alert: :material-check-circle:{ .sr-green }
:material-close-circle:{ .sr-red } :material-clock-alert:{ .sr-amber } :fontawesome-brands-github:
:octicons-arrow-right-24: :simple-python: :simple-raspberrypi:

```markdown
Emoji: :robot: :warning: :white_check_mark: :x: :tada:
Icons: :material-robot-industrial: :material-check-circle:{ .sr-green } :material-close-circle:{ .sr-red }
:fontawesome-brands-github: :octicons-arrow-right-24: :simple-python: :simple-raspberrypi:
```

Any icon from Material Design, FontAwesome, Octicons and Simple Icons works (`:set-name:`); the colour classes
`sr-green`, `sr-red`, `sr-amber` are in `extra.css`.

## Buttons

[Open the dashboard](#){ .md-button }
[Report a problem](../support/report-a-problem.md){ .md-button .md-button--primary }
[:material-download: Download the models](../simulation/models.md){ .md-button }

```markdown
[Open the dashboard](#){ .md-button }
[Report a problem](../support/report-a-problem.md){ .md-button .md-button--primary }
[:material-download: Download the models](../simulation/models.md){ .md-button }
```

## Block quote and rule

> Read the user manual of your robot before this programming manual.

---

```markdown
> Read the user manual of your robot before this programming manual.

---
```
