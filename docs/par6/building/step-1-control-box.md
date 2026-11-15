---
status: new
---

# Step 1: The Pi and the configuration

Stage 0 of [the first-run check](first-run-check.md) checks everything the robot needs before any drive gets power: that the Raspberry Pi is set up for the robot (real-time kernel, boot settings, Python packages, user groups, the robot service), that the robot and gripper configuration files load and pass the runtime's own validator, that the control box version in the configuration matches the board in your box, and that the robot service is running with its control loop ticking. Every later stage reads the drives through the robot service, and the control box version decides how the E-stop is read, so a mistake here shows up later as confusing failures. Nothing moves in this stage, the drives need no power, and no step waits for the arm to be enabled or disabled.

**Prerequisites**

- The Raspberry Pi is running, set up as the runtime's README describes ("Set up a new Pi"), and you are logged in to it or have the dashboard open.
- The robot service has been started (`autorun.service`). If it is not running, the last step fails and tells you how to start it.
- You can read the version printed on the control box's PCB (the silkscreen on the board). The check asks you to confirm it.
- The drives do not need power. The arm may be in any state, but see the note below about the setup check.

!!! note "Note"
    The setup check starts a Python process that imports all of the runtime's packages, which takes about 3 s of CPU time.

    The setup script itself says to run it with the arm DISABLED: starting another process slows the real-time loop's ticks on the Pi. Stage 0 does not check or wait for this.

    - Press **Disable** in the dashboard before you start stage 0 (support or park the arm first), or run stage 0 before the drives are powered.

## Procedure

**In the dashboard:** open the **First run** tab. All six stages are ticked by default: leave only **0 The Pi and the configuration** ticked, then press **Start**.

