---
status: new
---

# Step 2: Power and every drive on the bus

Stage 1 of [the first-run check](first-run-check.md) checks the power and the CAN bus: that every drive the robot's configuration declares (and a gripper on the CAN bus) answers on its CAN ID, that no other device answers where it should not, that the CAN bus stays free of errors while it is watched for 3 s, that the drives run firmware this runtime supports (the same version on every joint), that every drive gets the right supply voltage, that no drive is hot, and that no drive reports a fault of its own. Most wiring mistakes of a new build — a drive without power, a loose or swapped CAN connector, a drive set to the wrong ID, a missing terminating resistor, a power wire too thin — show up here, before anything moves. Nothing moves in this stage: every step only reads what the drives report through the robot service. The drives must be powered; the arm should be DISABLED.

**Prerequisites**

- [Step 1](step-1-control-box.md) passed: the configuration loads and the robot service runs.
- The drives are powered (the control box's power on), and they were powered **before the robot service started**. The robot service scans the CAN IDs and reads every drive's firmware version when it starts: a drive powered later still answers, but it is noted as having missed the start-up scan, and its firmware version may not have been read. If you powered the drives after the service, restart the service (`sudo systemctl restart autorun.service`) and run this stage again.
- The arm DISABLED (support or park it first, then press **Disable** in the dashboard). This stage's description asks for it, but its steps do not check it and do not wait for it: they only read.
- The E-stop released. A pressed E-stop shows up as the drives' `estop` fault flag in *Drive fault flags*.
- Nobody touches the CAN cables or the power while the stage runs: a drive powered up or down, or a cable moved, raises the CAN error counters.

## Procedure

**In the dashboard:** open the **First run** tab. All six stages are ticked by default: leave only **1 Power and CAN** ticked, then press **Start**.

**From a terminal** on the robot's Pi:

```bash
cd ~/Desktop/RCB-Runtime && .venv/bin/python3 tools/first_run.py --stages 1
```

Stage 1 asks you nothing and shows no **Skip** button: it runs by itself in a few seconds. In the terminal, Ctrl-C while a step runs skips that step (SKIP *skipped by the user (Ctrl-C)*); the run and its report go on. The steps run in this order:

1. **The configuration loads** and **The robot service runs** — two steps of [Step 1](step-1-control-box.md), run first because the steps of this stage need them. They run only when stage 0 is not part of the run, and their results are listed under stage 1. The Pi's setup and the control box question are not repeated.
2. **Every drive answers** (`S1.nodes`).
3. **The CAN bus is clean** (`S1.can_bus`). The check says *Watching the CAN bus for 3 s ...* and waits 3 s. The dashboard shows no **Skip** button for it; in the terminal, Ctrl-C during it skips this step.
4. **Firmware versions** (`S1.firmware`).
5. **Supply voltage** (`S1.voltage`).
6. **Drive temperatures** (`S1.temperature`).
7. **Drive fault flags** (`S1.faults`).
8. **Only when your run also includes later stages:** if stage 1 has a FAIL, the check asks *Stage 1 has a FAIL — fix it first (the hints say what to check). Go on to stage `<next stage>` anyway?* **yes** goes on, **no** ends the run. Ctrl-C (or **Stop the run**) at this question counts as no.
9. The run ends: the check writes its report and, with the support bundle set to *ask*, asks whether to add the support bundle (see [the first-run check](first-run-check.md#the-report-and-the-support-bundle)).

**Stop the run** in the dashboard takes effect at the next wait or question; stage 1 has none, so it runs to its end first.

## What each check looks at

Every step reads `get_hardware`, the robot's one-call report of every drive. Each drive is named by its joint, `J1` to `J6`, on CAN ID 0 to 5 (joint *n* on ID *n* − 1); a gripper on the CAN bus is named `gripper` and has the next ID (6 on PAR6). Firmware, voltage, temperature and fault flags are judged on one reading: the last one *Every drive answers* or *The CAN bus is clean* took.

### Every drive answers

Step `S1.nodes`. For each declared drive and a CAN gripper:

- **answering**: the robot has fresh data from it now (its old-data warning is off);
- **answered the scan**: it answered the scan of CAN IDs 0-15 that the robot service makes when it starts.

It also lists every ID above the robot's own (from the first unused ID up to 15) that answered the start-up scan. Two of them have a meaning: ID **14** is where a drive waiting in its bootloader answers (the bootloader's IDs read as 14), and ID **13** is reserved for the real-time loop's timing messages: no device should answer there.

**Pass rule:** every declared drive answers now. Each unused ID that answered adds one WARN, whatever the verdict on the drives.

### The CAN bus is clean

Step `S1.can_bus`. Reads the Pi's CAN interface state and error counters (the kernel's, as `ip -details -statistics link show` reports them), waits 3 s, and reads them again. The counters: `bus_off`, `restarts`, `error_passive`, `error_warning`, `bus_errors`, `arbitration_lost`. The interface's state is one of ERROR-ACTIVE (normal), ERROR-WARNING, ERROR-PASSIVE, BUS-OFF or STOPPED.

The rules, in this order:

1. **FAIL** when the state is ERROR-PASSIVE, BUS-OFF or STOPPED, or `bus_off`, `restarts` or `error_passive` rose during the 3 s.
2. **WARN** when the state is ERROR-WARNING, or `bus_errors` rose during the 3 s.
3. **WARN** when `bus_off`, `restarts` or `error_passive` is above 0 in the interface's totals (the check's line calls them "since RTI started"), though none rose during the 3 s.
4. **PASS** otherwise. Expected: *ERROR-ACTIVE, no new errors*.

