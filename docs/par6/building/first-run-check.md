---
status: new
---

# The first-run check

The first-run check is a guided test of a robot you have just built: it goes through the robot stage by stage — the Raspberry Pi and the configuration files, every drive on the CAN bus, the E-stop and the inputs, a small test move of each joint, the first homing and the homed arm — and tells you after every step what it measured, whether that is right, and, when it is not, what to check first. Run it after building the robot, after a repair, or whenever something was rewired. The six [steps](#the-stages) that follow this page describe every check, every question it asks and every result it can give.

Stages 0 to 2 move nothing. Stage 3 moves each joint a few degrees, stage 4 homes the arm and stage 5 moves the homed arm.

!!! danger "Danger"
    In stages 3, 4 and 5 the arm moves by itself once you answer the question before each move: the test moves of stage 3 slowly and with limited force, the homing at its own speed to every joint's endstop, the homed arm's turns at 10 % speed.

    - Clear the space the arm can reach, and keep people out of it.
    - Keep a hand on the E-stop. Skip and Stop in the check end a step; they are not emergency stops.
    - Fix every FAIL of stages 0 to 2 before you let the arm move.

!!! note "Note"
    The dashboard's First run tab, stages 4 and 5 and the support bundle in the report come with runtime 1.2.0. Older runtimes have the command-line tool with stages 0 to 3.

## Two ways to run it

Both run the same program with the same checks, and both write the same report. The dashboard is the easier one; the terminal works over SSH without a browser.

### In the dashboard: the First run tab

1. Open the dashboard and the **First run** tab.
2. Tick the stages to run. All six are ticked; untick the ones you have done already.
3. Choose how stage 3 runs: powered test moves (the default) or **Stage 3 by hand** — each joint is freed in turn and you turn it yourself, with no motor current. See [Step 4](step-4-joint-test.md).
4. Choose **Support bundle at the end**: *ask at the end* (the default), *yes* or *no*. See [The report and the support bundle](#the-report-and-the-support-bundle).
5. Press **Start**.

While the check runs:

- A **question** appears in an orange box above the transcript, with one button per answer. When the check waits for something — you pressing the E-stop, the arm being enabled, a move finishing — the box shows what it waits for, how long it waits at most, and a **Skip** button. Skipping a wait skips what the check was waiting for: the step, or — in the steps that go joint by joint or item by item — that joint or item alone. A move in progress is stopped where it is; a homing too, and the arm is then not homed.
- When the check asks something while another tab is open, the dashboard shows a notification.
- The **transcript** lists each stage, what the check tells you, every question with the answer given, and every result with its verdict. A WARN or FAIL is followed by what was expected and what to check. Grey lines are the check's own output: if the check itself fails, the reason is there.
- **Stop the run** ends the run early: the wait in progress is skipped (its move stopped), so is any wait before the next question, and the run ends at that question. The report keeps everything done so far.
- Only one run can be in progress, whichever page started it. Every open dashboard page shows that run and can answer it; a reloaded page finds it again.
- If the dashboard itself stops or restarts during a run, the check ends the same way as with **Stop the run**: the move in progress is stopped and the report is written.

When the run has ended, the result line shows the overall verdict and the count of each verdict, with download buttons for `report.txt`, `report.json` and the support bundle. **Earlier reports** lists the newest ten reports with their verdicts and downloads.

The Enable and Disable buttons are in the dashboard's top bar. The check asks you to press one of them when a stage needs it; it never presses them itself.

### From a terminal

On the robot's Raspberry Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py
```

| Option | Default | What it does |
|---|---|---|
| `--stages LIST` | `0,1,2,3,4,5` | The stages to run, as a comma list, for example `--stages 3` or `--stages 1,2`. Without stage 0, its configuration and robot-service checks still run first: the later stages need them. |
| `--by-hand` | off | Stage 3 by hand instead of the powered test moves. |
| `--bundle ask\|yes\|no` | `ask` | Add the support bundle to the report: ask at the end, always, or never. |
| `--list` | — | List every step with its stage and what it does, then exit. |
| `--host ADDRESS` | `127.0.0.1` | The robot's command executor. The default is the Pi the tool runs on; stages 0 and 5 read files on that Pi, so run the tool there. |
| `--ui console\|json` | `console` | `json` is how the dashboard's First run tab talks to the check, not for typing. |

Answering in the terminal:

- A yes / no question takes `y`, `yes`, `n` or `no`. A question with several answers lists them as `[1] … [2] …`: type the number or the answer's text.
- **Ctrl-C while the check waits** skips what it waits for, as the dashboard's Skip does; a move in progress is stopped where it is (a homing too: the arm is then not homed).
- **Ctrl-C while a step works on its own** — the Pi's setup check, the CAN-bus watch, a move the robot finishes by itself — skips that step; such a move finishes.
- **Ctrl-C at a question** stops the run. The report keeps everything done so far.

The tool exits with `0` when nothing failed, `1` when a step failed, and `2` when the run was stopped early.

## The stages

| Stage | Page | The arm | What it checks | Moves |
|---|---|---|---|---|
| 0 | [Step 1: The Pi and the configuration](step-1-control-box.md) | not needed | the Pi's setup, the robot and gripper files, the control box version, the robot service | nothing |
| 1 | [Step 2: Power and every drive on the bus](step-2-drives.md) | powered, DISABLED | every drive answers, the CAN bus, firmware, supply voltage, temperatures, the drives' fault flags | nothing |
| 2 | [Step 3: E-stop, buttons, I/O and the Hall sensor](step-3-io.md) | powered, DISABLED | the E-stop, the box's buttons, the isolated inputs and outputs, the Hall sensor | you turn one joint by hand |
| 3 | [Step 4: Joint test moves](step-4-joint-test.md) | ENABLED, homed or not | each joint moves, the right way, freely | each joint a few degrees and back |
| 4 | [Step 5: The first homing](step-5-homing.md) | ENABLED | the homing; a failure is explained | every joint to its endstop |
| 5 | [Step 6: The homed arm](step-6-homed-arm.md) | ENABLED, homed | how far each joint turns, its friction, a quiet hold, the gripper, a stop part-way | each joint a visible amount and back |

Run the stages in order the first time: each one relies on what the earlier ones checked.

## The results

Every step gives one or more results:

| Verdict | Meaning |
|---|---|
| **PASS** | Measured and right. |
| **WARN** | It works, but something is off: read the hints before you rely on it. |
| **FAIL** | Wrong. Fix it before you go on: the hints say what to check, most likely first. |
| **SKIP** | Not checked, and the line says why: you skipped it, a step before it failed, the arm was in the wrong state, or the robot refused the step. |
| **INFO** | Information, not a verdict. |

The run's overall result is FAIL when any step failed, else WARN when any step warned, else PASS.

When a stage ends with a FAIL, the check asks *Stage N has a FAIL — fix it first (the hints say what to check). Go on to stage M anyway?* before the next stage. Answer no, fix the cause, and run that stage again.

## What the check asks of you

- **The arm's state.** Stage 2 needs the arm DISABLED; the powered test moves of stage 3, and stages 4 and 5, need it ENABLED. When the arm is in the other state, the check tells you which button to press in the dashboard and waits up to 180 s; after that it skips the step. It never enables or disables the arm itself. Stage 1 only reads the drives and works in either state; the arm is normally still disabled there. Stage 3 by hand works in either state too, and tells you before each joint what the other joints do meanwhile.
- **Control of the robot.** The steps that switch outputs, run the Hall-sensor check or move the arm take control of the robot. The dashboard holds control for 5 s after your last click there, for example on Enable: the check waits up to 15 s for it to let go, then skips the step and says so.
- **Your eyes.** Several checks cannot measure everything themselves: which way a joint moved, how far it turned, whether a lamp on an output came on. Answer what you saw. If you answered wrong by mistake, the questions about outputs offer *again*; elsewhere, run that stage again.

## The report and the support bundle

Every run writes a report into its own folder on the Pi, named by the time the run started (UTC): `temp_data/first_run/<YYYYMMDD_HHMMSS>/`.

| File | What it holds |
|---|---|
| `report.txt` | The readable report: the robot, gripper, control box and code version, the overall result, then every result by stage — a WARN or FAIL with what was expected and what to check. |
| `report.json` | The same for programs: the run's details (time, whether it completed, the Pi's name, the code version, the robot, gripper, joint count, control box version and the last hardware reading of every drive), the overall verdict, the counts, and every result with its value, expected value, hints and details. |
| `support_<YYYYMMDD_HHMMSS>.zip` | The support bundle, when you asked for one. |

The newest 50 report folders are kept; older ones are deleted when a new report is written.

The **support bundle** is one zip with everything a helper needs: this report (in `first_run/`), every log file of the robot (`logs/`), the incident recordings (`incidents/`), the configuration files (`config/`, `config/cells/`, `robots/`, `grippers/`) and an `info.txt` with the time, the code version, the version of every part, the robot's state, latched errors, free disk space and the Pi's uptime. The dashboard's Logs tab makes the same zip without the report.

- Building the bundle reads about 60 MB, which can slow the robot's real-time loop while the arm is powered. When the arm is ENABLED at the end of the run, the check asks you to support the arm (or park it) and press **Disable**, and waits up to 180 s. If the arm stays enabled, no bundle is made; the Logs tab can make one later.
- With less than 200 MB free on the Pi's SD card no bundle is made.
- A bundle is tens of MB: only the newest three reports keep theirs.

Asking for help? Send the support bundle, or at least the report folder. See [Getting help](../09-troubleshooting/support.md).

## What's next

Start with [Step 1: The Pi and the configuration](step-1-control-box.md).
