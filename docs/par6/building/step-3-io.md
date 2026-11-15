---
status: new
---

# Step 3: E-stop, buttons, I/O and the Hall sensor

Stage 2 of [the first-run check](first-run-check.md) checks the control box's inputs and outputs with your help: you press and release the E-stop (the check confirms that the E-stop channels your control box version uses read pressed, that the robot latches the E-stop, and that it clears again), you give the box's buttons B1 and B2 a short press, you may switch each isolated input and watch each isolated output, and you turn the Hall-sensor joint by hand through its magnet. The E-stop matters most: when it is pressed, the robot latches an ESTOP error and the arm is disabled, so a wiring mistake there must be found before anything moves. No motor moves in this stage; the only motion is the joint you turn yourself. The drives must be powered and the arm DISABLED: every step of this stage waits for it.

**Prerequisites**

- [Step 1](step-1-control-box.md) and [Step 2](step-2-drives.md) passed. The control box version must be right: it decides which E-stop channels this stage reads.
- The drives powered: the Hall sensor is read through its joint's drive.
- The arm DISABLED. If it is enabled, each step asks you to press **Disable** and waits up to 180 s (see the Danger notice below).
- The dashboard's software E-stop (its **E-STOP** button) off. If it is on, the E-stop step asks you to switch it off and waits up to 60 s.
- Within your reach:
    - the E-stop;
    - the control box's buttons B1 and B2 (a build without them can skip each one);
    - for the isolated inputs (optional): a way to switch each one — a 24 V signal or a switch wired to it — on terminals 11 (input 1), 10 (input 2) and 9 (input 3), see the runtime's `docs/pin_map.md`;
    - for the isolated outputs (optional): something you can see on terminals 6 (output 1), 7 (output 2) and 8 (output 3) — a lamp, a relay, a meter — and nothing that moves;
    - the Hall-sensor joint, to turn it by hand (J6 on PAR6), and the gripper, to hold it.

!!! danger "Danger"
    When the arm is enabled, each step of this stage asks you to press **Disable** in the dashboard.

    An arm that is not supported can drop when it is disabled; the check never disables it itself for this reason.

    - Support the arm, or park it, before you press **Disable**.
    - Keep your hands out from under the arm while you disable it.

## Procedure

**In the dashboard:** open the **First run** tab. All six stages are ticked by default: leave only **2 E-stop, buttons, I/O, Hall sensor** ticked, then press **Start**. A question shows one button per answer; a wait shows what the check waits for, how long at most, and a **Skip** button.