A rise of `error_warning` or `arbitration_lost` alone does not change the verdict; when the step fails, the FAIL line names every counter that rose.

### Firmware versions

Step `S1.firmware`. Reads the firmware version of every answering joint drive (0 = not read yet) and of a CAN gripper that answers. Each version is checked against the range this runtime supports for the drive type the robot or gripper file declares: **103 or newer** for both drive types the runtime knows. A drive whose version has not been read, or whose file declares no drive type the runtime knows, is not judged against the range.

The rules, in this order:

1. **FAIL** when any drive (joints and gripper) runs a version outside the supported range.
2. **WARN** when the joints do not all run the same version. The gripper is not compared with the joints.
3. **WARN** when any joint's version was not read.
4. **PASS** otherwise. Expected: *the same version on every joint*.

### Supply voltage

Step `S1.voltage`. Reads the supply voltage every answering drive (joints and gripper) measures; a drive that reports 0 V (not read yet) is left out. The robot's supply is **24 V**.

The rules, in this order:

1. **FAIL** when any drive is more than 20 % off 24 V: below 19.2 V or above 28.8 V.
2. **WARN** when any drive is more than 10 % off 24 V: below 21.6 V or above 26.4 V.
3. **WARN** when the spread — the highest drive's voltage minus the lowest's — is more than 1.5 V.
4. **PASS** otherwise. Expected: *24 V +-10%, spread under 1.5 V*.

### Drive temperatures

Step `S1.temperature`. Reads the temperature (°C) of every answering drive (joints and gripper) and takes the median: the middle value of the sorted temperatures (with an even count, the upper of the two middle ones).

**Pass rule:** every drive below 60 °C, and none more than 15 °C above the median. Expected, as the check prints it: *under 60 C* with a PASS, *under 60 C, near the others* with a WARN.

### Drive fault flags

Step `S1.faults`. For every answering drive (joints and gripper) reads whether it is calibrated, its fault bit, and its eight fault flags:

| Flag | What the drive reports |
|---|---|
| `temperature` | over-temperature |
| `encoder` | an encoder error |
| `supply_voltage` | its supply voltage outside its range |
| `driver` | a motor driver stage error |
| `velocity` | over-speed |
| `current` | over-current |
| `estop` | its E-stop input active |
| `watchdog` | it stopped hearing from the Pi for 100 ms |

The rules, per drive:

- **WARN** when the drive reports it is not calibrated.
- **WARN** when `watchdog` is its only flag.
- **FAIL** when it has any other flag, or its fault bit is set with no flag read yet.

**PASS** (one line for the whole step) when no drive gives any of these. Expected: *no fault flags*.

## Expected results

A correctly wired robot shows, after the two steps of stage 0 when they run first:

- PASS `Every drive answers: all <n> drives answer` — `<n>` counts the joints and a CAN gripper: 7 on PAR6 with its gripper on the CAN bus.
- PASS `The CAN bus is clean: state ERROR-ACTIVE, no errors in 3 s nor since RTI started`
- PASS `Firmware versions: every joint on firmware <version>; gripper <version>` — the gripper part only with a CAN gripper that answers.
- PASS `Supply voltage: <lowest>-<highest> V on every drive (spread <spread> V)`
- PASS `Drive temperatures: <lowest>-<highest> C`
- PASS `Drive fault flags: no drive reports a fault`

For comparison, the PAR6 reference arm measured (2026-10-18): 23.0-23.8 V on its 24 V supply, a spread of about 0.7 V, firmware 103 on every drive, 36-42 °C.

## Troubleshooting

The Result column shows what the check prints after the step's title. A WARN or FAIL is followed by what was expected (when the step says) and the hints, most likely first.

### Every drive answers (`S1.nodes`)