**From a terminal** on the robot's Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 0
```

In the result lines below, `<runtime>` stands for the runtime's folder on the Pi (`~/Desktop/RCB-Runtime` in the command above); the check prints the full path.

The steps run in this order:

1. **The Pi's setup** (`S0.setup`). Nothing to do. The check says *Checking the Pi's setup (scripts/setup_system.sh --check, a few seconds) ...* and runs the setup script in its check-only mode. It gives up after 180 s.
2. **The configuration loads** (`S0.config`). Nothing to do.
3. **The control box version** (`S0.pcb`). The check asks: *config/system.xml says the control box has PCB v`<version>` (its E-stop is read on `<n>` channel(s)). Is that the board in your box? The version is printed on the board.* The answers are **yes**, **no** and **not sure**:
    - **yes**: PASS.
    - **no**: FAIL. Your answer does not change the configuration: correct `<pcb_version>` yourself (see [Troubleshooting](#troubleshooting)).
    - **not sure**: WARN.

    In the dashboard each answer is a button. In the terminal type the number (`1`, `2`, `3`) or the answer's text. Ctrl-C at this question, or **Stop the run** in the dashboard, stops the whole run. When the configuration did not load in step 2, the question is not asked (INFO).
4. **The robot service runs** (`S0.service`). Nothing to do.
5. **Only when your run also includes later stages:** if stage 0 has a FAIL, the check asks *Stage 0 has a FAIL — fix it first (the hints say what to check). Go on to stage `<next stage>` anyway?* **yes** goes on, **no** ends the run. Ctrl-C (or **Stop the run**) at this question counts as no.
6. The run ends: the check writes its report and, with the support bundle set to *ask*, asks whether to add the support bundle (see [the first-run check](first-run-check.md#the-report-and-the-support-bundle)).

Stage 0 has no waits and shows no **Skip** button: the control box question is the only point where you answer anything. In the terminal, Ctrl-C while a step works on its own — for example while the setup script runs — skips that step (SKIP *skipped by the user (Ctrl-C)*); the run and its report go on.

## What each check looks at

### The Pi's setup

Step `S0.setup`. Runs `bash <runtime>/scripts/setup_system.sh --check` (report only, no sudo, at most 180 s) and reads its report: one line per item, `OK`, `MISSING` (followed by `->` lines that say how to fix it) or `NOTE`. The script checks these items:

| Item | What the script checks |
|---|---|
| kernel | a real-time kernel (`/sys/kernel/realtime` = 1) |
| boot | the CAN chip, SPI, UART and I2C in `/boot/firmware/config.txt`; no serial console in `cmdline.txt` |
| python | the runtime's `.venv` on Python 3.11 with the runtime's packages |
| groups | the user in the `dialout`, `i2c` and `gpio` groups (the UART, the OLED's I2C, the GPIO header) |
| sudo | the commands the runtime runs with sudo, password-free (`/etc/sudoers.d/10-rcb-runtime`), when the user cannot already run them |
| priority | `cap_sys_nice` on the `python3` binary (the real-time loop's scheduling priority; without it the loop refuses to start) |
| service | `autorun.service` and `autorun.sh` installed and enabled, with the memory-lock drop-in (`LimitMEMLOCK=infinity`) |
| logs | the system log limits (the journal 200 MB, syslog 50 MB, logrotate hourly) |

**Pass rule:** no `MISSING` line and the script's exit code 0. `NOTE` lines do not change the verdict; they are kept in the report's details with the script's output.

### The configuration loads

Step `S0.config`. Loads `config/system.xml`, the robot file it names (in `robots/`) and the active gripper's file (in `grippers/`) with the runtime's own loader, then runs the runtime's own validator over them. The validator checks, in this order: the joint count, the required per-joint values, the values that must be positive, the encoder bits, the hard joint limits, the soft joint limits against them, the loop timing, and the gripper.

**Pass rule:** the files load without an error, and the validator finds no `[ERROR]`-level problem. `[WARNING]`-level findings do not fail the step: they are kept in the report's details.

The later steps use what this step read: the robot and gripper names, the joint count, whether the gripper is on the CAN bus (from the gripper's file), the Hall-sensor joint (the first joint whose `<has_hall_sensor>` is 1) and the control box version.

### The control box version

Step `S0.pcb`. Reads `<control_box><pcb_version>` from `config/system.xml` and tells you how many E-stop channels that version reads:

| PCB version | E-stop channels read |
|---|---|
| v1 | 1 — channel 1 only. Channel 2 has a layout fault on this board and always reads pressed. |
| v2 | 2 — both channels are read and cross-checked: either channel pressed means pressed. |
| below 1 | treated as v1 |
| newer than v2 | treated as v2, with a warning in the log |

**Pass rule:** you answer **yes**. The check cannot read the version from the board: the board does not report it.

### The robot service runs

Step `S0.service`. Connects to the robot's command executor (by default on the same Pi, `127.0.0.1`; the terminal tool's `--host` option changes it) and reads the robot's health report: its "control loop" part says whether the real-time loop's tick still advances. Then it reads the robot's mode and state.

**Pass rule:** the connection succeeds, and the control loop is running (the health report has a control loop entry that is not STALE). A loop that is running but slow (its health level WARN or ERROR) still passes; its summary is part of the PASS line.

## Expected results

A correctly set-up Pi shows:

- PASS `The Pi's setup: the Pi's setup is complete (<n> checks OK)`
- PASS `The configuration loads: robot <robot> (<n> joints), gripper <gripper> (on CAN)` — for PAR6, `robot PAR6 (6 joints)`; `(on CAN)` appears only for a gripper on the CAN bus.
- PASS `The control box version: PCB v<version>, confirmed by the user`
- PASS `The robot service runs: connected; RTI running (<rate> Hz, p99 period <ms> ms, <n> overruns since start); mode <mode>, <state>`

## Troubleshooting

The Result column shows what the check prints after the step's title.

### The Pi's setup (`S0.setup`)

| Result | What it means | What to check |
|---|---|---|
| WARN `could not run the setup check: <error>` | The script could not be started, or it ran longer than 180 s. | run it by hand: `bash <runtime>/scripts/setup_system.sh --check` |
| FAIL `<n> item(s) missing in the Pi's setup` | The script reported `<n>` items as `MISSING`. | One line per missing item: `<item> — fix: <fix>; <fix>` (the script's own fix lines; the `— fix:` part only when the script gives one)<br>then: `sudo bash <runtime>/scripts/setup_system.sh` (applies what it can) and run this check again |
| WARN `the setup check exited with <code> but named nothing missing` | The script failed without a `MISSING` line. | read its output: `bash <runtime>/scripts/setup_system.sh --check` |
| PASS `the Pi's setup is complete (<n> checks OK)` | Every item is in place. | — |

