# Tabs and tables

## Content tabs

=== "Dashboard"

    Press **Home** in the control row. The status bar shows *HOMING* until every joint has its reference.

=== "Python"

    ```python
    robot.home(wait=True)
    ```

=== "Blocks"

    There is no homing block: a program refuses to start on an unhomed arm.

```markdown
=== "Dashboard"

    Press **Home** in the control row.

=== "Python"

    ```python
    robot.home(wait=True)
    ```

=== "Blocks"

    There is no homing block.
```

Tabs with the **same labels are linked** across a page (`content.tabs.link`): choose *Python* once and every
tab group on the page switches to Python. Try it on the second group:

=== "Dashboard"

    Press **Enable**.

=== "Python"

    ```python
    robot.enable(wait=True)
    ```

=== "Blocks"

    A program never enables the arm itself.

## Tabs inside an admonition

!!! example "The same move, three ways"

    === "Joint space"

        ```python
        robot.move_joints(0, -60, 60, 0, 0, 0)
        ```

    === "Cartesian"

        ```python
        robot.move_linear(300, 0, 250, 180, 0, 90)
        ```

## Tables

| Joint | Range (deg) | Velocity limit (deg/s) | Reference |
|:-----:|:-----------:|-----------------------:|:----------|
| J1 | −140 … 140 | 172 | endstop |
| J2 | −130 … 10 | 120 | endstop |
| J3 | 114 … 376 | 150 | endstop |
| J6 | −49 … 409 | 230 | Hall sensor |

```markdown
| Joint | Range (deg) | Velocity limit (deg/s) | Reference |
|:-----:|:-----------:|-----------------------:|:----------|
| J1 | −140 … 140 | 172 | endstop |
```

The colons set the alignment: `:---` left, `:---:` centre, `---:` right. **Click a header to sort** (every plain
table is sortable; the values above are examples, not the specification).

## Icons, code and marks in cells

| Check | Result | Fix |
|---|---|---|
| Every drive answers | :material-check-circle:{ .sr-green } PASS | — |
| Supply voltage | :material-alert:{ .sr-amber } WARN, 21.2 V | check the supply under load |
| E-stop channel 2 | :material-close-circle:{ .sr-red } FAIL | wire the second pair, see `pin_map` |
| Firmware | `103` on every drive | update to `109` |

```markdown
| Check | Result | Fix |
|---|---|---|
| Every drive answers | :material-check-circle:{ .sr-green } PASS | — |
| Firmware | `103` on every drive | update to `109` |
```

## A wide table scrolls

| Runtime | Client | TCP protocol | RTI protocol | Telemetry format | Drive firmware | Control box PCB | Description package | OS image | Manuals |
|---|---|---|---|---|---|---|---|---|---|
| 1.0.0 | 1.0.x | 1 | 2 | 1 | 103–109 | v1, v2 | ≥ 2.0 | 24.04.2 rt11 | PM 1.0, OM 1.0, UM 2026.A |
| 1.1.0 | 1.1.x | 1 | 2 | 1 | 105–110 | v2 | ≥ 2.1 | 24.04.2 rt11 | PM 1.1, OM 1.1, UM 2026.B |

## Lists inside cells

| Mode | Needs | Leaves to |
|---|---|---|
| EXEC | ENABLED, HOMED | IDLE on `stop`, ACTIVE_ERROR on a fault |
| RTI | ENABLED, HOMED, a paired PC | IDLE on `rti_release`, ACTIVE_ERROR on a lost link |

Tables cannot hold bullet lists in Markdown; for multi-line cells use `<br>` or move the content into a
definition list below the table.