| Result | What it means | What to check |
|---|---|---|
| FAIL `no drive answers` | Not one declared drive (nor the CAN gripper) answers. | the drives' power: the control box's power button / relay; is any drive's LED lit?<br>the cable from the Pi's CAN connector to the first drive<br>termination (120 ohm at each end of the bus: ~60 ohm between CAN-H and CAN-L with the power off)<br>every drive set to 1 Mbit/s |
| FAIL `not answering: <name> (ID <id>), <name> (ID <id>), ...` | These drives do not answer; the others do. | First, when they apply:<br>• other IDs answered at the start (`<ids>`): probably the missing drive set to a wrong ID — when unused IDs answered the start-up scan<br>• `<names>` answered when RTI started and stopped since: a loose connector, a power dip, or a drive that resets (its supply) — when a silent drive did answer the start-up scan<br>Then always:<br>• its power: is the drive's LED lit? Follow the power wires to it (with a daisy-chained supply, the connector before it)<br>• its CAN cable: both connectors fully seated; CAN-H and CAN-L not swapped at any connector<br>• its CAN ID: the drive must be set to the ID shown — a drive on a wrong ID shows up as 'a device answers on ID `<n>`'<br>• termination: one 120 ohm resistor at each END of the bus — with all power off, about 60 ohm between CAN-H and CAN-L at any connector (120 = one missing, ~40 = one too many)<br>Last, when more than one drive is silent:<br>• if every drive after one point of the cable chain is silent, the break is at that point |
| PASS `all <n> drives answer` | Every declared drive answers. | — |
| PASS `all <n> drives answer (<names> came after RTI's start-up scan: powered later?)` | Every drive answers now, but the named ones missed the robot service's start-up scan. | No hint. Their firmware may not have been read: see *Firmware versions*. |
| WARN `a drive is waiting in its bootloader (it answers on the bootloader's IDs)` | ID 14 answered the start-up scan. | an interrupted firmware update: flash it again — the dashboard's Firmware tab, 'Scan' finds it |
| WARN `a device answers on ID 13, which is reserved` | ID 13 answered the start-up scan. | ID 13 is reserved for RTI's timing messages: set that device to its own ID |
| WARN `a device answers on ID <id>, which this robot does not use` | Another unused ID (not 13 or 14) answered the start-up scan. One line per ID. | a drive set to the wrong ID — one of the missing ones?<br>set it to its joint's ID (J1 = 0 ... J6 = 5, a CAN gripper = 6) |

### The CAN bus is clean (`S1.can_bus`)

| Result | What it means | What to check |
|---|---|---|
| INFO `the CAN interface's counters cannot be read here (simulation, or not on the robot's Pi)` | The interface's counters could not be read, so the bus was not watched. | — |
| FAIL `the CAN bus is in trouble: state <state>, while watching +<n> <counter>, +<n> <counter>, ...` | The state is ERROR-PASSIVE, BUS-OFF or STOPPED, or `bus_off`, `restarts` or `error_passive` rose in the 3 s. The line lists every counter that rose. | termination: 120 ohm at each END of the bus (~60 ohm between CAN-H and CAN-L with the power off)<br>a connector with CAN-H / CAN-L swapped, or not fully seated<br>two drives set to the SAME ID (both answer at once and their replies collide)<br>every drive at 1 Mbit/s; the cable's length and its ground / shield |
| WARN `state <state>, +<n> bus errors in 3 s` | The state is ERROR-WARNING, or bus errors were counted in the 3 s. | the same four hints as the FAIL above |
| WARN `clean now, but since RTI started: <n> bus_off, <n> restarts, <n> error_passive` | No new errors in the 3 s, but these counters are above 0. Only the counters above 0 are listed. | a drive powered up or down, or a cable moved, while RTI ran — if the counters keep rising, check:<br>then the same four hints as the FAIL above |
| PASS `state <state>, no errors in 3 s nor since RTI started` | A clean bus. | — |

### Firmware versions (`S1.firmware`)

| Result | What it means | What to check |
|---|---|---|
| INFO `no drive answers (see 'Every drive answers')` | No joint drive answers, so no version could be read. | Fix *Every drive answers* first. |
| FAIL `firmware this runtime does not support: <name> <version> (<drive type>: <supported range>), ...` | These drives run firmware outside the supported range (103 or newer). | update the drives: the dashboard's Firmware tab, 'Update robot' (it flashes every drive with the release its driver type needs) |
| WARN `the joints run different firmware: J1 <version>, J2 <version>, ...` | Not every joint runs the same version. The line lists every answering joint (0 = not read). | update every drive to the same release: the dashboard's Firmware tab, 'Update robot' |
| WARN `firmware not read for <names>` | These joints answer, but the robot service has not read their version. | RTI reads the versions at start: restart the service once every drive is powered |
| PASS `every joint on firmware <version>; gripper <version>` | Every joint runs the same supported version. The gripper part appears only with a CAN gripper that answers. | — |

