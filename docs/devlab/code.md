# Code blocks

Every block has a copy button. Line numbers, highlighted lines, titles and annotations are per block.

## Title, line numbers, highlighted lines

```python title="first_move.py" linenums="1" hl_lines="6 7"
from robotclient import RobotClient

robot = RobotClient()
robot.connect("192.168.0.84")
robot.enable(wait=True)
robot.home(wait=True)
robot.enter_exec_mode(wait=True)
robot.move_joints(0, -60, 60, 0, 0, 0, speed=20)
```

````markdown
```python title="first_move.py" linenums="1" hl_lines="6 7"
from robotclient import RobotClient
...
```
````

## Annotations (numbered markers with a popup)

```python
robot.move_joints(0, -60, 60, 0, 0, 0, speed=20)  # (1)!
robot.wait_motion_complete()  # (2)!
```

1.  Degrees. `speed` is a percent of the velocity limit.
2.  Waits for *this* command, not for the whole queue; `wait_idle()` waits for the queue.

````markdown
```python
robot.move_joints(0, -60, 60, 0, 0, 0, speed=20)  # (1)!
robot.wait_motion_complete()  # (2)!
```

1.  Degrees. `speed` is a percent of the velocity limit.
2.  Waits for *this* command, not for the whole queue.
````

The `!` after the marker hides the comment itself; without it the `# (1)` stays visible.

## Inline code with highlighting

Call `#!python robot.home(wait=True)` before `#!python robot.enter_exec_mode()`; the wire form is
`#!json {"cmd": "home", "wait": true}`.

```markdown
Call `#!python robot.home(wait=True)` before `#!python robot.enter_exec_mode()`; the wire form is
`#!json {"cmd": "home", "wait": true}`.
```

## Languages

```json title="one command on the wire"
{"cmd": "move_joints", "args": [0, -60, 60, 0, 0, 0], "speed": 0.2}
```

```console
$ cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 1
Stage 1: every drive answers ... PASS
```

```xml title="robots/PAR6.xml (excerpt)"
<joint id="0">
  <name>J1</name>
  <joint_velocity_limit>3.0</joint_velocity_limit>
  <software_joint_limit_negative>-2.44</software_joint_limit_negative>
</joint>
```

```yaml title="system.xml policy, as YAML for the example"
drive_watchdog_ms: 100
safety_monitor:
  collision: warn
```

```diff
- <max_payload_kg>0.75</max_payload_kg>
+ <max_payload_kg>0.4</max_payload_kg>
```

```text
plain text, no highlighting
```

## A file embedded from disk

The block below is the file `docs/includes/example.py`, pulled in at build time, so the manual never drifts from
the example that is actually run:

```python title="docs/includes/example.py"
--8<-- "example.py"
```

Source (the marker is written without the spaces: `-- 8< --`):

````markdown
```python title="docs/includes/example.py"
-- 8< -- "example.py"
```
````

The same marker outside a fence embeds Markdown: the symbol definitions on every About page are one file.

## Code in tabs

=== "Python"

    ```python
    robot.move_linear(300, 0, 250, 180, 0, 90)
    ```

=== "JSON over TCP"

    ```json
    {"cmd": "move_linear", "args": [300, 0, 250, 180, 0, 90]}
    ```

=== "Blocks"

    *move linear* block with the point `P1`.

````markdown
=== "Python"

    ```python
    robot.move_linear(300, 0, 250, 180, 0, 90)
    ```

=== "JSON over TCP"

    ```json
    {"cmd": "move_linear", "args": [300, 0, 250, 180, 0, 90]}
    ```
````