**From a terminal** on the robot's Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 2
```

In the terminal a yes / no question takes `y`, `yes`, `n` or `no`; a question with several answers lists them as `[1] …`: type the number or the answer. **Ctrl-C while the check waits** skips; **Ctrl-C at a question** stops the run; Ctrl-C while a step works on its own (for example during the 2 s an output is on) skips that whole step.

When stage 0 is not part of the run, two of its steps run first, because this stage needs them: **The configuration loads** and **The robot service runs** (see [Step 1](step-1-control-box.md)). Their results are listed under the first stage of the run: stage 2 when you run it alone.

Then, before **each** of the five steps below: if the arm is ENABLED, the check says *The arm is ENABLED. Support it (or park it), then press Disable in the dashboard — waiting for the arm to be disabled* and waits up to 180 s. If the arm stays enabled, that step is skipped.

1. **The E-stop** (`S2.estop`). Skipping any of its waits skips the whole step.
    1. Only if the software E-stop is on: *The software E-stop (the dashboard's E-STOP button) is on — switch it off* — up to 60 s.
    2. Only if the E-stop already reads pressed: *The E-stop reads PRESSED — release it (turn or pull it to unlock)* — up to 60 s.
    3. *Press the E-stop now* — up to 60 s. Press it and keep it pressed.
    4. The check waits 0.5 s, then reads the E-stop channels again.
    5. *Waiting for the robot to latch the E-stop ...* — up to 1 s. Nothing to do.
    6. *Now release the E-stop* — up to 60 s. Turn or pull it to unlock it. If it is not seen released, the step ends here.
    7. The check sends the robot's Clear Errors command itself, then *Clearing the E-stop error ...* — up to 3 s. Nothing to do.
2. **The box's buttons** (`S2.buttons`). For B1, then B2:
    1. *Give the control box's button B1 a SHORT press (it only turns the screen's page; skip it if your box has no such button)* — up to 30 s. Skipping here skips only this button; the check goes on with B2.
    2. *... and release B1* — up to 30 s. Skipping here also skips only this button (its press was seen); the check goes on with B2.
3. **Isolated inputs (optional)** (`S2.inputs`). The question: *Test the isolated inputs? You need a way to switch each one (a 24 V signal or a switch wired to it, docs/pin_map.md); you can skip any input that has nothing wired to it.* **no** skips the step. **yes**: for input 1, 2 and 3 in turn:
    1. *Switch isolated input `<n>` (terminal `<terminal>`; it reads `<level>` now) — skip it if nothing is wired to it* — up to 45 s. `<level>` is the input's level when the wait starts, 0 or 1. Skipping here skips only this input.
    2. *Switch input `<n>` back* — up to 45 s. Skipping here also skips only this input (its change was seen); the check goes on with the next input.
4. **Isolated outputs (optional)** (`S2.outputs`). The question: *Test the isolated outputs? Each switches on for 2 s — have something on it you can see (a lamp, a relay, a meter), and nothing that moves; answer 'not wired' for one with nothing on it.* **no** skips the step. **yes**:
    1. The check takes control of the robot. If the dashboard holds control (it keeps it for 5 s after your last click there), the check says *Another client holds control — the dashboard lets go 5 s after its last click; waiting for it* and waits up to 15 s. Skipping this wait skips the whole step.
    2. For output 1, 2 and 3 in turn: the check switches the output on for 2 s, then back to the level it had before, and asks *Did output `<n>` (terminal `<terminal>`) switch on for ~2 s?* The answers:
        - **yes**: PASS for this output.
        - **no**: FAIL for this output.
        - **again**: the output switches on for 2 s once more and the question comes again — for an answer you gave by mistake, as often as you need.
        - **not wired**: SKIP for this output.
5. **The Hall sensor** (`S2.hall`). Only on a robot with a Hall-sensor joint, and only when the robot is in IDLE.
    1. The check takes control of the robot, as for the outputs (up to 15 s; skipping skips the whole step).
    2. It starts the Hall check: *Starting the Hall check ...* — up to 3 s. The joint goes limp.
    3. *`<joint>` is limp now (hold the gripper if its weight could turn it). Turn `<joint>` SLOWLY by hand through its magnet and a little past it* — up to 120 s. The wait ends by itself once the sensor has changed and changed back.
    4. The question: *Check that it triggers at the same place? Turn `<joint>` back past the magnet, then through it again the SAME way as before.* **no** ends the step. **yes**:
    5. *Turn `<joint>` back past the magnet, then through it again the same way* — up to 120 s. The wait ends by itself once the sensor has changed six times in all: twice on the first pass, twice on the way back, twice on the second pass.
    6. However the step ends, the check stops the Hall check and the joint holds again.

    Skipping any of this step's waits skips the whole step.
6. **Only when your run also includes later stages:** if stage 2 has a FAIL, the check asks *Stage 2 has a FAIL — fix it first (the hints say what to check). Go on to stage `<next stage>` anyway?* **yes** goes on, **no** ends the run. Ctrl-C (or **Stop the run**) at this question counts as no.
7. The run ends: the check writes its report and, with the support bundle set to *ask*, asks whether to add the support bundle (see [the first-run check](first-run-check.md#the-report-and-the-support-bundle)).

**Stop the run** in the dashboard skips the wait in progress and every wait after it — each gives the same result as **Skip** — and stops the run at the next question. The results the step had measured before that question are kept in the report.

!!! danger "Danger"
    Isolated outputs 1, 2 and 3 each switch on for 2 s — and again for every **again** you answer.

    Whatever is wired to them runs: a valve, a motor, a tool. Every output is switched before the question, so answering **not wired** afterwards does not stop it.

    - Disconnect anything that moves from the outputs before you answer **yes** to *Test the isolated outputs?*.
    - Put something on them you can see instead: a lamp, a relay, a meter.
    - Answer **no** to skip the outputs altogether.

!!! note "Note"
    During the Hall check the Hall-sensor joint makes no torque: its drive's current limit is set to 0.

    The gripper's weight can turn the joint by itself.

    - Hold the gripper while the joint is limp.
    - The joint holds again when the step ends, when the robot leaves IDLE or a mode change is requested, or after 2 minutes without the check renewing it. The check renews it when it starts, after the start and before the repeat.

## What each check looks at

The steps read the control box's inputs through `get_hardware` (without the CAN counters). The waits for a press, a release or a switch read them every 0.04 s; the two waits before the E-stop test (the software E-stop, an E-stop already pressed) every 0.1 s. The E-stop channels and the buttons are active low: level 0 means pressed.

### The E-stop

Step `S2.estop`. Reads E-stop channel 1 (terminals E2 + E4) and channel 2 (terminals E1 + E3), the dashboard's software E-stop, and the robot's latched errors. Which channels count follows the control box version from the configuration:

| PCB version | Channels that count | "Pressed" means |
|---|---|---|
| v1 | 1 | channel 1 reads pressed. Channel 2 is not used: on this board it always reads pressed (a layout fault), and the step reports it as INFO. |
| v2 | 1 and 2 | either channel reads pressed. 0.5 s after the press both must read pressed. |

**Pass rule** — all of these:

- the E-stop is seen pressed within 60 s of *Press the E-stop now*;
- with PCB v2: 0.5 s after the press, both channels read pressed;
- the robot latches its ESTOP error within 1 s;
- the E-stop is seen released within 60 s of *Now release the E-stop*.

The PASS can come with an INFO (PCB v1's channel 2) and a WARN (the ESTOP error did not clear within 3 s of the check's Clear Errors).

!!! note "Note"
    The E-stop step sends the robot's Clear Errors command itself, after you release the E-stop.

    You do not need to press **Clear Errors** in the dashboard after this step, unless the step warns that the error did not clear.

    - If it warns, press **Clear Errors**; if the error stays, an E-stop channel still reads pressed.

### The box's buttons

Step `S2.buttons`. Reads buttons B1 and B2, every 0.04 s: a short press lasts about 0.1-0.3 s.

**Pass rule, per button:** a press seen within 30 s, then the release within 30 s.

### Isolated inputs (optional)

Step `S2.inputs`. Inputs 1, 2 and 3 on terminals 11, 10 and 9. For each, the step notes the input's level when it starts on it (0 or 1).

**Pass rule, per input:** the level changes within 45 s, and returns to the starting level within the next 45 s.

### Isolated outputs (optional)

Step `S2.outputs`. Outputs 1, 2 and 3 on terminals 6, 7 and 8. For each, the step switches the output on (level 1) for 2 s, then back to the level it had just before. The step cannot see the result: it asks you.

An output that was already on before the step stays on throughout, so you see no change.

**Pass rule, per output:** you answer **yes**.

### The Hall sensor

Step `S2.hall`. The Hall-sensor joint is the first joint whose `<has_hall_sensor>` is 1 in the robot's file (J6 on PAR6). The step needs the robot in IDLE and control of the robot. It starts the robot's Hall check: the joint's drive gets a current limit of 0, so the joint makes no torque, and the robot reads the joint's Hall sensor every tick. The robot counts every change of the sensor's level and records the joint's angle (in degrees, as the robot reads it) at the last change to each level.

**Pass rule:**

- the Hall check has started on that joint within 3 s;
- the sensor changes at least twice (on at the magnet, and back after it) within 120 s.

**The repeat** (if you answer yes): at least six changes in all within the next 120 s. The step then compares the angle of the last change to level 0 on the first pass with the same angle after the second pass, both turned the same way. **PASS** within 2.0°, **WARN** above.

## Expected results

A correctly wired robot shows, after the two steps of stage 0 when they run first:

- PASS `The E-stop: pressed: read on <n> channel(s) and latched by the robot; released: clear` — `read on 1 channel` with PCB v1, `read on 2 channels` with PCB v2.
- With PCB v1 only: INFO `The E-stop: channel 2 reads pressed — not used on PCB v1`. This is normal for a v1 board.
- PASS `The box's buttons: button B1: pressed and released`
- PASS `The box's buttons: button B2: pressed and released`
- PASS `Isolated inputs (optional): input <n>: switches both ways` — for each input you tested.
- PASS `Isolated outputs (optional): output <n>: switched, seen by the user` — for each output you tested.
- PASS `The Hall sensor: the sensor changes at the magnet and back (<joint> at <angle> deg, <angle> deg)` — the joint's angles at the last change to level 0 and to level 1.
- PASS `The Hall sensor: triggered <difference> deg apart on the two passes` — when you did the repeat.

