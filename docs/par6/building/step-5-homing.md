---
status: new
---

# Step 5: The first homing

Stage 4 of [the first-run check](first-run-check.md) runs the robot's normal homing on your build and explains a failure in a builder's terms. Each joint moves slowly to its mechanical endstop to find its position reference, and then the arm moves to its start pose: about half a minute in all. A gripper on CAN is calibrated as part of the homing. The speeds and currents are those of the robot's homing sequence, not values of the check. Every move that needs a position reference, stage 5 and every program included, needs a homed arm. When the homing fails, the check shows the robot's own reason and, for that kind of failure, what a builder checks first.

!!! danger "Danger"
    Every joint drives to the end of its travel, and the arm then swings to its start pose.

    A hand, a cable or a tool near a joint's endstop or in the arm's path can be caught or struck.

    - Clear the space around the arm and keep a hand on the E-stop, as the check asks before the homing starts.
    - Keep your hands off the arm and away from the gripper's jaws until the homing has ended.
    - **Skip**, Ctrl-C and **Stop the run** stop the homing (the robot leaves homing for IDLE, and the arm is then not homed), but they are not emergency stops. To stop the arm at once, press the E-stop or **Disable** in the dashboard.

**Prerequisites**

- Step 4 done without a FAIL (the powered test moves, or the by-hand variant).
- The arm ENABLED. When it is DISABLED, the check asks *The arm is DISABLED. Clear the space around it, then press Enable in the dashboard (it holds where it is; nothing moves yet) — waiting for the arm to be enabled* and waits up to 180 s; after that the step is skipped. It never enables the arm itself.
- The robot in IDLE: no error latched (clear errors first) and no other mode.
- The arm at or near its park pose, nothing in the way and no cable that can catch. A joint that starts far from its endstop can fail to reach it in time (see [Troubleshooting](#troubleshooting)).
- A gripper on CAN powered, with nothing between its jaws.
- Control of the robot free. The check takes control before the homing; the dashboard keeps it for 5 s after your last click there (the Enable click too), and the check waits up to 15 s for it.

## Procedure

**In the dashboard:** open the **First run** tab, tick **4 Homing** (untick the stages you do not want to run) and press **Start**.

**In a terminal** on the robot's Raspberry Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 4
```

Without stage 0 in the list, stage 0's configuration and robot-service checks still run first: this stage needs them.

The stage begins with *Stage 4: Homing* and the line *The arm ENABLED: the normal homing, each joint to its endstop; a failure is explained with what to check.* Then:

1. If the arm is DISABLED, the check waits up to 180 s for you to press **Enable** (see Prerequisites).
2. If the robot is not in IDLE, the step ends with a SKIP and nothing moves.
3. The check asks one of two questions:
    - Not homed yet: *The arm homes now: each joint moves slowly to its endstop, then to its start pose (about half a minute). Clear the space around the arm and keep a hand on the E-stop.*
    - Homed already: *The arm is homed already. Home it again? Each joint moves slowly to its endstop, then to its start pose (about half a minute).*

    Answer **home** to go on, or **skip**: nothing moves, and the result is a SKIP (not homed: stage 5 then has no homed arm) or an INFO (homed already).

4. The check takes control of the robot. If the dashboard still holds it, the check shows *Another client holds control — the dashboard lets go 5 s after its last click; waiting for it* and waits up to 15 s.
5. The check notes the errors already latched (only errors that latch from now on count) and starts the homing. If the robot refuses it, the step ends with a SKIP giving the robot's reason.
6. The arm homes while the check shows *Homing — each joint to its endstop, then the start pose*. The check waits up to 180 s in all. The robot must enter homing within 5 s; the wait ends when it leaves homing. Skip (Ctrl-C) stops the homing: the robot leaves homing for IDLE, the arm is not homed, and the step is a SKIP. After 180 s the check stops the homing the same way, and the step is a FAIL.
7. The results appear: a PASS with the time it took, or one FAIL per homing failure with the robot's reason and what to check.
8. If the stage has a FAIL and stage 5 is in the run, the check asks *Stage 4 has a FAIL — fix it first (the hints say what to check). Go on to stage 5 anyway?* — **no** ends the run, **yes** goes on (stage 5 then skips its steps on an arm that is not homed).

After a failed homing the robot keeps the error latched, and the arm is not homed. The error's own advice (the robot's error list) for a failed joint is: *Move the arm to its park pose by hand and check that nothing is in the way. Clear errors, enable and home again. After a deliberate mechanical change, accept the new reference in System Info, Arms (homing).* For the gripper: *Check that the jaws move freely and the gripper is powered. Clear errors, enable and home again.*

!!! note "Note"
    Run the check on the robot's Raspberry Pi. The robot's reason for a failure is read from the Pi's shared memory; from another computer (`--host`) the FAIL line shows only the joint and the error's title, for example *J3: Joint homing failed*, and the hints fall back to the general one.

## What each check looks at

### Homing `S4.home`

**When it passes.** The robot was seen in HOMING, then left it, and is now in IDLE and homed, with no new homing error. Seeing HOMING matters: an arm homed before reads IDLE and homed even when the homing never ran, so that alone is no PASS.

**Timing.** The check reads the robot's state every 0.2 s. The robot must enter HOMING within **5 s** of the command, and the whole wait lasts at most **180 s**; a homing still running then is stopped (`stop`), as is one you skip. The check measures the time from the command to the end of the wait.

**The errors.** After the homing the check compares the robot's error list with the one from before the homing. Every new error whose key ends in `HOMING_FAILED` (`J<n>:HOMING_FAILED` for a joint), `GRIPPER_HOMING_FAILED` or `HOMING_ABORTED` is one FAIL. Its line is the robot's own description of the error, which carries the reason, with the joint from the error's key in front when the key names one, for example *J3: Joint homing failed: the two passes stopped 410 ticks apart (max 200) — … (4002 HOMING_FAILED)*. The gripper's key names no joint: its line starts with *Gripper homing failed*. Without a description, the line is the error's title.

**The hints** for each FAIL are chosen by the words of that reason (case ignored; the first kind in the [table of failure kinds](#homing-failure-kinds) that matches wins), else by the key (`HOMING_ABORTED`), else the general hint. The general hint is always added after the others, once.

**Other errors.** Errors that latched during the homing but are not homing errors are listed in one INFO next to the homing FAILs. When there is no homing error at all but other errors latched, each of them is a FAIL with the general hints. When nothing latched and the arm is still not homed, the result is one FAIL naming the mode the robot ended in, with the hints for an interrupted homing. This is what an interrupted homing looks like: a Stop, **Disable** or a mode change ends the homing without latching an error (the robot writes `HOMING_ABORTED` only to its activity log, not to the error list).

## Expected results

A correctly built PAR6 gives one line:

- **PASS** `homed in <took> s` — `<took>` about 30 (the line is just `homed` when it took under 1 s).

## Troubleshooting

In the tables, `<mode>` is the robot's mode, `<reason>` the robot's own words and `<took>` the time the homing took in seconds.

### Homing `S4.home`

| Result | What it means | What to check |
|---|---|---|
| **PASS** `homed in <took> s` | The robot homed: it entered and left homing, ended in IDLE and homed, with no new homing error. `homed` alone when it took under 1 s. | — |
| **FAIL** `<joint>: <the robot's description of the error>` | A homing error latched (`J<n>:HOMING_FAILED`, `GRIPPER_HOMING_FAILED` or `HOMING_ABORTED`); one line per error. `<joint>: ` is in front when the error's key names a joint, for example `J3: Joint homing failed: … (4002 HOMING_FAILED)`. When no homing error latched but other errors did (for example the E-stop, or a drive's fault), each of those is a line of its own, usually with the general hint only. | The hints of its kind in [Homing failure kinds](#homing-failure-kinds), then, once: logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]') |
| **INFO** `also latched while homing: <keys>` | Next to a homing FAIL: other errors that latched during the homing, by key. Another error can be what stopped the homing. | The dashboard's Errors tab names them. |
| **FAIL** `homing ended in <mode>, not homed` | The homing ended with no new error, and the arm is not homed: it was interrupted by a Stop, **Disable** or a mode change, which end the homing and leave the arm not homed without latching an error. (The E-stop latches an error: that error is then the FAIL line.) | the homing was interrupted — Stop, Disable, the E-stop or a mode change ends it, and the arm is then not homed: home it again<br>an error ended it: the dashboard's Errors tab names it<br>logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]') |
| **FAIL** `homing never started (the robot stayed in <mode>)` | The robot accepted the command but did not enter HOMING within 5 s, and no homing error latched. | logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]') |
| **FAIL** `homing did not end within 180 s (stopped)` | The robot was still homing 180 s after the command. The check stopped the homing: the robot left homing for IDLE, and the arm is not homed. | logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]') |
| **SKIP** `skipped by the user: the homing was stopped, the arm is not homed` | You skipped (Skip, Ctrl-C, or **Stop the run**) while the arm homed. The check stopped the homing: the robot left homing for IDLE, and the arm is not homed. | Home again when you are ready: run stage 4 again. |
| **INFO** `already homed (not homed again)` | The arm was homed and you answered **skip** to *Home it again?* | — |
| **SKIP** `not homed (the user's choice): stage 5 needs a homed arm` | The arm was not homed and you answered **skip**. Stage 5 will skip its steps. | — |
| **SKIP** `the robot refused to home: <reason>` | The robot refused the homing, so nothing moved. Homing is allowed only in IDLE with the arm ENABLED. | Read `<reason>`; clear the errors, enable the arm and run stage 4 again. |
| **SKIP** `needs IDLE (the robot is in <mode>: clear its errors first)` | The robot was not in IDLE when the step began, for example in ACTIVE_ERROR after a failed homing. Nothing moved. | Clear the errors in the dashboard, then run stage 4 again. |
| **SKIP** `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | Another client still held control of the robot after 15 s. Nothing moved. | Wait 5 s after your last click in the dashboard, or release control there, then run stage 4 again. |
| **SKIP** `the arm stayed disabled (this step needs it enabled)` | The arm was not enabled within 180 s. Nothing moved. | Press **Enable** in the dashboard while the check waits. |
| **SKIP** `no connection to the robot (S0's 'Robot service' step)` | The check has no connection to the robot. | The robot service step of stage 0 (Step 1). |
| **SKIP** `skipped by the user` | You skipped the wait for **Enable** or the wait for control. Nothing moved. | — |
| **SKIP** `skipped by the user (Ctrl-C)` | In the terminal: Ctrl-C while the check was working on its own, outside a wait or a question (for example while it sent the homing command). | Check the robot's state in the dashboard before going on. |
| **SKIP** `the run was stopped here` | The run was stopped (**Stop the run**, or Ctrl-C at a question). | — |
| **FAIL** `the check itself failed: <error>` | The check's own code failed. The report holds its traceback. | this is a fault of the check, not necessarily of the robot — send the report |

### Homing failure kinds

The check sorts each homing FAIL by the words of the robot's reason, in this order; the first kind that matches gives the hints. The middle column shows what the robot's reason says for that kind, as the homing code writes it (fields in `<>`). Every row's hints are followed, once, by the general hint *logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]')*.