### The configuration loads (`S0.config`)

| Result | What it means | What to check |
|---|---|---|
| FAIL `the configuration does not load: <error type>: <message>` | Reading the files failed; the message says where. The later steps that need the configuration cannot use it. | `<runtime>/config/system.xml: <robot> must name a file in robots/, <gripper> one in grippers/`<br>an XML syntax error: the message names the file and the line |
| FAIL `robot <robot> (<n> joints), gripper <gripper> — <n> problem(s) in the robot / gripper XML` | The files load, but the validator found at least one `[ERROR]`. `(on CAN)` follows the gripper's name for a CAN gripper. | Each problem the validator found, one per line, `[ERROR]` and `[WARNING]` alike. |
| PASS `robot <robot> (<n> joints), gripper <gripper>` | The files load and validate. `(on CAN)` follows the gripper's name for a CAN gripper. | — |

### The control box version (`S0.pcb`)

| Result | What it means | What to check |
|---|---|---|
| INFO `skipped: the configuration did not load` | The version comes from the configuration, which did not load: no question is asked. | Fix the result of *The configuration loads* first. |
| PASS `PCB v<version>, confirmed by the user` | You answered **yes**. | — |
| FAIL `system.xml declares PCB v<version>, the user says the board differs` | You answered **no**. | set `<control_box><pcb_version>` in `config/system.xml` to the board's version, then restart the robot service (`sudo systemctl restart autorun.service`): the E-stop is read according to it |
| WARN `system.xml declares PCB v<version>, not confirmed` | You answered **not sure**. | look for the version on the control box's PCB (silkscreen) before relying on the E-stop check; v1 boards read the E-stop on one channel only |
| SKIP `the run was stopped here` | You stopped the run at this question (Ctrl-C in the terminal, **Stop the run** in the dashboard). The run ends; this line is in the report. | — |

### The robot service runs (`S0.service`)

| Result | What it means | What to check |
|---|---|---|
| FAIL `no connection to the robot service: <error type>: <message>` | The check could not connect to the robot's command executor. Every later step that needs the robot is skipped with *no connection to the robot (S0's 'Robot service' step)*. | start it: `sudo systemctl start autorun.service`<br>its state: `systemctl status autorun.service`; the logs: `logs/supervisor.log`, `logs/high_level.log` (the executor), `logs/RTI.log`<br>the next stages need it: they read the drives through it |
| FAIL `the robot service answers but RTI's control loop is not running` | The executor answers, but the real-time loop's tick does not advance (or the health report has no control loop entry). | `logs/RTI.log` and `logs/RTI.out.log` say why it stopped (a configuration error is named there)<br>restart: `sudo systemctl restart autorun.service` |
| PASS `connected; RTI running (<loop summary>); mode <mode>, <state>` | Connected, and the loop runs. | — |

### Any step

| Result | What it means | What to check |
|---|---|---|
| SKIP `skipped by the user (Ctrl-C)` | You pressed Ctrl-C in the terminal while the step worked on its own, for example while the setup script ran. The run goes on with the next step. | Run the stage again for this step's result. |
| FAIL `the check itself failed: <error type>: <message>` | The check's own code raised an error. The run goes on with the next step; the report's details hold the error's traceback. | this is a fault of the check, not necessarily of the robot — send the report |

## What's next

[Step 2: Power and every drive on the bus](step-2-drives.md)