A button, input or output you skipped, or answered **not wired** for, shows as a SKIP: that is not a fault.

## Troubleshooting

The Result column shows what the check prints after the step's title. A WARN or FAIL is followed by what was expected (when the step says) and the hints, most likely first.

### The E-stop (`S2.estop`)

| Result | What it means | What to check |
|---|---|---|
| SKIP `the software E-stop stayed on` | The dashboard's software E-stop was on and was not switched off within 60 s. | Switch the software E-stop off in the dashboard, then run the stage again. |
| FAIL `the E-stop reads pressed and did not release` | The E-stop read pressed when the step started and was not seen released within 60 s. Expected: *released*. | the E-stop's two wires to the control box: E-Stop 1 is terminals E2 + E4 (E-Stop 2: E1 + E3, docs/pin_map.md)<br>the E-stop's contact type: the box expects a normally-CLOSED contact that OPENS when pressed<br>the E-stop button itself: a contact block not clipped on, or a broken contact<br>a wire broken anywhere in the E-stop circuit reads as pressed — that is on purpose |
| FAIL `pressing the E-stop changed nothing within 60 s` | No pressed E-stop was seen within 60 s of *Press the E-stop now*. Expected: *pressed*. | the E-stop's two wires to the control box: E-Stop 1 is terminals E2 + E4 (E-Stop 2: E1 + E3, docs/pin_map.md)<br>the E-stop's contact type: the box expects a normally-CLOSED contact that OPENS when pressed<br>the E-stop button itself: a contact block not clipped on, or a broken contact |
| FAIL `E-stop channel <n> does not read pressed (the other does)` | PCB v2 only: 0.5 s after the press, this channel did not read pressed. Expected: *both channels pressed*. | channel `<n>`'s wire or contact (a dual-channel E-stop has two separate contacts) |
| INFO `channel 2 reads pressed — not used on PCB v<version>` | PCB v1: channel 2 is not read. On a v1 board it always reads pressed. | — |
| INFO `channel 2 reads released — not used on PCB v<version>` | PCB v1: channel 2 is not read, and it reads released. | — |
| FAIL `the inputs read pressed but the robot did not latch ESTOP` | The control box reads the E-stop pressed, but the robot did not latch its ESTOP error within 1 s. | RTI reads the E-stop every tick: is RTI running (S0)? `logs/RTI.log` |
| FAIL `the E-stop still reads pressed after the release` | The E-stop was not seen released within 60 s of *Now release the E-stop*. The step ends without clearing the error. | the E-stop's two wires to the control box: E-Stop 1 is terminals E2 + E4 (E-Stop 2: E1 + E3, docs/pin_map.md)<br>the E-stop's contact type: the box expects a normally-CLOSED contact that OPENS when pressed<br>the E-stop button itself: a contact block not clipped on, or a broken contact |
| WARN `the ESTOP error did not clear after the release` | The check sent Clear Errors, but the ESTOP error was still latched 3 s later. | press Clear Errors in the dashboard; if it stays, an E-stop channel still reads pressed |
| PASS `pressed: read on <n> channel(s) and latched by the robot; released: clear` | The E-stop works. Given only when the step has no FAIL. | — |