| Kind | Selected by the words | What the robot's reason says | What to check |
|---|---|---|---|
| The endstop was not reached | `did not reach its endstop`, `timeout (` | *timeout (`<s>` s / `<ticks>` ticks) — check homing_direction and wiring*<br>*it did not reach its endstop within `<s>` s of its controlled approach (`<speed>` ticks/s, `<current>` mA) — something in the way, or the joint far from its endstop* | the joint started far from its endstop: move the arm to its park pose by hand before homing<br>something in the way, or a cable caught<br>the joint homes the wrong way: its direction in the robot's homing sequence<br>a Hall-sensor joint: the sensor's cable and its magnet (stage 2 checks the sensor) |
| The Hall sensor stays triggered | `Hall sensor still triggered` | *the Hall sensor still triggered right after backing off `<n>` times — check the sensor and its magnet* | the Hall sensor stays triggered: the magnet too close, or the sensor's output shorted (stage 2 checks it) |
| The two passes disagree | `passes stopped`, `ticks apart` | *the two passes stopped `<n>` ticks apart (max `<max>`) — the endstop trigger is not repeatable (a false stall: the joint could not move, or something blocked it?)* | the joint stopped at two different places on its two passes: a loose or flexible endstop<br>a coupling or belt that slips (stage 3 checks the coupling)<br>a cable or part that sometimes catches before the endstop |
| The approach stopped short (the arm check) | `controlled approach stopped` | *its controlled approach stopped `<deg>` deg short of where it always stops on arm `<arm>` — something in the way (the arm against itself or its base?), or the joint could not carry the arm there. …* (or *short of where its endstop always is*) | something in the way before the endstop: the arm against itself or its base, a cable<br>the joint could not carry the arm there: move the arm to its park pose and home again |
| It homed away from where this arm always homes (the arm check) | `always homes` | *it homed `<deg>` deg from where arm `<arm>` always homes — checked as soon as it homed: a false stall (could it move? was it at its park pose? something in the way?), a skipped belt or a slipping coupling. …*<br>*it homed `<deg>` deg from where this arm always homes — …* | after a deliberate mechanical change (a new belt, the joint taken apart): accept the new reference in the dashboard's System Info, Arms (homing)<br>otherwise: a belt that skipped, a coupling that slipped, or a false stall — start from the park pose |
| No known arm matches (the arm check) | `known arm` | *it homed where no known arm's `<joints>` homes (closest: `<arm>`, `<offsets>`) — a false stall (could it move from where it was? the arm touching itself or something?), or a different arm. …*<br>*it homed `<deg>` deg from where the closest known arm's J`<n>` homes — no known arm matches (closest: `<arm>`, `<offsets>`) — false stalls, or a different arm: …* | a false stall: a joint stopped before its endstop — could it move from where it was? Move the arm to its park pose and home again<br>a different arm on this controller: the dashboard's System Info, Arms (homing), 'Learn a new arm on the next homing' |
| A false stall | `during its release`, `false stall` | *it slid `<n>` ticks during its release (more than `<max>`, twice its two-pass tolerance) — it was not resting on an endstop: a false stall (could it carry the arm from where it was?)* | the joint stalled before its endstop: something stiff (a tight belt, a cable), or a load the homing current cannot move — start from the park pose<br>the joint's homing current in the robot's homing sequence |
| No position was read | `never read valid`, `no position was read`, `without a home reference` | *its position never read valid at the endstop — no home reference*<br>*no position was read on the way to the endstop (pass 1) — the two passes cannot be compared*<br>*it completed without a home reference (no valid position read at the endstop)* | the drive read no position: its encoder (the magnet on the motor shaft, the drive's encoder setting)<br>the CAN connection to that drive (stage 1 checks it) |
| The gripper did not calibrate | `firmware calibration`, `no endstop` | *its firmware calibration did not finish within `<s>` s — check that the jaws can move freely and the gripper is powered*<br>*its driver object cannot send a firmware calibration* | the gripper's jaws move freely, nothing between them<br>the gripper's power and its CAN cable (stage 1 checks it answers) |
| Homing aborted | none of the words above, and the error's key ends in `HOMING_ABORTED` | — (the robot writes `HOMING_ABORTED` only to its activity log, not to its error list: this row matters only if the robot ever latches it; an interrupted homing shows as `homing ended in <mode>, not homed`) | the homing was interrupted — Stop, Disable, the E-stop or a mode change ends it, and the arm is then not homed: home it again<br>an error ended it: the dashboard's Errors tab names it |
| Anything else | none of the above | for example *it failed (see RTI.log)* | logs/RTI.log has each joint's homing steps (search for the joint, e.g. 'J3 [CANID 2]') (once) |

The texts marked `…` go on with the arm check's advice: *Move the arm to its park pose and home again*, and either *after a deliberate mechanical change: System Info > 'Arms (homing)' > 'Accept as new reference'* or *a different arm: System Info > 'Arms (homing)' > 'Learn a new arm on the next homing'*.

## What's next

Continue with [Step 6: The homed arm](step-6-homed-arm.md).