### Supply voltage (`S1.voltage`)

| Result | What it means | What to check |
|---|---|---|
| INFO `no supply voltage read yet (no drive answers, or RTI has not polled them)` | No answering drive reported a voltage above 0 V. | Fix *Every drive answers* first, or run the stage again a little later. |
| FAIL `supply voltage far off: <name> <volts> V, ...` | These drives are more than 20 % off 24 V (below 19.2 V or above 28.8 V). | the power supply's output (this robot expects 24 V)<br>the power wiring to the drives: wire size, screw terminals, connectors |
| WARN `supply voltage off: <name> <volts> V, ...` | These drives are more than 10 % off 24 V (below 21.6 V or above 26.4 V). | the power supply's output (this robot expects 24 V)<br>the power wiring to the drives: wire size, screw terminals, connectors |
| WARN `<name> gets <spread> V less than the best-supplied drive (<volts> V)` | Every drive is within 10 % of 24 V, but the lowest one is more than 1.5 V below the highest. The number in brackets is the low drive's own voltage. | the power path to `<name>`: a thin or long wire, a loose screw terminal, a worn connector on its branch of the supply |
| PASS `<lowest>-<highest> V on every drive (spread <spread> V)` | — | — |

### Drive temperatures (`S1.temperature`)

| Result | What it means | What to check |
|---|---|---|
| INFO `no temperature read (no drive answers)` | No drive answers. | Fix *Every drive answers* first. |
| WARN `warm: <name> <temp> C, ... (others ~<median> C)` | These drives are at 60 °C or more, or more than 15 °C above the median. | while nothing moves a drive should stay near the others: its heatsink and airflow; a motor held against a load (a joint resting on an endstop); a drive that is faulty |
| PASS `<lowest>-<highest> C` | — | — |

### Drive fault flags (`S1.faults`)

| Result | What it means | What to check |
|---|---|---|
| WARN `<name> reports it is not calibrated` | The drive's own motor / encoder calibration has not been done. | the drive's motor / encoder calibration has to be done once (the drive's configuration tool) before it can run the motor |
| WARN `<name> reports watchdog` | The watchdog flag is the drive's only flag. | the drive stopped hearing from the Pi for 100 ms: normal after a restart or a lost connection; Clear Errors — if it returns, that drive's CAN connection |
| FAIL `<name> reports <flag>, <flag>, ...` | The drive reports these flags (any flag set other than `watchdog` alone). | One hint per flag, in the order listed:<br>`temperature`: over-temperature: the drive's heatsink and airflow; a motor working against a load<br>`encoder`: the encoder: the magnet on the motor shaft (loose, missing, off-centre) or the encoder board's distance to it<br>`supply_voltage`: the supply voltage is outside the drive's range: the power supply and its wiring<br>`driver`: the motor driver stage: the motor's phase wires (loose or touching), the supply<br>`velocity`: over-speed: usually after a fall or a hand spin; clear the errors and watch whether it returns<br>`current`: over-current: a shorted motor phase, or a joint that is blocked<br>`estop`: the drive's E-stop input is active: the E-stop line to the drives, or the E-stop pressed<br>`watchdog`: the drive stopped hearing from the Pi for 100 ms: normal after a restart or a lost connection; Clear Errors — if it returns, that drive's CAN connection |
| FAIL `<name> reports a fault (its flags not read yet)` | The drive's fault bit is set, but none of its flags has been read. | Clear Errors and read again; `logs/RTI.log` names the fault |
| PASS `no drive reports a fault` | No drive gives any of the results above. | — |

A drive can give a *not calibrated* WARN and a flags line at the same time.

### Any step of this stage

| Result | What it means | What to check |
|---|---|---|
| SKIP `no connection to the robot (S0's 'Robot service' step)` | *The robot service runs* failed, so there is no connection to read the drives through. | Fix *The robot service runs* ([Step 1](step-1-control-box.md#the-robot-service-runs)). |
| SKIP `skipped by the user (Ctrl-C)` | You pressed Ctrl-C in the terminal while the step ran, for example during the 3 s CAN watch. The run goes on with the next step. | Run the stage again for this step's result. |
| FAIL `the check itself failed: <error type>: <message>` | The check's own code raised an error. The run goes on with the next step; the report's details hold the error's traceback. | this is a fault of the check, not necessarily of the robot — send the report |

## What's next

[Step 3: E-stop, buttons, I/O and the Hall sensor](step-3-io.md)