### The box's buttons (`S2.buttons`)

Each line names the button, B1 or B2.

| Result | What it means | What to check |
|---|---|---|
| SKIP `button <B1/B2>: skipped by the user` | You skipped the press wait for this button. | — |
| FAIL `button <B1/B2>: no press seen in 30 s` | No press was seen within 30 s. | `<B1/B2>`'s two wires to the Pi's header (docs/pin_map.md)<br>is the supervisor running? It reads the buttons (`logs/supervisor.log`) |
| SKIP `button <B1/B2>: the press was seen; skipped by the user before its release` | A press was seen; you skipped the release wait. The check goes on with the next button. | — |
| PASS `button <B1/B2>: pressed and released` | — | — |
| FAIL `button <B1/B2>: stays pressed` | A press was seen, but no release within 30 s. | `<B1/B2>` is stuck or its wire is shorted to ground |

### Isolated inputs (`S2.inputs`)

| Result | What it means | What to check |
|---|---|---|
| SKIP `not tested (the user's choice)` | You answered **no** to *Test the isolated inputs?*. | — |
| SKIP `input <n>: skipped by the user (not wired)` | You skipped the switch wait for this input. | — |
| FAIL `input <n>: no change seen` | The input's level did not change within 45 s. | input `<n>`'s wiring and its supply (an isolated input needs its own signal voltage) |
| SKIP `input <n>: the change was seen; skipped by the user before switching back` | The level changed; you skipped the switch-back wait. The check goes on with the next input. | — |
| PASS `input <n>: switches both ways` | The level changed and came back. | — |
| WARN `input <n>: changed, did not go back` | The level changed, but was not back at its starting level within 45 s. | what drives input `<n>` still gives its signal (a switch that latches, a sensor still triggered), or the input's wiring holds it |

### Isolated outputs (`S2.outputs`)

| Result | What it means | What to check |
|---|---|---|
| SKIP `not tested (the user's choice)` | You answered **no** to *Test the isolated outputs?*. | — |
| SKIP `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | The check could not take control of the robot: another client held it for more than 15 s, or the robot refused for the reason given. No output was switched. | The line says it: wait, or release control in the dashboard, then run the stage again. |
| SKIP `output <n>: not wired (the user)` | You answered **not wired**. | — |
| PASS `output <n>: switched, seen by the user` | You answered **yes**. | — |
| FAIL `output <n>: the user saw nothing` | You answered **no**. | output `<n>`'s wiring and the supply of what it drives (an isolated output switches an external voltage) |

### The Hall sensor (`S2.hall`)

| Result | What it means | What to check |
|---|---|---|
| SKIP `this robot has no Hall-sensor joint` | No joint has `<has_hall_sensor>` 1 in the robot's file. The same line appears when the configuration did not load (*The configuration loads* failed). | A robot without a Hall sensor: nothing. Otherwise fix *The configuration loads* first. |
| SKIP `the Hall check needs IDLE (the robot is in <mode>)` | The robot is in another mode than IDLE. | Bring the robot to IDLE (the line names the mode it is in), then run the stage again. |
| SKIP `another client holds control (<reason>) — the dashboard keeps it ~5 s after its last command: wait, or release it there, then run this step again` | The check could not take control of the robot, as for the outputs. | The line says it: wait, or release control in the dashboard, then run the stage again. |
| SKIP `the robot refused the Hall check: <reason>` | The robot refused to start the Hall check and said why. The real-time loop's own reasons: a joint is free for hand turning or in a test move; the robot is not in IDLE, or a mode change is pending; the loop is still configuring the drives (the first ~1.2 s after it starts); the robot has no joint with `<has_hall_sensor>` 1. | Do what the reason says, then run the stage again. |
| FAIL `the robot did not start the Hall check` | The Hall check was accepted but had not started on the joint within 3 s. | `logs/RTI.log` |
| FAIL `the sensor never changed` | Within 120 s the sensor's level never changed. Expected: *it changes at the magnet and changes back after it*. | the sensor's cable to the drive (its connector on the drive)<br>the magnet: present, its gap to the sensor (a few mm), the right pole facing it<br>turn through the whole range once: the magnet may sit elsewhere |
| FAIL `the sensor changed once and stayed` | Within 120 s the level changed once and did not change back. Expected: *it changes at the magnet and changes back after it*. | the sensor stays triggered: the magnet too close, or the sensor's output shorted |
| PASS `the sensor changes at the magnet and back (<joint> at <angle> deg, <angle> deg)` | The sensor works. The angles are the joint's at the last change to level 0 and to level 1; `?` when none was recorded. | — |
| WARN `the repeat was not completed` | You chose the repeat, but six changes in all were not seen within 120 s. | — |
| WARN `the trigger angle was not recorded both times` | The angle of the change to level 0 is missing from one of the two passes. | — |
| PASS `triggered <difference> deg apart on the two passes` | The sensor triggered within 2.0° of the first pass. | — |
| WARN `triggered <difference> deg apart on the two passes` | The two passes were more than 2.0° apart. Expected: *within 2.0 deg*. | the magnet or the sensor is loose, or the gap is so large the sensor triggers late; homing relies on this point |

### Any step of this stage

| Result | What it means | What to check |
|---|---|---|
| SKIP `no connection to the robot (S0's 'Robot service' step)` | *The robot service runs* failed, so there is no connection to the robot. | Fix *The robot service runs* ([Step 1](step-1-control-box.md#the-robot-service-runs)). |
| SKIP `the arm stayed enabled (this step needs it disabled)` | The arm was ENABLED and was not disabled within 180 s. | Support or park the arm, press **Disable** in the dashboard, then run the stage again. |
| SKIP `skipped by the user` | You skipped a wait that skips the whole step: the wait for **Disable**, the wait for control, or any wait of the E-stop or Hall sensor step. (In the buttons and inputs steps a skip skips only that button or input: see their tables.) | — |
| SKIP `skipped by the user (Ctrl-C)` | You pressed Ctrl-C in the terminal while the step worked on its own rather than waiting for you, for example during the 2 s an output is on (the output goes back to its level first). The whole step is skipped and its results so far are not kept; the run goes on with the next step. | Run the stage again for this step's result. |
| SKIP `the run was stopped here` | You stopped the run at a question of this step (Ctrl-C in the terminal, **Stop the run** in the dashboard): *Test the isolated inputs?*, *Test the isolated outputs?*, an output's question, or the Hall sensor's repeat question. The run ends. This line and the step's results measured before the question — the outputs already answered, or the Hall sensor's first-pass PASS — are in the report. | — |
| FAIL `the check itself failed: <error type>: <message>` | The check's own code raised an error. The run goes on with the next step; the report's details hold the error's traceback. | this is a fault of the check, not necessarily of the robot — send the report |

## What's next

[Step 4: Joint test moves](step-4-joint-test.md)
